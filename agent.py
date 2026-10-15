OUTIL_RETRIEVE = {
    "type": "function",
    "function": {
        "name": "retrieve",
        "description": (
            "Recherche dans une base de 30 fiches pratiques sur la location de logement "
            "en France (bail, préavis, loyer, dépôt de garantie, état des lieux, "
            "travaux, impayés, droit de visite...). "
            "À utiliser pour toute question sur les droits et obligations d'un "
            "locataire ou d'un propriétaire. "
            "Renvoie les extraits de fiches les plus proches de la requête, avec leur source. "
            "Si les premiers extraits ne suffisent pas, tu peux relancer une recherche "
            "avec une autre formulation."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "requete": {
                    "type": "string",
                    "description": (
                        "Phrase de recherche en français, reformulée avec les termes "
                        "du droit de la location. Ex. : 'préavis de départ logement meublé'."
                    )
                }
            },
            "required": ["requete"]
        }
    }
}

import json
import os
from retrieve import load_index, retrieve
from dotenv import load_dotenv
from mistralai.client import Mistral

# 1. Client Mistral :
load_dotenv()
api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)
MODELE = "mistral-small-latest"


# 2. Consigne système, version 3 (15 oct.) : règles de réponse communes (prompts.py)
#    + ce qui est propre à l'agent : utiliser l'outil, une recherche par sujet, relancer si besoin.

from prompts import INTRO, REGLES_REPONSE

SYSTEM = (
    INTRO + " "
    "Pour répondre, utilise l'outil retrieve. "
    "Avant de répondre, vérifie si la question touche plusieurs sujets (ex. une procédure ET un délai, "
    "une règle ET ses conséquences) : si oui, fais une recherche par sujet avant de conclure. "
    "Si les extraits ne suffisent pas, relance une recherche avec une autre formulation avant de conclure. "
    + REGLES_REPONSE
)

MAX_TOURS = 3   # garde-fou : nombre maximum d'appels au modèle


def repondre_agent(question, chunks, vectors, k=4):
    """Pose la question à l'agent. Renvoie (réponse finale, requêtes faites, consommation)."""
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question},
    ]
    requetes = []                                    # trace : ce que l'agent a cherché
    tokens = {"entree": 0, "sortie": 0, "appels": 0} # consommation cumulée sur tous les tours

    for tour in range(MAX_TOURS):
        # 1. Le modèle lit toute la conversation et décide : répondre ou chercher
        reponse = client.chat.complete(
            model=MODELE,
            messages=messages,
            tools=[OUTIL_RETRIEVE],
            tool_choice="auto",
            parallel_tool_calls=False,
            temperature=0,
        )
        # On additionne à chaque tour : un agent relit tout l'historique à chaque appel,
        # donc ses tokens d'entrée grossissent d'un tour à l'autre. C'est ce coût qu'on veut voir.
        tokens["entree"] += reponse.usage.prompt_tokens
        tokens["sortie"] += reponse.usage.completion_tokens
        tokens["appels"] += 1

        message = reponse.choices[0].message
        messages.append(message)

        # 2. Pas de demande d'outil → c'est sa réponse finale : on sort
        if not message.tool_calls:
            return message.content, requetes, tokens

        # 3. Sinon, le harness exécute la recherche demandée
        appel = message.tool_calls[0]
        if appel.function.name != "retrieve":
            raise ValueError(f"Outil inconnu demandé : {appel.function.name}")

        requete = json.loads(appel.function.arguments)["requete"]
        requetes.append(requete)
        extraits = retrieve(requete, chunks, vectors, k=k)
        resultat = "\n\n".join(f"[{chunk['source']}]\n{chunk['texte']}" for score, chunk in extraits)

        messages.append({
            "role": "tool",
            "name": appel.function.name,
            "content": resultat,
            "tool_call_id": appel.id,
        })

    # 4. On sort de la boucle sans réponse : la limite de tours est atteinte
    return "Limite de recherches atteinte sans réponse finale.", requetes, tokens


if __name__ == "__main__":
    chunks, vectors = load_index()   # chargé une seule fois
    question = "Un locataire qui ne paie plus son loyer peut-il être expulsé en janvier ?"
    reponse, requetes, tokens = repondre_agent(question, chunks, vectors)
    print("Requêtes faites par l'agent :", requetes)
    print("Tokens :", tokens)
    print("Réponse :", reponse)