# generate_assurance.py
# Rôle : générer la réponse du RAG assurance pour chacune des 20 questions d'eval_assurance.json.
# Entrée : eval_assurance.json + l'index assurance (chunks_assurance.json, vectors_assurance.npy).
# Sortie : reponses_assurance.json (réponse, extraits récupérés avec leur rang, tokens, erreur éventuelle).
# Ce qui peut casser en silence :
#   - un index qui ne correspond pas aux chunks (d'où le contrôle du nombre au démarrage) ;
#   - une erreur 429 sur une seule question (d'où les nouvelles tentatives et le champ "erreur") ;
#   - l'alias mistral-small-latest peut changer de version entre deux lancements (limite à noter).

# --- Bloc 1 : imports et réglages ---
# rechercher() est reprise de test_retrieval_assurance.py : même calcul de similarité,
# même index, chargé une seule fois. On ne réécrit pas la recherche une deuxième fois.
import json
import time
from test_retrieval_assurance import rechercher, chunks, vecteurs, client
from prompts import INTRO_ASSURANCE, REGLES_ASSURANCE_V4

MODELE = "mistral-small-latest"   # même modèle que le projet location, pour comparer
K = 8                             # ton choix : de la place pour plusieurs lignes de tableau
LIMITE = None                       # 2 pour tester ; None pour les 20 questions
PAUSE = 1.5                       # secondes entre deux questions, contre les 429
FICHIER_SORTIE = "reponses_assurance.json"

SYSTEM = INTRO_ASSURANCE + " " + REGLES_ASSURANCE_V4


# --- Bloc 2 : mise en forme d'un extrait pour le modèle ---
# Chaque extrait porte son en-tête : assureur, référence, édition, page, titre de section.
# C'est ce qui permet au modèle de citer [MAIF p.21] et de repérer l'édition 2009 d'AXA.
# page_pdf (position dans le PDF) et non page_imprimee : c'est la page des sources attendues.
def formater(chunk):
    entete = (f"[{chunk['assureur']} p.{chunk['page_pdf']}] "
              f"CG {chunk['assureur']} réf. {chunk['reference']}, édition {chunk['date_version']}"
              f" — section : {chunk['titre']}")
    return f"{entete}\n{chunk['texte']}"


# --- Bloc 3 : un appel au modèle, avec nouvelles tentatives sur 429 ---
# Même logique qu'embed_assurance.py : on ne réessaie que la limite de débit.
def appeler_modele(user_msg):
    for tentative in range(1, 4):
        try:
            return client.chat.complete(
                model=MODELE,
                temperature=0,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": user_msg},
                ],
            )
        except Exception as e:
            if "429" not in str(e) or tentative == 3:
                raise
            print(f"429, tentative {tentative}/3, pause de 60 s")
            time.sleep(60)


# --- Bloc 4 : répondre à une question (recherche puis génération) ---
# Renvoie aussi les extraits récupérés, avec leur rang : ils serviront au hit rate
# et au rang moyen sans refaire la recherche.
def repondre(question):
    resultats = rechercher(question, k=K)
    contexte = "\n\n".join(formater(c) for c, score in resultats)
    user_msg = f"Extraits :\n{contexte}\n\nQuestion : {question}"

    response = appeler_modele(user_msg)
    extraits = [
        {"rang": rang, "assureur": c["assureur"], "page_pdf": c["page_pdf"],
         "origine": c["origine"], "score": round(float(score), 4)}
        for rang, (c, score) in enumerate(resultats, start=1)
    ]
    tokens = {"entree": response.usage.prompt_tokens, "sortie": response.usage.completion_tokens}
    return response.choices[0].message.content, extraits, tokens


# --- Bloc 5 : boucle sur les questions, puis sauvegarde ---
if __name__ == "__main__":
    print(f"Chunks : {len(chunks)}, vecteurs : {len(vecteurs)} (attendu : 2195 et 2195)")
    assert len(chunks) == len(vecteurs), "index désaligné : relancer embed_assurance.py"

    with open("eval_assurance.json", encoding="utf-8") as f:
        questions = json.load(f)
    if LIMITE is not None:
        questions = questions[:LIMITE]

    sorties = []
    for q in questions:
        try:
            reponse, extraits, tokens = repondre(q["question"])
            erreur = None
        except Exception as e:
            reponse, extraits, tokens, erreur = None, [], None, str(e)

        sorties.append({
            "id": q["id"], "type": q["type"], "question": q["question"],
            "reponse": reponse, "extraits": extraits, "tokens": tokens, "erreur": erreur,
        })
        statut = f"ERREUR : {erreur}" if erreur else f"ok — {tokens}"
        print(f"{q['id']} : {statut}")
        time.sleep(PAUSE)

    with open(FICHIER_SORTIE, "w", encoding="utf-8") as f:
        json.dump(sorties, f, ensure_ascii=False, indent=2)
    print(f"{len(sorties)} réponses enregistrées dans {FICHIER_SORTIE}")
