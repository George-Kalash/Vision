from edgar import *  
from edgar.xbrl.xbrl import XBRL
from datetime import date
import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

set_identity(os.getenv("EDGAR_IDENTITY", "Your Name your.email@example.com"))
__all__ = ['getStatementXBRL', 'listRecentFilings']
def _quarter_bounds(year: int, quarter: int) -> tuple[str, str]:
    if quarter not in (1, 2, 3, 4):
        raise ValueError("quarter must be 1..4")
    starts = {1: (1, 1), 2: (4, 1), 3: (7, 1), 4: (10, 1)}
    ends   = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}
    s = date(year, *starts[quarter]).strftime("%Y-%m-%d")
    e = date(year, *ends[quarter]).strftime("%Y-%m-%d")
    return s, e

def listRecentFilings(ticker: str = "AAPL", form: str = "10-Q", count: int = 5):
    co = Company(ticker)
    filings = co.get_filings(form=form, is_xbrl=True, amendments=True).head(count)
    print(f"Recent {form} filings for {ticker}:")
    for filing in filings:
        print(f"  - {filing.filing_date}: {filing.form} - {filing.accession_number}")
    return filings

def getStatementXBRL(ticker: str = "AAPL", form: str = "10-K", statement: str = "IS", *,
        year: int | None = None, quarter: int | None = None): 
    # reeturns the statements obj
    #statement = IS - income stmt, CF - cashflow stmt, BS - balance sheet
    
    co = Company(ticker)
    filings = co.get_filings(form=form, is_xbrl=True, amendments=True)
    if filings.empty:
        return None

    # If no year/quarter specified, get the latest filing
    if year is None and quarter is None:
        filing = filings.latest()
    elif year is not None and quarter is None:
        date_filter = f"{year}-01-01:{year}-12-31"
        filings = filings.filter(date=date_filter)
        filing = filings.latest()
    elif year is not None and quarter is not None:
        start, end = _quarter_bounds(year, quarter)
        filings = filings.filter(date=f"{start}:{end}")
        filing = filings.latest()
    else:
        filing = filings.latest()
    
    if not filing:
        return None
    
    xb = filing.xbrl() 
    if not xb:
        return None
    return xb.statements

def stitch_by_concept_iterative(stmt_list: list) -> pd.DataFrame | None:
  if not stmt_list:
    return None
  
  result_df = None
  
  for i, stmt_df in enumerate(stmt_list):
    if stmt_df is None or stmt_df.empty:
      continue
    
    # Clean the statement to remove duplicates and dimensional metadata
    stmt_df = clean_financial_statement(stmt_df)
      
    if result_df is None:
      
      result_df = stmt_df.drop(columns=['level', 'abstract', 'dimension'], errors='ignore').copy()
    
      value_cols = [col for col in result_df.columns if col not in ['concept', 'label']]


      
    else:
      stmt_copy = stmt_df.drop(columns=['level', 'abstract', 'dimension'], errors='ignore').copy()
      
      value_cols = [col for col in stmt_copy.columns if col not in ['concept', 'label']]

      # OUTER JOIN on concept - this preserves ALL concepts from both sides
      # Same concepts: data goes in same row
      # Different concepts: new row created with NaN for missing columns
      result_df = pd.merge(
        result_df,
        stmt_copy,
        on='concept',
        how='outer',  # CRITICAL: 'outer' preserves all concepts and fills missing with NaN
        suffixes=('', '_temp')
      )

      if 'label_temp' in result_df.columns:

        result_df['label'] = result_df['label'].fillna(result_df['label_temp'])
        result_df = result_df.drop(columns=['label_temp'])
        columns_to_drop = [col for col in result_df.columns if '_temp' in col]
        result_df = result_df.drop(columns=columns_to_drop, axis=1)
  
  # Sort by concept for better readability, but ensure Net Income is always last
  if result_df is not None and 'concept' in result_df.columns:
    result_df = sort_financial_statement(result_df)
  
  return result_df

