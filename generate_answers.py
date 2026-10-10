import json
from retrieve import load_index
from ask import answer

with open("eval.json", "r", encoding="utf-8") as f:
    questions = json.load(f)
chunks, vectors = load_index()
resultats =[]

for k in [4,8]:
    for question in questions:
        print(k, question["id"])
        reponse, sources = answer(question["question"], chunks, vectors, k=k)
        resultats.append({"id":question["id"], "question":question["question"], "k":k, "reponse":reponse, "sources":sources, "reponse_attendue":question["reponse_attendue"]})

with open("reponses.json", "w", encoding="utf-8") as f:
    json.dump(resultats, f, indent=2, ensure_ascii=False)