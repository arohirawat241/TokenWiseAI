import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Connect to Groq
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Ask Groq what models we are allowed to use
models = client.models.list()
print("\n✅ MODELS AVAILABLE TO YOUR API KEY:\n")
for model in models.data:
    print(f"- {model.id}")