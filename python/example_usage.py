# Example of importing and using getStatementXBRL from utilities.py

from utilities import getStatementXBRL

def main():
  
    # Get Apple's latest 10-K income statement
    statements = getStatementXBRL("AAPL", "10-K", "IS")
    
    if statements:
        print("Successfully retrieved XBRL statements")
        print(f"Type: {type(statements)}")
        print(statements.income_statement())
        # You can now work with the statements object
    else:
        print("Failed to retrieve statements")

    # # Get quarterly data (example for Q1 2024)
    # quarterly_statements = getStatementXBRL("AAPL", "10-K", "IS", year=2010)
    
    # if quarterly_statements:
    #     print("Successfully retrieved quarterly statements")
    #     print(quarterly_statements.income_statement().to_dataframe())
    # else:
    #     print("No quarterly statements found")

if __name__ == "__main__":
    main()