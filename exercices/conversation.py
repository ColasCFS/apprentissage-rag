from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()
messages=[]
prompt ="Mon prénom est Colas."


def assistant_response(prompt):
    messages.append({"role":"user","content":prompt})
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=messages
    )
    
    messages.append({"role":"assistant","content":response.content[0].text})
    print(response.usage.input_tokens)
    return response.content[0].text



assistant_response(prompt)
assistant_response("Quel est mon prénom ?")
assistant_response("Résume notre conversation en une phrase.")
print (messages)