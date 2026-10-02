from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()



note = "La réunion budget du comité de pilotage aura lieu le 14 novembre en salle Mercure."
question = "Quand a lieu la réunion budget du comité de pilotage, et dans quelle salle ?"
contenu = f"Voici un document : {note}\n\nRéponds uniquement à partir de ce document : {question}"

response=client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=300,
    messages=[{"role":"user","content":contenu}]
)

cout_input_token_M = 1
cout_output_token_M = 5
cout_input_token = cout_input_token_M/1000000
cout_output_token = cout_output_token_M/1000000
cout_input = cout_input_token * (response.usage.input_tokens)
cout_output = cout_output_token * (response.usage.output_tokens)

print (response.content[0].text)
print(f"Tokens d'entrée : {response.usage.input_tokens}, au prix de {cout_input_token_M}$/M tokens, soit {cout_input:.6f}$")
print(f"Tokens de sortie : {response.usage.output_tokens}, au prix de {cout_output_token_M}$/M tokens, soit {cout_output:.6f}$")
print(f"Coût total : {cout_input + cout_output:.6f}$")