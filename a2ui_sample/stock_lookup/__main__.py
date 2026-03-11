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

import logging
import os

import click
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from a2ui.extension.a2ui_extension import get_a2ui_agent_extension
from agent import StockAgent
from agent_executor import StockAgentExecutor
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
    """Exception for missing API key."""


@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=10004)
def main(host, port):
    try:
        load_dotenv()
        model = os.getenv("LITELLM_MODEL", "gemini/gemini-2.5-flash")
        logger.info("Using model: %s", model)

        if model.startswith("gemini/") or model.startswith("google/"):
            if os.getenv("GOOGLE_GENAI_USE_VERTEXAI") != "TRUE":
                if not os.getenv("GEMINI_API_KEY"):
                    raise MissingAPIKeyError(
                        "GEMINI_API_KEY environment variable not set and GOOGLE_GENAI_USE_VERTEXAI is not TRUE."
                    )
                logger.info("Using Gemini API key")
        elif model.startswith("zai/"):
            if not os.getenv("ZAI_API_KEY"):
                raise MissingAPIKeyError(
                    "ZAI_API_KEY environment variable not set for ZhipuAI model."
                )
            logger.info("Using ZhipuAI (Z.AI) API key")

        capabilities = AgentCapabilities(
            streaming=True,
            extensions=[get_a2ui_agent_extension()],
        )
        skill = AgentSkill(
            id="get_stock_quote",
            name="Stock Quote Tool",
            description="Fetches current stock details by ticker symbol.",
            tags=["stock", "quote", "finance"],
            examples=["Show me AAPL stock details"],
        )

        base_url = f"http://{host}:{port}"

        agent_card = AgentCard(
            name="Stock Agent",
            description="This agent provides stock quote details by symbol.",
            url=base_url,
            version="1.0.0",
            default_input_modes=StockAgent.SUPPORTED_CONTENT_TYPES,
            default_output_modes=StockAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        agent_executor = StockAgentExecutor(base_url=base_url)

        request_handler = DefaultRequestHandler(
            agent_executor=agent_executor,
            task_store=InMemoryTaskStore(),
        )
        server = A2AStarletteApplication(
            agent_card=agent_card, http_handler=request_handler
        )

        import uvicorn

        app = server.build()
        app.add_middleware(
            CORSMiddleware,
            allow_origin_regex=r"http://localhost:\\d+",
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        uvicorn.run(app, host=host, port=port)
    except MissingAPIKeyError as exc:
        logger.error("Error: %s", exc)
        raise SystemExit(1)
    except Exception as exc:
        logger.error("An error occurred during server startup: %s", exc)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
