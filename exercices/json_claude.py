from dotenv import load_dotenv
from anthropic import Anthropic
import json
load_dotenv()
client = Anthropic()

texte = "Un RAG combine une recherche dans des documents avec un modèle de langage pour répondre avec des sources."
demande = f'Voici un texte : {texte}\n\nRéponds uniquement avec un JSON de la forme {{"resume": "...", "mots_cles": ["...", "..."]}}, sans aucun autre texte.'

response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role":"user","content":demande}]
       )

brut = response.content[0].text
propre = brut.replace("```json", "").replace("```", "")

try:
        data = json.loads(propre)
except json.JSONDecodeError as e:
    print(f"Erreur lors du décodage JSON")
    print(f"Message brut : {brut}")
    print(f"Le Programme s'arrête ici, veuillez corriger le prompt pour qu'il renvoie un JSON valide.")
    raise SystemExit(1)
 

print(data["resume"])
