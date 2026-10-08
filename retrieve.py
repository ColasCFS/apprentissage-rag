import numpy as np
import sys
import json
from embed_utils import embed
from embed_utils import cosinus

def load_index():
    with open("chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)
    vectors = np.load("vectors.npy")
    if len(chunks) != len(vectors):
        print("Erreur : le nombre de chunks ne correspond pas au nombre de vecteurs.")
        raise SystemExit(1)
    return chunks, vectors


def retrieve(question, chunks, vectors, k=4):
    q_vec = embed([question])[0]
    paires = []
    for i in range(len(chunks)):
        paires.append([float(cosinus(q_vec, vectors[i])), chunks[i]])
    sorted_paires = sorted(paires, key=lambda x: x[0], reverse=True)
    return sorted_paires[:k]

if __name__=="__main__":
    if len(sys.argv)<2:
        print("Usage : python retrieve.py \"votre question\"")
        raise SystemExit(1)

    question = sys.argv[1]

    chunks, vectors = load_index()
    resultats = retrieve(question, chunks, vectors)
