# Example of importing and using getStatementXBRL from utilities.py


from Enterprize import Enterprize

def main():
    
    company = Enterprize('U')
    stmt = company.getFilings(filingType="10-K", stmtType="IS", periods=10)
    print(f"title: {company.name} ({company.ticker})")
    print(stmt)
  

if __name__ == "__main__":
    main() 