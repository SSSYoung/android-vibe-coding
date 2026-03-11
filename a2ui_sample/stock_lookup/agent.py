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

import os

from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from prompt_builder import A2UI_SCHEMA, STOCK_UI_EXAMPLES, get_text_prompt, get_ui_prompt
from shared_a2ui import SchemaValidatedA2uiAgent
from tools import get_stock_quote

AGENT_INSTRUCTION = """
You are a helpful stock assistant.

Rules:
1. For stock detail requests, you MUST call get_stock_quote.
2. Use the returned fields to populate A2UI JSON.
"""


class StockAgent(SchemaValidatedA2uiAgent):
    """Stock sample agent using shared A2UI flow."""

    def __init__(self, base_url: str, use_ui: bool = False):
        super().__init__(
            base_url=base_url,
            use_ui=use_ui,
            a2ui_schema=A2UI_SCHEMA,
            max_retries=1,
            allow_empty_json=False,
        )

    def get_processing_message(self) -> str:
        return "Fetching stock quote..."

    def _build_agent(self, use_ui: bool) -> LlmAgent:
        model_name = os.getenv("LITELLM_MODEL", "gemini/gemini-2.5-flash")
        if use_ui:
            instruction = AGENT_INSTRUCTION + get_ui_prompt(self.base_url, STOCK_UI_EXAMPLES)
        else:
            instruction = get_text_prompt()

        return LlmAgent(
            model=LiteLlm(model=model_name),
            name="stock_agent",
            description="An agent that provides stock quote details.",
            instruction=instruction,
            tools=[get_stock_quote],
        )
