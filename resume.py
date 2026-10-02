import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

if len(sys.argv)<2:
    print("Nombre d'élément de la liste insuffisant, veuillez entrer un nom sous la forme 'python resume.py dossier/")
    raise SystemExit(1)

chemin_cible = Path(sys.argv[1])

if chemin_cible.is_dir():
    print("Le chemin n'est pas un fichier, veuillez entrer un nom sous la forme 'python resume.py dossier/fichier")
    raise SystemExit(1)

try:

    with open(chemin_cible, "r", encoding="utf-8") as f:
        fichier = f.read()  

except FileNotFoundError:
        print("Le chemin n'existe pas, veuillez entrer un nom sous la forme 'python resume.py dossier/fichier.txt'")
        raise SystemExit(1)  



question = "Quel est le sujet de ce document? réponds avec un JSON avec deux clés : resume et points_cles"
contenu = f"Voici un document : {fichier}\n\nRéponds uniquement à partir de ce document : {question}"

response=client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=500,
    messages=[{"role":"user","content":contenu}]
)

brut= response.content[0].text

propre = brut.replace("```json", "").replace("```", "")

try:
        data = json.loads(propre)
   
except json.JSONDecodeError as e:
    print(f"Erreur lors du décodage JSON")
    print(f"Message brut : {brut}")
    print(f"Le Programme s'arrête ici, veuillez corriger le prompt pour qu'il renvoie un JSON valide.")
    raise SystemExit(1)
 
try:
    data_resume = data["resume"]
except KeyError as e:
    print(f"Clé \"resume\" introuvable dans le JSON : {e}")
    raise SystemExit(1)

try:
    data_point_cles = data["points_cles"]
    
except KeyError as e:
    print(f"Clé \"points_cles\" introuvable dans le JSON : {e}")
    raise SystemExit(1)

cout_input_token_M = 1
cout_output_token_M = 5
cout_input_token = cout_input_token_M/1000000
cout_output_token = cout_output_token_M/1000000
cout_input = cout_input_token * (response.usage.input_tokens)
cout_output = cout_output_token * (response.usage.output_tokens)


donne_resume = {
    "resume": data_resume,
    "points_cles": data_point_cles,
    "tokens_utilises": {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens
    },
    "cout_total": (cout_input + cout_output)
}
donne_resume =json.dumps(donne_resume, indent=2, ensure_ascii=False)

print(donne_resume)
