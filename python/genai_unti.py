import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError

load_dotenv()


def normalize_column_name(name: str, json_file, stmtType="IS") -> str:
  api_key = os.getenv("GEMINI_API_KEY", "api_key_not_set")
  client = genai.Client(api_key=api_key)
  if(stmtType == "IS"):
    prompt_type = "prompt_IS.txt"
  if(stmtType == "BS"):
    prompt_type = "prompt_BS.txt"
  if(stmtType == "CF"):
    prompt_type = "prompt_CF.txt"
  else:
    prompt_type = "prompt_IS.txt"
  with open(prompt_type, "r", encoding="utf-8") as f:
    prompt = f.read()
  model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
  contents = [prompt, json_file]

  for attempt in range(4):
    try:
      response = client.models.generate_content(
        model=model,
        contents=contents)  # type: ignore
      text = getattr(response, "text", "")
      print("Normalization successful ✅")
      return text or json_file
    except ServerError as exc:
      if getattr(exc, "status_code", None) == 503 and attempt < 3:
        wait_for = 2 ** attempt
        time.sleep(wait_for)
        continue
      
      print(f"Normalization failed with ServerError ❌: {exc}")
      return json_file
    except Exception as exc:
      print(f"Normalization failed with Exception ❌: {exc}")
      return json_file

  return json_file

