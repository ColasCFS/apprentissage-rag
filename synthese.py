# synthese.py
# Rôle : transformer les 45 verdicts en tableau de décision.
# Entrée : verdicts_comparaison.json. Sortie : affichage dans le terminal.
# Aucun appel au modèle : on peut relancer ce script autant qu'on veut.

import json

CONFIGS = ["A_workflow", "B_reformulation", "C_agent"]

with open("verdicts_comparaison.json", encoding="utf-8") as f:
    verdicts = json.load(f)

# --- Bloc 1 : tableau par configuration ---
# "Correctes" = juste + refus_correct, la même définition que pour le 13/15 de l'essai 5.
print(f"{'Config':<17} {'Correctes':>9} {'Juste':>5} {'Part.':>5} {'Fausse':>6} "
      f"{'Ref.tort':>8} {'Ref.ok':>6} {'Limite':>6} {'Appels':>6} {'Tok.entrée':>10} {'Tok.sortie':>10}")

for config in CONFIGS:
    lignes = [v for v in verdicts if v["config"] == config]

    # Compte des verdicts : .get(cle, 0) évite un KeyError si une étiquette n'apparaît jamais
    compte = {}
    for v in lignes:
        compte[v["verdict"]] = compte.get(v["verdict"], 0) + 1

    correctes = compte.get("juste", 0) + compte.get("refus_correct", 0)
    limites = sum(1 for v in lignes if v["sortie_limite"])

    # Consommation totale sur les 15 questions (les réponses en erreur n'ont pas de tokens)
    avec_tokens = [v["tokens"] for v in lignes if v["tokens"] is not None]
    appels = sum(t["appels"] for t in avec_tokens)
    tok_entree = sum(t["entree"] for t in avec_tokens)
    tok_sortie = sum(t["sortie"] for t in avec_tokens)

    print(f"{config:<17} {correctes:>6}/{len(lignes):<2} {compte.get('juste', 0):>5} "
          f"{compte.get('partielle', 0):>5} {compte.get('fausse', 0):>6} "
          f"{compte.get('refus_a_tort', 0):>8} {compte.get('refus_correct', 0):>6} "
          f"{limites:>6} {appels:>6} {tok_entree:>10} {tok_sortie:>10}")

# --- Bloc 2 : les questions où les configurations ne sont pas d'accord ---
# Ce sont les seules qui expliquent un écart de score : c'est là qu'on regarde en premier.
verdict_par_id = {}
for v in verdicts:
    verdict_par_id.setdefault(v["id"], {})[v["config"]] = v["verdict"]

print("\nQuestions où les verdicts diffèrent :")
for id_q, par_config in verdict_par_id.items():
    if len(set(par_config.values())) > 1:
        detail = ", ".join(f"{c[0]} = {par_config.get(c)}" for c in CONFIGS)
        print(f"  {id_q} : {detail}")