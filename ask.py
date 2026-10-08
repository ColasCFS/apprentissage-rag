
import sys
import os
from embed_utils import embed
from embed_utils import cosinus
from retrieve import load_index
from retrieve import retrieve
from dotenv import load_dotenv
from mistralai.client import Mistral

load_dotenv()
api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)
model="mistral-small-latest"

SYSTEM = SYSTEM = """Tu es un assistant qui répond à des questions sur la location de logements.
Réponds uniquement à partir des extraits fournis, sans ajouter de connaissances extérieures.
Si les extraits contiennent des éléments de réponse, même formulés différemment de la question, utilise-les pour répondre.
Réponds "Je ne trouve pas cette information dans les documents." seulement si aucun extrait ne traite du sujet de la question.
Cite la source de chaque affirmation entre crochets, ex. [bail.txt]."""

if __name__=="__main__":
    if len(sys.argv)<2:
        print("Usage : python ask.py \"votre question\"")
        raise SystemExit(1)

    question = sys.argv[1]
    chunks, vectors = load_index()
    resultats = retrieve(question, chunks, vectors)

    for score, chunk in resultats:
        print(f"{score:.3f}  [{chunk['source']}], [{chunk['texte']}]")

    morceaux = []
    for score, chunk in resultats:
        morceaux.append(f'[{chunk["source"]}]\n{chunk["texte"]}')

    contexte = "\n\n".join(morceaux)
    user_msg=f"Extraits: \n{contexte}\n\nQuestion: {question}"

    response = client.chat.complete(
    model=model,      
    messages=[
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user_msg},
    ],
    )
    print(response.choices[0].message.content)

    