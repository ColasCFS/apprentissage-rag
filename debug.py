import json
import sys
from retrieve import load_index
from retrieve import retrieve

with open("eval.json", "r", encoding="utf-8") as f:
        questions = json.load(f)

if len(sys.argv)<2:
    print("Nombre d'élément de la liste insuffisant, veuillez entrer un nom sous la forme 'python recherche.py taper l'ID question ici'")
    raise SystemExit(1)

question_ID = (sys.argv[1])
chunks, vectors =load_index()
texte_question=None
for question in questions:
       if question["id"]==question_ID:
                texte_question= question["question"]
                sources_attendues=question["sources_attendues"]

if texte_question is None:
       print("Identifiant introuvable dans eval.json")
       raise SystemExit(1)

retrieve_Q=retrieve(texte_question, chunks, vectors, k=(len(chunks)))
i=0
print(texte_question)
print(sources_attendues)
for chunk in retrieve_Q:
        i+=1 
        if chunk[1]["source"] in sources_attendues:
                print(f'Rang : {i}, score {chunk[0]}, source : {chunk[1]["source"]}, attendue : {sources_attendues}, debut du texte : {chunk[1]["texte"]}')
                        