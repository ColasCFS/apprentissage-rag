import json
import numpy as np
from embed_utils import embed, cosinus




with open("chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)
vectors = np.load("vectors.npy")



if len(chunks) != len(vectors):
    print("Erreur : le nombre de chunks ne correspond pas au nombre de vecteurs.")
    raise SystemExit(1)

revect_10=embed(chunks[10]["texte"])[0]

if len(revect_10) != len(vectors[10]):
    print("Erreur : la longueur du vecteur recalculé ne correspond pas à la longueur du vecteur original.")
    raise SystemExit(1)

print (cosinus(revect_10, vectors[10]))
print (cosinus(revect_10, vectors[11]))