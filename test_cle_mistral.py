from dotenv import load_dotenv
import os

load_dotenv()
print(os.getenv("MISTRAL_API_KEY") is not None)