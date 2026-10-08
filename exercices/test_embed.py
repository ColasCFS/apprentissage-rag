from dotenv import load_dotenv
from mistralai.client import Mistral
import os

load_dotenv()

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-embed"

client = Mistral(api_key=api_key)


note1 = "La location est un business qui peut rapporter des revenus passifs, mais qui est soumis à une forte législation en France et à une fiscalité qu'il est important de connaître."
note2 = "Il ne fait pas beau en Crète à Heraklion ce week-end. C'est dommage. J'avais un mariage, celui de Marine. "


embeddings_batch_response = client.embeddings.create(
    model=model,
    inputs=[note1, note2],
)




print(len(embeddings_batch_response.data))
print(len(embeddings_batch_response.data[0].embedding))


