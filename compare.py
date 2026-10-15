# compare.py
# Rôle : produire, pour chaque question d'eval.json, trois réponses dans les mêmes conditions
#   A_workflow      : chercher avec la question brute, puis générer
#   B_reformulation : reformuler la question, chercher avec la requête, générer sur la question d'origine
#   C_agent         : le modèle décide lui-même quoi chercher et combien de fois (max 3 tours)
# Entrée : eval.json + l'index (chunks.json, vectors.npy). Sortie : reponses_comparaison.json
# Ce qui peut casser en silence : un index qui n'est pas celui de l'essai 5 (d'où le contrôle
# du nombre de chunks), ou une erreur 429 sur une seule réponse (d'où l'enregistrement de l'erreur).

# --- Bloc 1 : imports et réglages ---
# client et MODELE sont repris d'agent.py : un seul client, un seul modèle pour les trois configurations.
import json
import time
from retrieve import load_index, retrieve
from reformulation import reformuler
from agent import repondre_agent, client, MODELE
from prompts import INTRO, REGLES_REPONSE

K = 8                  # même k pour les trois configurations (celui de l'essai 5)
LIMITE = None           # nombre de questions traitées ; 2 pour tester, None pour les 15
PAUSE = 1.5            # secondes entre deux configurations, pour limiter les erreurs 429
FICHIER_SORTIE = "reponses_comparaison.json"

SYSTEM_WORKFLOW = INTRO + " " + REGLES_REPONSE

# --- Bloc 2 : la génération commune à A et B (renvoie aussi sa consommation) ---
def generer(question, extraits):
    morceaux = [f"[{chunk['source']}]\n{chunk['texte']}" for score, chunk in extraits]
    contexte = "\n\n".join(morceaux)
    user_msg = f"Extraits :\n{contexte}\n\nQuestion : {question}"

    response = client.chat.complete(
        model=MODELE,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_WORKFLOW},
            {"role": "user", "content": user_msg},
        ],
    )
    tokens = {
        "entree": response.usage.prompt_tokens,
        "sortie": response.usage.completion_tokens,
        "appels": 1,
    }
    return response.choices[0].message.content, tokens

# Additionne deux consommations (utile pour B : reformulation + génération)
def additionner(t1, t2):
    return {cle: t1[cle] + t2[cle] for cle in t1}

# --- Bloc 3 : les trois configurations ---
# Format commun à toutes : (réponse, requêtes de recherche, consommation)
def config_a(question, chunks, vectors):
    extraits = retrieve(question, chunks, vectors, k=K)
    texte, tokens = generer(question, extraits)
    return texte, [question], tokens

def config_b(question, chunks, vectors):
    requete, tokens_reformulation = reformuler(question)
    extraits = retrieve(requete, chunks, vectors, k=K)
    texte, tokens_generation = generer(question, extraits)
    return texte, [requete], additionner(tokens_reformulation, tokens_generation)

def config_c(question, chunks, vectors):
    return repondre_agent(question, chunks, vectors, k=K)

CONFIGS = {
    "A_workflow": config_a,
    "B_reformulation": config_b,
    "C_agent": config_c,
}

# --- Bloc 4 : la boucle de comparaison ---
if __name__ == "__main__":
    chunks, vectors = load_index()
    print(f"Nombre de chunks dans l'index : {len(chunks)} (attendu : 195)")

    with open("eval.json", encoding="utf-8") as f:
        questions = json.load(f)
    if LIMITE is not None:
        questions = questions[:LIMITE]

    resultats = []
    for q in questions:
        for nom, fonction in CONFIGS.items():
            try:
                reponse, requetes, tokens = fonction(q["question"], chunks, vectors)
                erreur = None
            except Exception as e:
                reponse, requetes, tokens, erreur = None, [], None, str(e)

            resultats.append({
                "id": q["id"],
                "config": nom,
                "reponse": reponse,
                "requetes": requetes,
                "nb_recherches": len(requetes),
                "tokens": tokens,
                "erreur": erreur,
            })
            statut = f"ERREUR : {erreur}" if erreur else f"ok — {tokens}"
            print(f"{q['id']} {nom} : {len(requetes)} recherche(s) — {statut}")
            time.sleep(PAUSE)
            
    # --- Bloc 5 : sauvegarde ---
    with open(FICHIER_SORTIE, "w", encoding="utf-8") as f:
        json.dump(resultats, f, ensure_ascii=False, indent=2)
    print(f"{len(resultats)} réponses enregistrées dans {FICHIER_SORTIE}")