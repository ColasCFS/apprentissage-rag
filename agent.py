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

# 2. Consigne système : rôle de l'agent + règle d'usage de l'outil
SYSTEM = (
    "Tu es un assistant sur le droit de la location en France. "
    "Pour répondre, utilise l'outil retrieve et réponds uniquement à partir des extraits obtenus."
)

SYSTEM = (
    "Tu es un assistant sur le droit de la location en France. "
    "Pour répondre, utilise l'outil retrieve. "
    "Règles de réponse : "
    "N'utilise que les informations présentes dans les extraits ; n'ajoute aucun article de loi, "
    "chiffre ou condition qui n'y figure pas. "
    "Tu peux interpréter la question (si elle est ambiguë, indique en une phrase l'interprétation retenue) "
    "et raisonner à partir des extraits pour en déduire la réponse, même si la formulation diffère. "
    "Ne transpose pas une règle d'une situation à une autre (ex. une règle sur les travaux "
    "ne s'applique pas aux visites). "
    "Avant de répondre, vérifie si la question touche plusieurs sujets (ex. une procédure ET un délai, "
    "une règle ET ses conséquences) : si oui, fais une recherche par sujet avant de conclure."
    "Cite la source de chaque affirmation entre crochets, ex. [droit_de_visite.txt]. "
    "Si les extraits ne suffisent pas, relance une recherche ou dis ce qui manque."
)

MAX_TOURS = 3   # garde-fou : nombre maximum d'appels au modèle


def repondre_agent(question, chunks, vectors, k=4):
    """Pose la question à l'agent. Renvoie (réponse finale, liste des requêtes faites)."""
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question},
    ]
    requetes = []   # trace : ce que l'agent a cherché, dans l'ordre

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
        message = reponse.choices[0].message
        messages.append(message)

        # 2. Pas de demande d'outil → c'est sa réponse finale : on sort
        if not message.tool_calls:
            return message.content, requetes

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
    return "Limite de recherches atteinte sans réponse finale.", requetes


if __name__ == "__main__":
    chunks, vectors = load_index()   # chargé une seule fois
    question = "Un locataire qui ne paie plus son loyer peut-il être expulsé en janvier ?"
    reponse, requetes = repondre_agent(question, chunks, vectors)
    print("Requêtes faites par l'agent :", requetes)
    print("Réponse :", reponse)