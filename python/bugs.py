import edgar 
edgar.set_identity("johndoe@gmail.com")

company = edgar.Company("MSFT")
filings = company.get_filings(form='10-K')
print(f"Oldest 10-K: {filings[0].accession_no}")  # What date do you see?

def getLatest10K(company):
    company = edgar.Company(company)
    filings = company.get_filings(form='10-K')
    return filings.iloc[0] if not filings.empty else None

filings = company.get_filings(form='10-K')
head_filings = filings.head(10)
files = []
for filing in head_filings:
    print(f'{filing.filing_date} - {filing.accession_number}')
    numr = filing.accession_number

xbrl = edgar.Filing(cik=company.cik, company=filing.company,  form=filing.form, filing_date=filing.filing_date, accession_no=filing.accession_number).xbrl()#.to_pandas()
# print(xbrl.statements.income_statement())
print(getLatest10K("AAPL"))


# print(files[0])