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

STOCK_UI_EXAMPLES = """
---BEGIN STOCK_CARD_EXAMPLE---
[
  { "beginRendering": { "surfaceId": "stock", "root": "root", "styles": { "primaryColor": "#0F766E", "font": "Roboto" } } },
  { "surfaceUpdate": {
    "surfaceId": "stock",
    "components": [
      { "id": "root", "component": { "Card": { "child": "mainColumn" } } },
      { "id": "mainColumn", "component": { "Column": { "children": { "explicitList": ["firstRow", "currentPrice", "changeInfo", "divider", "fourthRow", "fifthRow", "buttonRow"] }, "distribution": "start", "alignment": "stretch" } } },
      { "id": "firstRow", "component": { "Row": { "children": { "explicitList": ["stockCode", "stockName"] }, "distribution": "spaceBetween", "alignment": "center" } } },
      { "id": "stockCode", "component": { "Text": { "text": { "path": "symbol" }, "usageHint": "h2" } } },
      { "id": "stockName", "component": { "Text": { "text": { "path": "name" }, "usageHint": "body" } } },
      { "id": "currentPrice", "component": { "Text": { "text": { "path": "price" }, "usageHint": "h1" } } },
      { "id": "changeInfo", "component": { "Text": { "text": { "path": "change_summary" }, "usageHint": "body" } } },
      { "id": "divider", "component": { "Divider": { "axis": "horizontal" } } },
      { "id": "fourthRow", "component": { "Row": { "children": { "explicitList": ["highPrice", "lowPrice"] }, "distribution": "spaceEvenly", "alignment": "center" } } },
      { "id": "highPrice", "component": { "Text": { "text": { "path": "high" }, "usageHint": "caption" } } },
      { "id": "lowPrice", "component": { "Text": { "text": { "path": "low" }, "usageHint": "caption" } } },
      { "id": "fifthRow", "component": { "Row": { "children": { "explicitList": ["openPrice", "volume"] }, "distribution": "spaceEvenly", "alignment": "center" } } },
      { "id": "openPrice", "component": { "Text": { "text": { "path": "open" }, "usageHint": "caption" } } },
      { "id": "volume", "component": { "Text": { "text": { "path": "volume" }, "usageHint": "caption" } } },
      { "id": "buttonRow", "component": { "Row": { "children": { "explicitList": ["refreshBtn", "addWatchlistBtn"] }, "distribution": "spaceEvenly", "alignment": "center" } } },
      { "id": "refreshBtn", "component": { "Button": { "child": "refreshBtnText", "primary": false, "action": { "name": "refreshStock", "context": [ { "key": "symbol", "value": { "path": "symbol" } } ] } } } },
      { "id": "refreshBtnText", "component": { "Text": { "text": { "literalString": "刷新" } } } },
      { "id": "addWatchlistBtn", "component": { "Button": { "child": "addWatchlistBtnText", "primary": true, "action": { "name": "addToWatchlist", "context": [ { "key": "symbol", "value": { "path": "symbol" } }, { "key": "name", "value": { "path": "name" } } ] } } } },
      { "id": "addWatchlistBtnText", "component": { "Text": { "text": { "literalString": "加入自选" } } } }
    ]
  } },
  { "dataModelUpdate": {
    "surfaceId": "stock",
    "path": "/",
    "contents": [
      { "key": "symbol", "valueString": "AAPL" },
      { "key": "name", "valueString": "Apple Inc" },
      { "key": "price", "valueString": "$145.09" },
      { "key": "change_summary", "valueString": "+1.23 (+0.85%)" },
      { "key": "high", "valueString": "High: $147.00" },
      { "key": "low", "valueString": "Low: $143.50" },
      { "key": "open", "valueString": "Open: $144.00" },
      { "key": "volume", "valueString": "Volume: 3.5M" }
    ]
  } }
]
---END STOCK_CARD_EXAMPLE---

---BEGIN WATCHLIST_SUCCESS_EXAMPLE---
[
  { "beginRendering": { "surfaceId": "stock", "root": "root", "styles": { "primaryColor": "#10B981", "font": "Roboto" } } },
  { "surfaceUpdate": {
    "surfaceId": "stock",
    "components": [
      { "id": "root", "component": { "Card": { "child": "contentColumn" } } },
      { "id": "contentColumn", "component": { "Column": { "children": { "explicitList": ["checkmarkText", "titleText", "detailText", "buttonRow"] }, "distribution": "center", "alignment": "center" } } },
      { "id": "checkmarkText", "component": { "Text": { "text": { "literalString": "✓" }, "usageHint": "h1" } } },
      { "id": "titleText", "component": { "Text": { "text": { "literalString": "已加入自选" }, "usageHint": "h2" } } },
      { "id": "detailText", "component": { "Text": { "text": { "path": "message" }, "usageHint": "body" } } },
      { "id": "buttonRow", "component": { "Row": { "children": { "explicitList": ["viewWatchlistBtn", "continueQueryBtn"] }, "distribution": "spaceEvenly", "alignment": "center" } } },
      { "id": "viewWatchlistBtn", "component": { "Button": { "child": "viewWatchlistBtnText", "primary": true, "action": { "name": "viewWatchlist" } } } },
      { "id": "viewWatchlistBtnText", "component": { "Text": { "text": { "literalString": "查看自选" } } } },
      { "id": "continueQueryBtn", "component": { "Button": { "child": "continueQueryBtnText", "primary": false, "action": { "name": "continueQuery" } } } },
      { "id": "continueQueryBtnText", "component": { "Text": { "text": { "literalString": "继续查询" } } } }
    ]
  } },
  { "dataModelUpdate": {
    "surfaceId": "stock",
    "path": "/",
    "contents": [
      { "key": "message", "valueString": "AAPL - Apple Inc 已添加到您的自选列表" }
    ]
  } }
]
---END WATCHLIST_SUCCESS_EXAMPLE---
"""
