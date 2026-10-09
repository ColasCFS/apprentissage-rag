import json
from retrieve import load_index, retrieve

with open("eval.json", "r", encoding="utf-8") as f:
        questions = json.load(f)

chunks, vectors = load_index()
nb__non_trouves = 0
nb_evaluees = 0

for question in questions:
    if not question["sources_attendues"]:
        continue
    nb_evaluees += 1
    resultat=retrieve(question["question"], chunks, vectors, k=4)
    sources = [chunk["source"] for score, chunk in resultat]

    rang = None
    position =1
    for source in sources:
         
        if source in question["sources_attendues"]:
              rang=position
              break 
        position+=1
    if rang == None:
        nb__non_trouves+=1
             
    print(f"{question['id']}, rang: {rang} | attendu : {question['sources_attendues']} | récupéré : {sources}")
print(f"Hit rate : {nb_evaluees-nb__non_trouves}/{nb_evaluees}")