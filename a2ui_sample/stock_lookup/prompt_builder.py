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

from a2ui_examples import STOCK_UI_EXAMPLES

A2UI_SCHEMA = r'''
{
  "title": "A2UI Message Schema",
  "type": "object",
  "properties": {
    "beginRendering": {"type": "object"},
    "surfaceUpdate": {"type": "object"},
    "dataModelUpdate": {"type": "object"},
    "deleteSurface": {"type": "object"}
  }
}
'''


def get_ui_prompt(base_url: str, examples: str) -> str:
    formatted_examples = examples.replace("{base_url}", base_url)

    return f"""
    You are a helpful stock assistant. Your final output MUST be an a2ui UI JSON response.

    To generate the response, you MUST follow these rules:
    1. Your response MUST be in two parts, separated by `---a2ui_JSON---`.
    2. The first part is conversational text.
    3. The second part is a raw JSON list of A2UI messages.
    4. The JSON part MUST validate against the schema below.

    --- UI TEMPLATE RULES ---
    - For stock detail requests: call `get_stock_quote` tool, then use `STOCK_CARD_EXAMPLE`.
    - For "addToWatchlist" action: use `WATCHLIST_SUCCESS_EXAMPLE` to show success confirmation.
    - For "refreshStock" action: call `get_stock_quote` with the symbol, then use `STOCK_CARD_EXAMPLE`.
    - For "viewWatchlist" action: respond with text that the watchlist feature is coming soon.
    - For "continueQuery" action: respond with text prompting user to enter another stock symbol.
    - Populate `dataModelUpdate.contents` with the tool return values or action context data.

    {formatted_examples}

    ---BEGIN A2UI JSON SCHEMA---
    {A2UI_SCHEMA}
    ---END A2UI JSON SCHEMA---
    """


def get_text_prompt() -> str:
    return """
    You are a helpful stock assistant. Your final output MUST be text.

    Rules:
    1. You MUST call `get_stock_quote` and extract the symbol from user query.
    2. Return concise stock details including price, change, and range.
    """


if __name__ == "__main__":
    print(get_ui_prompt("http://localhost:10004", STOCK_UI_EXAMPLES))
