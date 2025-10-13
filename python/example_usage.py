# Example of importing and using getStatementXBRL from utilities.py
import os
from urllib import response
# from genai import client
from Enterprize import Enterprize
import pandas as pd
from genai_unti import normalize_column_name

def strip_first_last_lines(input_file, output_file=None):
  if output_file is None:
    output_file = input_file  # Overwrite original
  
  with open(input_file, "r") as f:
    lines = f.readlines()
  
  # Remove first and last lines
  if len(lines) > 2:
    stripped_lines = lines[1:-1]
      
    with open(output_file, "w") as f:
      f.writelines(stripped_lines)
    print(f"Stripped file saved to {output_file}")
  else:
    print("File has too few lines to strip")



def main():
    
  company = Enterprize('MU')
  stmt = company.getFilings(filingType="10-K", stmtType="IS", periods=10)
  print(f"title: {company.name} ({company.ticker})")
  print(stmt)
  stmt_json = stmt.to_json(index=False) # type: ignore
  response = normalize_column_name("MU", stmt_json)
  print(response)
  json_data = response
  
  # Write the JSON response to a file
  if json_data:
    with open("response.json", "w") as f:
      f.write(json_data)
    print("Response saved to response.json")
  else:
    print("No response data to save")
  strip_first_last_lines("response.json", "cleaned_response.json")
  # print("\n----------------------------------------\n")
  # # print(response)
  df_from_string = pd.read_json("cleaned_response.json")
  print(df_from_string)

if __name__ == "__main__":
  # Given the following financial statement, segregate every row by proper concept ie if there is two rows that have the same intrinsic meaning but different titles make sure to collect them under the same title, as would revenue and gross sales would usually mean the same. Make sure to not oversimplify, only combine what should and would be combined by the analysts looking. NaN can be overriden by any relevant number:\n{stmt.to_markdown()}. Please return it in a markdown table format."}
  main() 