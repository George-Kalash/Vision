from __future__ import annotations

import time
import logging
from datetime import date, datetime
from io import StringIO
from typing import Any
from pathlib import Path
import json
import shutil

import pandas as pd
from flask import Flask, jsonify, render_template, request

from Enterprize import Enterprize
from utilities import strip_first_last_lines, truncate_large_numbers
from genai_unti import normalize_column_name

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


CLEANED_RESPONSE_PATH = Path(__file__).with_name("cleaned_response.json")
_MAX_NORMALIZE_ATTEMPTS = 5
_NORMALIZE_BACKOFF_SECONDS = 1.5
_FILE_POLL_INTERVAL = 0.5


def _to_serializable(value: Any) -> Any:
  if value is None:
    return None
  if pd.isna(value):
    return None
  if isinstance(value, pd.Timestamp):
    return value.to_pydatetime().isoformat()
  if isinstance(value, (datetime, date)):
    return value.isoformat()
  if hasattr(value, "item"):
    try:
      return value.item()  # numpy scalars
    except (ValueError, TypeError):
      return value
  return value


def _cleaned_response_mtime() -> float:
  try:
    return CLEANED_RESPONSE_PATH.stat().st_mtime
  except FileNotFoundError:
    return 0.0


def _load_normalized_dataframe(payload: str) -> pd.DataFrame:
  try:
    normalized_df = pd.read_json(StringIO(payload))
  except ValueError as exc:
    raise ValueError("Failed to parse Gemini normalized response") from exc
  if normalized_df is None or normalized_df.empty:
    raise ValueError("Gemini normalization produced an empty table")
  return normalized_df


def _wait_for_cleaned_response(previous_mtime: float) -> pd.DataFrame:
  while True:
    try:
      current_stat = CLEANED_RESPONSE_PATH.stat()
    except FileNotFoundError:
      current_stat = None
    if current_stat and current_stat.st_mtime > previous_mtime:
      payload = CLEANED_RESPONSE_PATH.read_text(encoding="utf-8").strip()
      if not payload:
        time.sleep(_FILE_POLL_INTERVAL)
        continue
      try:
        return _load_normalized_dataframe(payload)
      except ValueError:
        time.sleep(_FILE_POLL_INTERVAL)
        continue
    time.sleep(_FILE_POLL_INTERVAL)


def _try_normalize(ticker: str, df: pd.DataFrame, periods: int) -> tuple[pd.DataFrame, bool, str]:
  """Normalize via Gemini and wait for cleaned_response.json."""
  json_str = df.to_json(orient="records")
  
  # Trigger normalization
  frame = normalize_column_name(ticker, json_str, stmtType="IS")
  with open("response.json", "w") as f:
    f.write(frame)
  strip_first_last_lines("response.json", "cleaned_response.json")
  
  print("Stripped response saved to cleaned_response.json")
  
  cleaned_path = Path("cleaned_response.json")
  while True:
    if cleaned_path.exists():
      try:
        with open(cleaned_path, "r") as f:
          cleaned_data = json.load(f)
        if cleaned_data:  # Non-empty data found
          df = pd.DataFrame(cleaned_data).dropna(subset=['label'], how='all').reset_index(drop=True)
          normalized_df = df.drop(columns=['balance', "validation_errors"], errors='ignore')
          length = len(normalized_df.columns)
          if length > periods + 2:
            normalized_df = normalized_df.drop(normalized_df.columns[2:-periods-1], axis=1) # Drop excess columns from the end
          normalized_df = normalized_df.dropna(subset=normalized_df.columns[2:], how='all')
          normalized_df = normalized_df.applymap(truncate_large_numbers)
          print("Normalization successful ✅")
          return normalized_df, True, ""
      except (json.JSONDecodeError, ValueError):
        pass  # File not ready yet, keep waiting
    time.sleep(0.5)


def _clear_edgar_cache():
  """Clear edgartools HTTP cache to force fresh data fetch."""
  cache_dir = Path.home() / ".cache" / "httpx-cache"
  if cache_dir.exists():
    try:
      shutil.rmtree(cache_dir)
      logger.info("Cleared edgartools cache")
    except Exception as exc:
      logger.warning("Failed to clear cache: %s", exc)


def _fetch_income_statement(ticker: str, years: int) -> tuple[pd.DataFrame, dict[str, Any], bool, str]:
  years = max(1, min(years, 10))
  try:
    enterprise = Enterprize(ticker)
  except Exception as exc:
    if "data sources are unavailable" in str(exc).lower() or "304" in str(exc):
      logger.info("Cache issue detected, clearing cache and retrying...")
      _clear_edgar_cache()
      enterprise = Enterprize(ticker)
    else:
      raise
  statement_df = enterprise.getFilings(filingType="10-K", stmtType="IS", periods=years - 1)
  print(statement_df)
  if statement_df is None or statement_df.empty:
    raise ValueError("No income statement data available for the requested range")
  normalized_df, normalized, note = _try_normalize(ticker, statement_df.reset_index(drop=True), years - 1)
  try:
    latest_price = enterprise.latestPrice
  except Exception:  # noqa: BLE001
    latest_price = None
  company_meta = {
    "ticker": enterprise.ticker.upper(),
    "name": getattr(enterprise, "name", enterprise.ticker.upper()),
    "latestPrice": latest_price,
  }
  return normalized_df, company_meta, normalized, note


def _serialize_dataframe(df: pd.DataFrame) -> tuple[list[str], list[dict[str, Any]]]:
  columns = df.columns.tolist()
  records: list[dict[str, Any]] = []
  for _, row in df.iterrows():
    record: dict[str, Any] = {}
    for col in columns:
      record[col] = _to_serializable(row[col])
    records.append(record)
  return columns, records


@app.route("/")
def index():
  return render_template("index.html")


@app.route("/api/income-statement", methods=["POST"])
def income_statement():
  payload = request.get_json(silent=True) or {}
  ticker = str(payload.get("ticker", "")).strip().upper()
  years_raw = payload.get("years", 10)
  try:
    years = int(years_raw)
  except (TypeError, ValueError):
    years = 10
  if not ticker:
    return jsonify({"error": "Ticker is required"}), 400
  if years <= 0:
    years = 1
  try:
    df, company_meta, normalized, note = _fetch_income_statement(ticker, years)
    columns, rows = _serialize_dataframe(df)
    response = {
      "company": company_meta,
      "columns": columns,
      "rows": rows,
      "normalized": normalized,
    }
    if note:
      response["note"] = note
    return jsonify(response)
  except ValueError as exc:
    return jsonify({"error": str(exc)}), 404
  except Exception as exc:  # noqa: BLE001
    logger.exception("Failed to build income statement for %s", ticker)
    error_msg = str(exc)
    if "data sources are unavailable" in error_msg.lower():
      error_msg = "SEC data sources are temporarily unavailable. Please try again in a few moments."
    elif "cik" in error_msg.lower():
      error_msg = f"Unable to find company data for ticker '{ticker}'. Please verify the ticker symbol."
    return jsonify({"error": error_msg}), 500


if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=8000)
