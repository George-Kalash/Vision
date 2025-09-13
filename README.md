# Vision - Stock Analyzer

This module is part of a stock analyzer project that uses SEC data to retrieve basic company information and financial metrics for further analysis.

## Files in this Directory

- **getData.py**: Script to fetch or process data from various online sources.
- **quotes.csv**: CSV file with stock quotes data.
- **requirements.txt**: Lists the Python dependencies required for the project.
- **sp500_top10_quotes.csv**: Contains stock data for the top 10 companies in the S&P 500.
- **top_20_NYSE_by_market_cap.csv**: CSV file with data for the top 20 NYSE companies by market capitalization.
- **testGetStock.py**: Unit tests for stock data retrieval functions.
- **tryAccessSECAPI.py**: Demonstrates accessing the SEC API using a configured User-Agent to obtain basic company facts.

## Setup & Usage

1. Create and activate your Python virtual environment (ignore .venv and .gitignore):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set the SEC User-Agent environment variable (as per SEC guidelines):
   ```bash
   export SEC_UA="Your Name your@email (YourApp/1.0)"
   ```
(The builder is currently in development, so features may not work as intended)

4. Run the specific scripts as needed, for example:
   ```bash
   python3 python/tryAccessSECAPI.py
   ```

## Overview

This directory holds the core scripts for a stock analyzer application. The analyzer leverages SEC data to get fundamental company details and financial information, which can be used for further stock analysis and decision-making.
