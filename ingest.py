
import json

from module3_exo1 import charger_documents
from module3_exo1 import chunk_text
from embed_utils import embed
from pathlib import Path
import numpy as np

#Taille du chunk
size=500
#taille de l'overlap
overlap=50

dossier = "corpus_location"

if __name__ == "__main__":
    try:
            documents = charger_documents(dossier)
    except FileNotFoundError as e:
            print(e)
            raise SystemExit(1)
    if  documents == []:
        print(f'Aucun document n\'a été trouvé dans le dossier {dossier}')
        raise SystemExit(1)


    print(f"Nombre de documents chargés : {len(documents)}")
   

    chunks=[]
    for doc in documents:
        titre = doc["texte"].split("\n")[0].strip()
        liste_de_chunks = chunk_text(doc["texte"], size=size, overlap=overlap)
        for chunk in liste_de_chunks:
            chunks.append({"source": doc["source"], "texte": chunk,"titre":titre})



    docs_vecs = embed([chunk["titre"] + ". " + chunk["texte"] for chunk in chunks])
    np.save("vectors.npy", docs_vecs)

    with open("chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f'Nombre de vecteurs : {len(docs_vecs)}, longueur de chaque vecteur : {len(docs_vecs[0])}')
