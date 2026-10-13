import json

# Charger les verdicts du juge déjà sauvegardés (pas de nouvel appel au modèle)
with open("verdicts_juge.json", "r", encoding="utf-8") as f:
    resultats = json.load(f)

# Ta référence humaine, figée
VERDICTS_COLAS = {
    "Q01": "juste", "Q02": "refus_a_tort", "Q03": "partielle", "Q04": "juste",
    "Q05": "refus_a_tort", "Q06": "refus_correct", "Q07": "refus_correct",
    "Q08": "juste", "Q09": "juste", "Q10": "juste", "Q11": "juste",
    "Q12": "juste", "Q13": "juste", "Q14": "juste", "Q15": "refus_correct",
}

accords = 0          # nombre de questions où le juge est d'accord avec toi
desaccords = []      # les id à relire

for item in resultats:
    verdict_humain = VERDICTS_COLAS[item["id"]]   # ton verdict pour CETTE question
    if item["verdict"] == verdict_humain:
        accords += 1
    else:
        desaccords.append(item["id"])

# Après la boucle : le bilan sur les 15
print(f"Accord : {accords}/{len(resultats)} ({accords / len(resultats):.0%})")
print("Désaccords :", desaccords)