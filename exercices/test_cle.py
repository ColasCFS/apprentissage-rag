from dotenv import load_dotenv
import os

load_dotenv()
print(os.getenv("ANTHROPIC_API_KEY") is not None)