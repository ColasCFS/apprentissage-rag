# juge_assurance.py
# Rôle : 1) noter les 20 réponses du RAG assurance avec le juge du 13 oct. (evaluer() de juge.py, prompt inchangé) ;
#        2) mesurer l'accord du juge avec tes verdicts sur l'échantillon de notation_assurance.csv.
# Entrée : eval_assurance.json, reponses_assurance.json, notation_assurance.csv (tes 10 verdicts à l'aveugle).
# Sortie : verdicts_juge_assurance.json + le taux d'accord et la liste des désaccords.
# Ce qui peut casser en silence : une étiquette mal orthographiée dans ton CSV (« Juste », « refus à tort »)
# compterait comme un désaccord — d'où la normalisation du bloc 2.

import csv
import json
import time
from juge import evaluer, ETIQUETTES

PAUSE = 1.5   # secondes entre deux appels, contre les 429

# --- Bloc 1 : chargement, réponses retrouvées par id ---
with open("eval_assurance.json", encoding="utf-8") as f:
    questions = json.load(f)
with open("reponses_assurance.json", encoding="utf-8") as f:
    reponses = {r["id"]: r for r in json.load(f)}

# --- Bloc 2 : tes verdicts, ramenés aux cinq étiquettes exactes du juge ---
# « Juste » → « juste », « refus à tort » → « refus_a_tort »
def normaliser(verdict):
    v = verdict.strip().lower().replace("à", "a").replace(" ", "_")
    return v if v in ETIQUETTES else f"inconnu({verdict})"

with open("notation_assurance.csv", encoding="utf-8-sig") as f:
    verdicts_colas = {ligne["id"]: normaliser(ligne["verdict_colas"])
                      for ligne in csv.DictReader(f, delimiter=";")}

# --- Bloc 3 : le juge note les 20 réponses ---
# Le prompt du juge n'est pas modifié : on mesure d'abord s'il tient sur ce nouveau domaine.
resultats = []
for q in questions:
    verdict, justification = evaluer(q["question"], q["reponse_attendue"], reponses[q["id"]]["reponse"])
    resultats.append({"id": q["id"], "type": q["type"], "verdict": verdict, "justification": justification})
    print(f"{q['id']} {verdict}")
    time.sleep(PAUSE)

with open("verdicts_juge_assurance.json", "w", encoding="utf-8") as f:
    json.dump(resultats, f, ensure_ascii=False, indent=2)

# --- Bloc 4 : accord sur ton échantillon, puis désaccords à trancher ---
juge = {r["id"]: r for r in resultats}
accords = [i for i in verdicts_colas if verdicts_colas[i] == juge[i]["verdict"]]
print(f"\nAccord juge / Colas : {len(accords)}/{len(verdicts_colas)}")
for i, v in verdicts_colas.items():
    if v != juge[i]["verdict"]:
        print(f"  {i} : toi = {v}, juge = {juge[i]['verdict']} — {juge[i]['justification']}")

# --- Bloc 5 : répartition des verdicts du juge sur les 20 (à ne lire qu'après l'accord) ---
print("\nRépartition sur les 20 :", {e: sum(r["verdict"] == e for r in resultats) for e in ETIQUETTES + ["invalide"]})
