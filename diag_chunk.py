# --- Diagnostic des chunks avant embeddings ---
# Objectif : vérifier trois hypothèses sans appel à l'API
import json
from collections import Counter

with open("chunks_assurance.json", encoding="utf-8") as f:
    chunks = json.load(f)

# 1. Répartition des tailles : combien de très petits chunks ?
tailles = [len(c["texte"]) for c in chunks]
print(f"Moins de 100 caractères : {sum(t < 100 for t in tailles)}")
print(f"100 à 500 : {sum(100 <= t <= 500 for t in tailles)}")
print(f"Plus de 500 : {sum(t > 500 for t in tailles)}")

# 2. Tableaux longs : combien dépassent 1 500 caractères ?
print(f"Tableaux de plus de 1 500 caractères : "
      f"{sum(c['texte'].startswith('|') and len(c['texte']) > 1500 for c in chunks)}")

# 3. Titres : combien de titres différents, et lesquels reviennent le plus ?
titres = Counter((c["assureur"], c["titre"]) for c in chunks)
print(f"\nTitres différents : {len(titres)}")
for (assureur, titre), n in titres.most_common(8):
    print(f"  {n:4d}  {assureur} | {titre[:60]}")