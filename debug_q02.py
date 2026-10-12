import json
from retrieve import load_index
from retrieve import retrieve

with open("eval.json", "r", encoding="utf-8") as f:
        questions = json.load(f)

Q02_question= questions[1]["question"]
Q02_sources_attendues=questions[1]["sources_attendues"]

chunks, vectors =load_index()

retrieve_Q02=retrieve(Q02_question, chunks, vectors, k=(len(chunks)))

i=0

print(Q02_question)
print(Q02_sources_attendues)
for chunk in retrieve_Q02:
        i+=1 
        if chunk[1]["source"] in Q02_sources_attendues:
                print(f'Rang : {i}, score {chunk[0]}, source : {chunk[1]["source"]}, attendue : {Q02_sources_attendues}, debut du texte : {chunk[1]["texte"]}')
           