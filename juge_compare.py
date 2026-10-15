# juge_compare.py
# Rôle : faire noter les 45 réponses de compare.py par le juge étalonné.
# Entrée : eval.json + reponses_comparaison.json. Sortie : verdicts_comparaison.json
# Ce qui peut casser en silence : une réponse "limite atteinte" notée au hasard par le juge,
# d'où la règle fixée AVANT de voir les scores (bloc 3).

import json
import time
from juge import evaluer   # le juge du 13 oct., inchangé (test de non-régression passé)

MSG_LIMITE = "Limite de recherches atteinte sans réponse finale."
PAUSE = 1.0

# --- Bloc 1 : lecture des fichiers ---
with open("eval.json", encoding="utf-8") as f:
    questions = json.load(f)
with open("reponses_comparaison.json", encoding="utf-8") as f:
    reponses = json.load(f)

# --- Bloc 2 : retrouver chaque question par son id ---
# Un dict id → question, pour retrouver la réponse attendue de chaque réponse générée.
question_par_id = {q["id"]: q for q in questions}

# --- Bloc 3 : notation ---
verdicts = []
for r in reponses:
    q = question_par_id[r["id"]]
    sortie_limite = r["reponse"] == MSG_LIMITE

    if r["erreur"] is not None:
        # Réponse jamais générée : on ne la fait pas noter
        verdict, justification = "erreur", r["erreur"]
    elif sortie_limite and q["reponse_attendue"] is None:
        # Règle décidée avant les scores : sur une question hors corpus, la sortie par limite
        # compte comme un refus correct (rien d'inventé). Elle reste signalée par sortie_limite.
        verdict = "refus_correct"
        justification = "Règle fixée avant les scores : sortie par limite sur une question hors corpus."
    else:
        verdict, justification = evaluer(q["question"], q["reponse_attendue"], r["reponse"])
        time.sleep(PAUSE)

    verdicts.append({
        "id": r["id"],
        "config": r["config"],
        "verdict": verdict,
        "justification": justification,
        "sortie_limite": sortie_limite,
        "nb_recherches": r["nb_recherches"],
        "tokens": r["tokens"],
    })
    print(f"{r['id']} {r['config']} : {verdict}")

# --- Bloc 4 : sauvegarde ---
with open("verdicts_comparaison.json", "w", encoding="utf-8") as f:
    json.dump(verdicts, f, ensure_ascii=False, indent=2)
print(f"{len(verdicts)} verdicts enregistrés dans verdicts_comparaison.json")