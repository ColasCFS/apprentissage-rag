# --- Imports et client ---
import json
import os
import time
import numpy as np
from dotenv import load_dotenv
from mistralai.client import Mistral

load_dotenv()
client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

TAILLE_LOT = 64


# --- Encodage d'un lot, avec nouvelles tentatives sur 429 ---
# Même logique que pour l'OCR : on ne réessaie que la limite de débit
def encoder_lot(textes):
    for tentative in range(1, 4):
        try:
            reponse = client.embeddings.create(model="mistral-embed", inputs=textes)
            return [d.embedding for d in reponse.data]
        except Exception as e:
            if "429" not in str(e) or tentative == 3:
                raise
            print(f"429, tentative {tentative}/3, pause de 60 s")
            time.sleep(60)


# --- Programme principal ---
if __name__ == "__main__":
    with open("chunks_assurance.json", encoding="utf-8") as f:
        chunks = json.load(f)
    textes = [c["texte_vectorise"] for c in chunks]

    # Lots successifs : textes[0:64], textes[64:128], …
    vecteurs = []
    for debut in range(0, len(textes), TAILLE_LOT):
        lot = textes[debut:debut + TAILLE_LOT]
        vecteurs.extend(encoder_lot(lot))
        print(f"{len(vecteurs)}/{len(textes)}")
        time.sleep(1)

    # Contrôle d'alignement : un vecteur par chunk, dans le même ordre
    assert len(vecteurs) == len(chunks), "nombre de vecteurs différent du nombre de chunks"
    np.save("vectors_assurance.npy", np.array(vecteurs))
    print(f"Sauvegardé : {len(vecteurs)} vecteurs de dimension {len(vecteurs[0])}")