# reformulation.py
# Rôle : transformer la question brute d'un utilisateur en requête de recherche
# avec le vocabulaire des fiches location.
# Entrée : une question (str). Sortie : une requête (str).
# Ce qui peut casser en silence : le modèle répond à la question au lieu de la
# reformuler, ou ajoute un détail absent de la question (cf. Q20 de ta fiche).

# --- Bloc 1 : imports et client ---
# Même chargement de clé que dans ask.py : la clé vient du .env, jamais du code.
# Si ask.py importe Mistral autrement (version 3.0.0 du SDK), recopie ses lignes d'import ici.
import os
import json
from dotenv import load_dotenv
from mistralai.client import Mistral

load_dotenv()
client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

# --- Bloc 2 : la consigne de reformulation (version 2, figée après ce test) ---
# Changement par rapport à la v1 : règle 3, qui interdit de changer l'intention.
# Le test sur Q02 a montré que le modèle transformait l'action demandée
# ("y retourner") en une autre procédure ("résilier le bail").
# Règle générale volontairement : elle ne mentionne ni visite ni Q02,
# pour ne pas régler la reformulation sur une seule question du jeu de test.
SYSTEM_REFORMULATION = """Tu reformules des questions d'utilisateurs en requêtes de recherche
pour une base de fiches pratiques sur la location de logement en France.
Règles :
1. Ne réponds pas à la question.
2. Remplace les mots courants par leurs équivalents juridiques (bail, bailleur, locataire, préavis, etc.).
3. Conserve exactement l'intention et l'action demandées. N'introduis aucune procédure,
   démarche ou situation que la question ne mentionne pas.
4. N'ajoute aucune information absente de la question. Si elle est ambiguë, garde l'ambiguïté.
5. Renvoie uniquement la requête, sur une seule ligne, sans introduction ni guillemets."""

# --- Bloc 3 : la fonction (renvoie maintenant aussi sa consommation) ---
# response.usage donne les tokens lus (prompt_tokens) et écrits (completion_tokens) par le modèle.
# On les renvoie dans un petit dict, avec le nombre d'appels, pour que compare.py puisse additionner.
def reformuler(question: str):
    response = client.chat.complete(
        model="mistral-small-latest",
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_REFORMULATION},
            {"role": "user", "content": question},
        ],
    )
    requete = response.choices[0].message.content.strip()
    tokens = {
        "entree": response.usage.prompt_tokens,
        "sortie": response.usage.completion_tokens,
        "appels": 1,
    }
    return requete, tokens

# --- Bloc 4 : test sur Q02 (adapté aux deux valeurs renvoyées) ---
if __name__ == "__main__":
    with open("eval.json", encoding="utf-8") as f:
        questions = json.load(f)

    for q in questions:
        if q["id"] == "Q02":
            requete, tokens = reformuler(q["question"])
            print("Question brute     :", q["question"])
            print("Requête reformulée :", requete)
            print("Tokens             :", tokens)