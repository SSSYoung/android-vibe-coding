# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import httpx
from google.adk.tools.tool_context import ToolContext

logger = logging.getLogger(__name__)

# 使用 pathlib 获取当前文件所在目录
_SCRIPT_DIR = Path(__file__).resolve().parent
_MOCK_DATA_PATH = _SCRIPT_DIR / "stock_data.json"


def _load_mock_data() -> dict:
    logger.info("Loading mock data from: %s", _MOCK_DATA_PATH)
    if not _MOCK_DATA_PATH.exists():
        logger.error("Mock data file not found: %s", _MOCK_DATA_PATH)
        raise FileNotFoundError(f"Mock data file not found: {_MOCK_DATA_PATH}")

    # 使用 utf-8-sig 处理可能存在的 BOM 标记
    with open(_MOCK_DATA_PATH, encoding="utf-8-sig") as f:
        data = json.load(f)
        logger.info("Mock data loaded successfully, keys: %s", list(data.keys()))
        return data


def _format_quote(payload: dict) -> dict:
    symbol = payload.get("symbol", "")
    currency = payload.get("currency", "USD")
    price = payload.get("price")
    change = payload.get("change")
    change_percent = payload.get("change_percent")

    if change is not None and change_percent is not None:
        sign = "+" if change >= 0 else ""
        change_summary = f"{sign}{change:.2f} ({sign}{change_percent:.2f}%)"
    else:
        change_summary = "N/A"

    market_time = payload.get("market_time")
    if not market_time:
        market_time = datetime.now(timezone.utc).strftime("As of %Y-%m-%d %H:%M UTC")

    return {
        "symbol": symbol,
        "name": payload.get("name", symbol),
        "price": f"{price} {currency}" if price is not None else "N/A",
        "change_summary": change_summary,
        "market_time": market_time,
        "open": f"Open: {payload.get('open', 'N/A')}",
        "high": f"High: {payload.get('high', 'N/A')}",
        "low": f"Low: {payload.get('low', 'N/A')}",
        "volume": f"Volume: {payload.get('volume', 'N/A')}",
    }


def _fetch_yahoo_quote(symbol: str) -> dict:
    url = "https://query1.finance.yahoo.com/v7/finance/quote"
    with httpx.Client(timeout=10.0) as client:
        response = client.get(url, params={"symbols": symbol})
        response.raise_for_status()
        data = response.json()

    results = data.get("quoteResponse", {}).get("result", [])
    if not results:
        raise ValueError("No quote result")

    quote = results[0]
    market_time = quote.get("regularMarketTime")
    if market_time:
        market_time = datetime.fromtimestamp(market_time, tz=timezone.utc).strftime(
            "As of %Y-%m-%d %H:%M UTC"
        )

    return {
        "symbol": quote.get("symbol", symbol),
        "name": quote.get("shortName") or quote.get("longName") or symbol,
        "currency": quote.get("currency", "USD"),
        "price": quote.get("regularMarketPrice"),
        "change": quote.get("regularMarketChange"),
        "change_percent": quote.get("regularMarketChangePercent"),
        "open": quote.get("regularMarketOpen"),
        "high": quote.get("regularMarketDayHigh"),
        "low": quote.get("regularMarketDayLow"),
        "volume": quote.get("regularMarketVolume"),
        "market_time": market_time,
    }


def get_stock_quote(symbol: str, tool_context: ToolContext) -> str:
    """Call this tool to get details for a single stock symbol."""
    symbol = (symbol or "").strip().upper()
    logger.info("--- TOOL CALLED: get_stock_quote ---")
    logger.info("  - Symbol: %s", symbol)

    if not symbol:
        logger.warning("Empty symbol provided")
        return json.dumps({})

    # 直接使用本地 mock 数据
    try:
        mock_data = _load_mock_data()
        logger.info("Mock data loaded, available symbols: %s", list(mock_data.keys()))

        if symbol in mock_data:
            quote = dict(mock_data[symbol])
            logger.info("Found exact match for %s in mock data", symbol)
        else:
            # 如果没有精确匹配，使用 AAPL 数据但替换 symbol
            quote = dict(mock_data.get("AAPL", {}))
            quote["symbol"] = symbol
            quote["name"] = f"{symbol} (Mock Data)"
            logger.info("Using AAPL mock data for %s", symbol)

        result = _format_quote(quote)
        logger.info("Formatted quote: %s", result)
        return json.dumps(result)
    except Exception as exc:
        logger.error("Mock data load failed: %s", exc)
        # 返回硬编码的备用数据
        fallback = {
            "symbol": symbol,
            "name": f"{symbol} (Fallback)",
            "price": "N/A",
            "change_summary": "N/A",
            "market_time": datetime.now(timezone.utc).strftime("As of %Y-%m-%d %H:%M UTC"),
            "open": "Open: N/A",
            "high": "High: N/A",
            "low": "Low: N/A",
            "volume": "Volume: N/A",
        }
        return json.dumps(fallback)
