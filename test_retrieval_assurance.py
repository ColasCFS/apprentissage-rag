# --- Imports, client, chargement de l'index ---
import json
import os
import numpy as np
from dotenv import load_dotenv
from mistralai.client import Mistral

load_dotenv()
client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

with open("chunks_assurance.json", encoding="utf-8") as f:
    chunks = json.load(f)
vecteurs = np.load("vectors_assurance.npy")

K = 4

# Les trois questions dont la réponse est connue (page 21 MAIF, scannée)
QUESTIONS = {
    "P11": "J'ai environ 90 000 € de bijoux. Quelle franchise la MAIF applique en cas de vol ?",
    "P12": "La MAIF m'a remboursé un cambriolage l'an dernier. Si ça recommence au même endroit, je paie plus ?",
    "P13": "La MAIF m'a remboursé un vol il y a six mois. On vient de me voler des affaires dans ma cave, "
           "dont j'avais fait renforcer la porte pour 400 €. Ma franchise est-elle triplée ?",
}


# --- Recherche : similarité cosinus entre la question et tous les chunks ---
# Même calcul qu'au module 5 ; la question n'a pas de préfixe assureur, c'est voulu :
# un client ne formule pas sa question comme un chunk
def rechercher(question, k=K):
    q = np.array(client.embeddings.create(model="mistral-embed", inputs=[question]).data[0].embedding)
    scores = vecteurs @ q / (np.linalg.norm(vecteurs, axis=1) * np.linalg.norm(q))
    meilleurs = np.argsort(-scores)[:k]
    return [(chunks[i], scores[i]) for i in meilleurs]


# --- Affichage : pour chaque extrait, d'où il vient et son début ---
if __name__ == "__main__":
    for qid, question in QUESTIONS.items():
        print(f"\n=== {qid} : {question[:70]}…")
        for rang, (c, s) in enumerate(rechercher(question), start=1):
            print(f"{rang}. {s:.3f} | {c['assureur']} p.{c['page_pdf']} ({c['origine']}) | "
                  f"{c['texte'][:110].replace(chr(10), ' ')}")