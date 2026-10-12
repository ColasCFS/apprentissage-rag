
import json

from doc_utils import charger_documents
from doc_utils import chunk_text
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
    compteur_paragraphes_over_500=0
    for doc in documents:
        titre = doc["texte"].split("\n")[0].strip()
        lignes = doc["texte"].splitlines()
        if lignes[1].startswith("Source"):
             del lignes[1]
        texte_propre = "\n".join(lignes)

        paragraphes = texte_propre.split("\n\n")
        for paragraphe in paragraphes:
            if paragraphe.strip() == titre or paragraphe.strip() == "":
                continue
            if len(paragraphe)<=500:
             chunks.append({"source": doc["source"], "texte": paragraphe,"titre":titre})
            else:
             compteur_paragraphes_over_500+=1
             chunk_paragraphes= chunk_text(paragraphe,size=size,overlap=overlap)
             for chunk_paragraphe in chunk_paragraphes:
                 chunks.append({"source": doc["source"], "texte": chunk_paragraphe,"titre":titre})

    docs_vecs = embed([chunk["titre"] + ". " + chunk["texte"] for chunk in chunks])
    np.save("vectors.npy", docs_vecs)

    with open("chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f'Nombre de vecteurs : {len(docs_vecs)}, longueur de chaque vecteur : {len(docs_vecs[0])}')
    print(compteur_paragraphes_over_500)
    
