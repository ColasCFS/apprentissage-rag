import numpy as np
from dotenv import load_dotenv
from mistralai.client import Mistral
import os

load_dotenv()

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-embed"

client = Mistral(api_key=api_key)

question = "Comment mettre fin à ma location ?"
noteA = "Le locataire peut résilier le bail avec un préavis d'un mois."
noteB = "La tour Eiffel mesure environ 330 mètres."
noteC = "Le dépôt de garantie est restitué sous deux mois."
notes =[noteA, noteB, noteC]
paires=[]

def cosinus(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def embed(textes):
    response = client.embeddings.create(model=model, inputs=textes)
    return [d.embedding for d in response.data]

def search(question, docs, docs_vecs, k):
    q_vec = embed([question])[0]
    paires = []
    for i in range(len(docs)):
        paires.append([float(cosinus(q_vec, docs_vecs[i])), docs[i]])
    sorted_paires = sorted(paires, key=lambda x: x[0], reverse=True)
    return sorted_paires[:k]

result = search(question, notes, docs_vecs=embed(notes), k=2)
print(f'Résultat de la recherche pour la question : "{question}"')
for score, doc in result:
    print(f'  - {doc} (score : {score:.2f})')