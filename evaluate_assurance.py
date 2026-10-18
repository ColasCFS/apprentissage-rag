# evaluate_assurance.py
# Rôle : mesurer la recherche (retrieval) du RAG assurance, sans aucun appel à l'API.
# Entrée : eval_assurance.json (sources attendues) + reponses_assurance.json (extraits récupérés et leur rang).
# Sortie : un tableau par question, puis trois indicateurs globaux.
# Ce qui peut casser en silence : une page attendue notée en page imprimée au lieu de page_pdf
# (le scan AXA p.7 est la page 9 du PDF) ferait compter un échec qui n'en est pas un.

import json

K = 8   # doit être le K utilisé dans generate_assurance.py

# --- Bloc 1 : chargement, réponses retrouvées par id ---
with open("eval_assurance.json", encoding="utf-8") as f:
    questions = json.load(f)
with open("reponses_assurance.json", encoding="utf-8") as f:
    reponses = {r["id"]: r for r in json.load(f)}

# --- Bloc 2 : indicateurs par question ---
# hit       : au moins une page attendue figure dans les K extraits
# rang      : rang de la première page attendue trouvée (K + 1 si aucune, la pénalité du module 7)
# couverture: part des pages attendues retrouvées — utile pour les questions à plusieurs sources
# assureurs : pour les comparatives, les assureurs attendus absents des extraits
lignes = []
for q in questions:
    attendues = {(s["assureur"], s["page_pdf"]) for s in q["sources_attendues"]}
    if not attendues:          # hors corpus : rien à retrouver, la recherche ne se mesure pas
        continue
    extraits = reponses[q["id"]]["extraits"]
    rangs = [e["rang"] for e in extraits if (e["assureur"], e["page_pdf"]) in attendues]
    trouvees = {(e["assureur"], e["page_pdf"]) for e in extraits} & attendues
    assureurs_absents = {a for a, p in attendues} - {e["assureur"] for e in extraits}
    lignes.append({
        "id": q["id"], "type": q["type"],
        "hit": bool(rangs),
        "rang": min(rangs) if rangs else K + 1,
        "couverture": len(trouvees) / len(attendues),
        "assureurs_absents": sorted(assureurs_absents),
    })

# --- Bloc 3 : affichage ---
for l in lignes:
    absents = f" | assureurs absents : {', '.join(l['assureurs_absents'])}" if l["assureurs_absents"] else ""
    print(f"{l['id']} {l['type']:<28} hit={'oui' if l['hit'] else 'NON'}  rang={l['rang']}  "
          f"couverture={l['couverture']:.0%}{absents}")

n = len(lignes)
print(f"\nHit rate à k={K} : {sum(l['hit'] for l in lignes)}/{n}")
print(f"Rang moyen (pénalité {K + 1}) : {sum(l['rang'] for l in lignes) / n:.2f}")
print(f"Couverture moyenne des pages attendues : {sum(l['couverture'] for l in lignes) / n:.0%}")
