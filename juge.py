import json
import os
from dotenv import load_dotenv
from mistralai.client import Mistral

K=8
load_dotenv()
api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)
model="mistral-small-latest"

with open("eval.json", "r", encoding="utf-8") as f:
    questions = json.load(f)
with open("reponses_essai1.json", "r", encoding="utf-8") as f:
    reponses = json.load(f)

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

fusion_dict = {}
for q in questions:
    attendue = q["reponse_attendue"]
    if attendue is None:
        attendue = MSG_ABSENT

    fusion_dict[q["id"]] = {
        "id": q["id"],
        "question": q["question"],
        "reponse_attendue": attendue,
        "reponse": None
    }

for r in reponses:
    if r["k"] != K:
        continue
    if r["id"] in fusion_dict:
        fusion_dict[r["id"]]["reponse"] = r["reponse"]

triplets_complets = list(fusion_dict.values())


resultats_evaluation = []

for item in triplets_complets:
    
    texte_brut_llm = juger(
        item["question"], item["reponse_attendue"], item["reponse"]
    )

    try:
        evaluation_json = json.loads(texte_brut_llm)
        item["verdict"] = evaluation_json.get("verdict")
        if item["verdict"] not in ETIQUETTES:
            item["verdict"]="invalide"
        item["justification"] = evaluation_json.get("justification")

    except json.JSONDecodeError:
        print(f"Erreur de décodage JSON pour l'id {item['id']}: {texte_brut_llm}")
        item["verdict"] = "invalide"
        item["justification"] = "Le LLM n'a pas renvoyé un JSON valide."

    resultats_evaluation.append(item)

with open(f"verdicts_juge_k{K}.json", "w", encoding="utf-8") as f:
    json.dump(resultats_evaluation, f, ensure_ascii=False, indent=2)


for item in resultats_evaluation:
    print(item["id"], item["verdict"])


        