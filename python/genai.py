from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = 'YOU API KEY HERE'
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", "api_key_not_set"))

# model_info = client.models.get(model="gemini-2.0-flash")

# response = client.models.generate_content(
#   model="gemini-2.0-flash",
#   contents="Are you able to accept and receive a pd dataframe?"# type: ignore
# )
# print(response.text)
# print(model_info)