from __future__ import annotations

import logging
from datetime import date, datetime
from io import StringIO
from typing import Any

import pandas as pd
from flask import Flask, jsonify, render_template, request

from Enterprize import Enterprize
from genai_unti import normalize_column_name

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


def _try_normalize(ticker: str, df: pd.DataFrame) -> tuple[pd.DataFrame, bool, str]:
  try:
    stmt_json = df.to_json(index=False)
    normalized_payload = normalize_column_name(ticker, stmt_json)
    if not normalized_payload:
      return df, False, ""
    payload_str = str(normalized_payload).strip()
    if not payload_str:
      return df, False, ""
    starts_with_json = payload_str[0] in {"{", "["}
    if not starts_with_json:
      return df, False, payload_str
    try:
      normalized_df = pd.read_json(StringIO(payload_str))
    except (ValueError, TypeError) as exc:
      return df, False, f"Unable to parse normalized response: {exc}"
    if normalized_df is None or normalized_df.empty:
      return df, False, ""
    return normalized_df, True, ""
  except Exception as exc:  # noqa: BLE001
    logger.warning("Normalization failed for %s: %s", ticker, exc)
    return df, False, str(exc)


def _fetch_income_statement(ticker: str, years: int) -> tuple[pd.DataFrame, dict[str, Any], bool, str]:
  years = max(1, min(years, 10))
  enterprise = Enterprize(ticker)
  statement_df = enterprise.getFilings(filingType="10-K", stmtType="IS", periods=years - 1)
  if statement_df is None or statement_df.empty:
    raise ValueError("No income statement data available for the requested range")
  normalized_df, normalized, note = _try_normalize(ticker, statement_df.reset_index(drop=True))
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
    return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=8000)
