from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
load_dotenv()



def normalize_column_name(name: str, json_file) -> str:
  GEMINI_API_KEY = 'YOU API KEY HERE'
  client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", "api_key_not_set"))
  prompt = 'Given the following financial statement, segregate every row by proper concept ie if there is two rows that have the same intrinsic meaning but different titles make sure to collect them under the same title, as would revenue and gross sales would usually mean the same. Make sure to not oversimplify, only combine what should and would be combined by the analysts looking. NaN can be overriden by any relevant number: \nPlease return it in the same table format. Always keep your json responce to the same format as provided in JSON schema do not alter the keys or structure. Assign rows based on the us-gaap concept taxonomy.'
  model = "gemini-2.5-flash"
  response = client.models.generate_content(
    model=model,
    contents=[prompt, json_file])# type: ignore
  return response.text

# model_info = client.models.get(model="gemini-2.0-flash")

# response = client.models.generate_content(
#   model="gemini-2.0-flash",
#   contents="Are you able to accept and receive a pd dataframe?"# type: ignore
# )
# print(response.text)
# print(model_info)