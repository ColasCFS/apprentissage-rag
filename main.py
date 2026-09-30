from pathlib import Path
from module3_exo1 import charger_documents, chunk_text
import sys

size=10
overlap=3

if len(sys.argv)<2:
    print("Nombre d''élément de la list de sys.argv insuffisant, veuillez entrer un nom sous la forme ''python main.py dossier/")
    raise SystemExit(1)

documents=charger_documents(sys.argv[1])

tous_les_chunks = []
longueur_tous_chunks = 0
nombre_documents_analysés = len(documents)
for document in documents:
    if document.get("texte") =="":
        print (f'{document["source"]} est vide et est ignoré')
        nombre_documents_analysés = nombre_documents_analysés -1 
        continue 
    
    a=chunk_text (document["texte"],size=size,overlap=overlap)
    tous_les_chunks.extend (a)

longueur_tous_chunks = sum([len(m) for m in tous_les_chunks])

if len(tous_les_chunks) == 0:
    print("Aucun chunk n'a été créé - fin de programme")
    raise SystemExit (1)
    
moyenne_chunk = longueur_tous_chunks/(len(tous_les_chunks))           

print (len(tous_les_chunks))
print (type(tous_les_chunks[0]))


print (moyenne_chunk)

print(nombre_documents_analysés)