def sort_financial_statement(df: pd.DataFrame) -> pd.DataFrame:
  """
  Sort financial statement with Net Income always as the last row
  """
  if df.empty or 'concept' not in df.columns:
    return df
  
  # Identify Net Income rows (various possible concept names)
  net_income_patterns = [
    'NetIncome',
    'NetIncomeLoss',
    'ProfitLoss',
    'us-gaap_NetIncomeLoss',
    'us-gaap_NetIncome', 
    'us-gaap_ProfitLoss',
    'ifrs-full_ProfitLoss',
    'ifrs-full_NetIncome'
  ]
  
  # Find Net Income rows
  net_income_mask = df['concept'].str.contains('|'.join(net_income_patterns), na=False, case=False)
  
  # Separate Net Income rows from other rows
  net_income_rows = df[net_income_mask].copy()
  other_rows = df[~net_income_mask].copy()
  
  # Sort other rows alphabetically by concept using a simple approach
  if not other_rows.empty and 'concept' in other_rows.columns:
    # Create a simple sorting key
    sorted_indices = sorted(range(len(other_rows)), key=lambda i: str(other_rows.iloc[i]['concept']))
    other_rows = other_rows.iloc[sorted_indices].reset_index(drop=True)
  
  # Concatenate: other rows first, then Net Income rows
  if not net_income_rows.empty:
    result_df = pd.concat([other_rows, net_income_rows], ignore_index=True)
  else:
    result_df = other_rows
  
  # Ensure we return a DataFrame
  return pd.DataFrame(result_df)

def smart_column_sort(df, newest_first=False):
  date_cols = []
  other_cols = []
  
  for col in df.columns:
    col_str = str(col)
    
    date_patterns = [
      r'(\d{4}[-_]\d{2}[-_]\d{2})',  # YYYY-MM-DD
      r'(\d{4}[-_]Q[1-4])',          # YYYY-Q1
      r'(\d{4})',                    # YYYY (if 4 digits)
      r'(\d{2}[-_]\d{2}[-_]\d{4})',  # MM-DD-YYYY
    ]
    
    found_date = False
    for pattern in date_patterns:
      match = re.search(pattern, col_str)
      if match:
        try:
          if 'Q' in match.group(1):
            # Handle quarterly
            quarter_match = re.search(r'(\d{4})[-_]Q([1-4])', match.group(1))
            if quarter_match:
              year, quarter = quarter_match.groups()
              date_obj = pd.to_datetime(f'{year}-{int(quarter)*3:02d}-01')
            else:
              continue
          else:
            date_obj = pd.to_datetime(match.group(1))
          
          date_cols.append((col, date_obj))
          found_date = True
          break
        except:
          continue
    
    if not found_date:
      other_cols.append(col)
  
  # Sort date columns
  date_cols.sort(key=lambda x: x[1], reverse=newest_first)
  sorted_date_cols = [col[0] for col in date_cols]
  
  return df[other_cols + sorted_date_cols]

def clean_financial_statement(df: pd.DataFrame) -> pd.DataFrame:
  """
  Clean financial statement by grouping same concepts and filling missing data with NaN
  Only filters by concept - if concept is same, put in same row
  If concept is different, put in next row with NaN for missing columns
  """
  if df.empty or 'concept' not in df.columns:
    return df
  
  # Group by concept and handle duplicates
  def merge_concept_rows(group):
    if len(group) == 1:
      return group.iloc[0]
    
    # Create a merged row
    merged_row = {}
    
    for col in group.columns:
      if col == 'concept':
        # Keep the concept value
        merged_row[col] = group[col].iloc[0]
      elif col == 'label':
        # For label, take the first non-null value
        non_null_labels = group[col].dropna()
        merged_row[col] = non_null_labels.iloc[0] if not non_null_labels.empty else None
      else:
        # For other columns (especially numeric), take the first non-null value
        non_null_values = group[col].dropna()
        merged_row[col] = non_null_values.iloc[0] if not non_null_values.empty else None
    
    return pd.Series(merged_row)
  
  # Group by concept and merge duplicate concepts
  df_cleaned = df.groupby('concept', group_keys=False).apply(merge_concept_rows)
  
  # Reset index to ensure clean row numbering
  df_cleaned = df_cleaned.reset_index(drop=True)
  
  # Ensure we return a DataFrame
  if isinstance(df_cleaned, pd.Series):
    df_cleaned = df_cleaned.to_frame().T
  
  return pd.DataFrame(df_cleaned)


