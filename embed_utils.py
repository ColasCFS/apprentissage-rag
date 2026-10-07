from dotenv import load_dotenv
from mistralai.client import Mistral
import os
import numpy as np

load_dotenv()

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-embed"

client = Mistral(api_key=api_key)



def embed(textes):
    response = client.embeddings.create(model=model, inputs=textes)
    return [d.embedding for d in response.data]

def cosinus(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))