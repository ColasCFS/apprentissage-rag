import sys
import numpy as np
from dotenv import load_dotenv
from mistralai.client import Mistral
from pathlib import Path
import os

load_dotenv()

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-embed"

client = Mistral(api_key=api_key)

if len(sys.argv)<2:
    print("Nombre d'élément de la liste insuffisant, veuillez entrer un nom sous la forme 'python recherche.py taper votre question ici'")
    raise SystemExit(1)

question = (sys.argv[1])

def cosinus(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def embed(textes):
    response = client.embeddings.create(model=model, inputs=textes)
    return [d.embedding for d in response.data]

def search(question, docs, docs_vecs, k=3):
    q_vec = embed([question])[0]
    paires = []
    for i in range(len(docs)):
        paires.append([float(cosinus(q_vec, docs_vecs[i])), docs[i]])
    sorted_paires = sorted(paires, key=lambda x: x[0], reverse=True)
    return sorted_paires[:k]

textes =[
"Explorer un monde ouvert permet souvent de découvrir des histoires et des environnements très différents."
, "Les choix du joueur peuvent modifier profondément le déroulement d'une aventure narrative."
, "Affronter des adversaires humains demande généralement de réagir rapidement aux décisions prises en face. (Call of duty, starcraft 2)"
, "Les productions indépendantes se distinguent parfois par des mécaniques originales et une direction artistique audacieuse."
, "Une ambiance sonore réussie peut renforcer la tension ressentie lors d'une partie. (RDR2)"
, "Anticiper les mouvements ennemis est essentiel lorsqu'une victoire dépend de plusieurs décisions successives."
, "Certains titres développent la mémoire, les réflexes et la capacité à résoudre rapidement des problèmes."
, "Dans certains jeux, il faut gérer ses ressources avec prudence afin de maximiser ses chances de réussite. (Age of empire)"
, "Répartir son capital entre plusieurs catégories d'actifs permet de limiter l'exposition à un seul marché."
, "La durée pendant laquelle on peut immobiliser son argent influence les choix que l'on peut raisonnablement envisager."
, "Une entreprise solide peut voir son cours progresser ou chuter en fonction des résultats publiés et des anticipations du marché."
, "Les coûts prélevés par un intermédiaire peuvent réduire sensiblement le résultat obtenu après plusieurs années."
, "Les fluctuations quotidiennes ne devraient pas nécessairement conduire à modifier constamment une stratégie à long terme."
, "Comparer différents supports permet de mieux comprendre leur fonctionnement, leurs contraintes et leur potentiel."
, "La constitution progressive d'un patrimoine repose souvent sur une discipline régulière plutôt que sur la recherche d'un gain immédiat."
, "Des systèmes informatiques peuvent désormais repérer des tendances difficiles à identifier manuellement dans d'immenses ensembles d'informations."
, "Certains outils sont capables de produire une illustration à partir de quelques lignes décrivant une scène."
, "Des assistants numériques peuvent reformuler un document, résumer une réunion ou proposer plusieurs solutions à un problème."
, "La qualité d'une réponse dépend notamment de la précision avec laquelle le besoin est formulé."
, "Comme dans un jeu de stratégie, un système autonome peut évaluer plusieurs scénarios avant de sélectionner l'action qui semble la plus avantageuse."]



if Path("vecteurs.npy").exists():
    docs_vecs = np.load("vecteurs.npy")
    print("Vecteurs chargés depuis le fichier vecteurs.npy")

else:
    docs_vecs = embed(textes)
    np.save("vecteurs.npy", docs_vecs)
    print("Vecteurs calculés et sauvegardés dans le fichier vecteurs.npy")

if len(docs_vecs) != len(textes):
    print("Erreur : le nombre de vecteurs ne correspond pas au nombre de textes.")
    raise SystemExit(1)

result = search(question, textes, docs_vecs=docs_vecs, k=3)
print(f'Résultat de la recherche pour la question : "{question}"')
for score, doc in result:
        print(f'(score : {score:.2f})  - {doc} ')




