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

from pathlib import Path

from a2a.types import TaskState
from agent import StockAgent
from shared_a2ui import SimpleA2uiAgentExecutor


class StockAgentExecutor(SimpleA2uiAgentExecutor):
    """Stock executor using shared A2UI executor flow."""

    def __init__(self, base_url: str):
        super().__init__(
            ui_agent=StockAgent(base_url=base_url, use_ui=True),
            text_agent=StockAgent(base_url=base_url, use_ui=False),
            raw_log_filename="llm_raw_response.txt",
            raw_log_dir=str(Path(__file__).resolve().parent),
        )

    def resolve_query_from_event(self, action: str | None, context_data: dict) -> str:
        """Convert button action to a query for the Agent."""
        if action == "addToWatchlist":
            symbol = context_data.get("symbol", "")
            name = context_data.get("name", "")
            return f"User clicked addToWatchlist button for {name} ({symbol}). Show the WATCHLIST_SUCCESS_EXAMPLE UI with message: '{symbol} - {name} 已添加到您的自选列表'"

        elif action == "refreshStock":
            symbol = context_data.get("symbol", "")
            return f"Refresh stock data for {symbol}. Call get_stock_quote and show STOCK_CARD_EXAMPLE."

        elif action == "viewWatchlist":
            return "User wants to view their watchlist. Respond that this feature is coming soon."

        elif action == "continueQuery":
            return "User wants to search another stock. Prompt them to enter a stock symbol."

        return f"User action: {action} with data: {context_data}"

    def get_final_state(self, action: str | None) -> TaskState:
        """Determine task state based on action."""
        if action == "addToWatchlist":
            return TaskState.input_required
        return TaskState.input_required
