# juge.py — version importable (15 oct.)
# Rôle : noter une réponse générée en la comparant à la réponse attendue.
# Entrée : question, réponse attendue, réponse générée. Sortie : (verdict, justification).
# Ce qui peut casser en silence : toute modification de SYS_JUGE ou du modèle invalide
# l'étalonnage (accord 15/15 du 13 oct.) — ne pas y toucher sans refaire la mesure d'accord.

import json
import os
from dotenv import load_dotenv
from mistralai.client import Mistral

# --- Bloc 1 : client et modèle du juge (inchangés) ---
load_dotenv()
api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)
model = "mistral-small-latest"

# --- Bloc 2 : constantes du juge (inchangées, c'est ce prompt qui a été étalonné) ---
MSG_ABSENT = "L’information n’est pas dans le corpus."

SYS_JUGE = """Tu es un juge qui compare une réponse générée par un LLM à une réponse attendue. \
Tu reçois une question, une réponse attendue et une réponse générée par un LLM. \
Pour chaque triplet, tu émets un verdict parmi ces cinq étiquettes, écrites exactement ainsi : \
juste, partielle, fausse, refus_a_tort, refus_correct. \
Tu juges sur le fond, pas sur la forme. Si des cas particuliers existent, ils ne sont pas exigés. \
Des informations supplémentaires correctes ne font pas baisser la note. \
juste : tous les éléments clés de la réponse attendue sont présents, explicitement. \
partielle : la réponse va dans le bon sens, mais au moins un élément clé manque ou n'est qu'implicite. \
fausse : la réponse affirme quelque chose de contraire à la réponse attendue, ou donne une réponse alors que la réponse attendue dit que l'information est absente du corpus. \
refus_a_tort : le modèle dit ne pas trouver, alors que la réponse attendue contient l'information. \
refus_correct : le modèle dit ne pas trouver, et la réponse attendue indique que l'information n'est pas dans le corpus. \
Réponds uniquement par un objet JSON {"verdict": ..., "justification": ...}, avec une étiquette de la liste et une seule phrase de justification. Rien avant ni après le JSON."""

ETIQUETTES = ["juste", "partielle", "fausse", "refus_a_tort", "refus_correct"]

# --- Bloc 3 : l'appel au juge (inchangé) ---
def juger(question, reponse_attendue, reponse):
    user_msg = f"Question : {question}\n\nRéponse attendue : {reponse_attendue}\n\nRéponse générée : {reponse}"
    response = client.chat.complete(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": SYS_JUGE},
            {"role": "user", "content": user_msg},
        ],
    )
    return response.choices[0].message.content

# --- Bloc 4 : evaluer(), nouvelle ---
# Regroupe ce que faisait ta boucle : remplacer une réponse attendue None,
# appeler le juge, lire son JSON, contrôler l'étiquette.
# Elle renvoie deux valeurs, pour que n'importe quel script puisse l'utiliser.
def evaluer(question, reponse_attendue, reponse):
    if reponse_attendue is None:
        reponse_attendue = MSG_ABSENT

    texte_brut = juger(question, reponse_attendue, reponse)

    try:
        evaluation = json.loads(texte_brut)
        verdict = evaluation.get("verdict")
        justification = evaluation.get("justification")
        if verdict not in ETIQUETTES:
            verdict = "invalide"
    except json.JSONDecodeError:
        verdict = "invalide"
        justification = f"Le LLM n'a pas renvoyé un JSON valide : {texte_brut}"

    return verdict, justification

# --- Bloc 5 : l'ancien usage (essai 1), protégé ---
# Ne s'exécute que si on lance "python juge.py", jamais lors d'un import.
# Sortie renommée en _test pour ne pas écraser le fichier du 13 oct.
if __name__ == "__main__":
    K = 8
    with open("eval.json", "r", encoding="utf-8") as f:
        questions = json.load(f)
    with open("reponses_essai1.json", "r", encoding="utf-8") as f:
        reponses = json.load(f)

    # Réponse générée de l'essai 1 à k = K, retrouvée par id
    reponse_par_id = {}
    for r in reponses:
        if r["k"] == K:
            reponse_par_id[r["id"]] = r["reponse"]

    resultats = []
    for q in questions:
        verdict, justification = evaluer(q["question"], q["reponse_attendue"], reponse_par_id.get(q["id"]))
        resultats.append({"id": q["id"], "verdict": verdict, "justification": justification})
        print(q["id"], verdict)

    with open(f"verdicts_juge_k{K}_test.json", "w", encoding="utf-8") as f:
        json.dump(resultats, f, ensure_ascii=False, indent=2)