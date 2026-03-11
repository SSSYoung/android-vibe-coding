import json
import logging
from collections.abc import AsyncIterable
from typing import Any

import jsonschema
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

logger = logging.getLogger(__name__)


class SchemaValidatedA2uiAgent:
    """Shared base class for ADK agents with optional A2UI JSON output."""

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(
        self,
        base_url: str,
        use_ui: bool,
        a2ui_schema: str,
        max_retries: int = 1,
        allow_empty_json: bool = False,
    ):
        self.base_url = base_url
        self.use_ui = use_ui
        self.max_retries = max_retries
        self.allow_empty_json = allow_empty_json
        self._agent = self._build_agent(use_ui)
        self._user_id = "remote_agent"
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

        self.a2ui_schema_object = None
        try:
            single_message_schema = json.loads(a2ui_schema)
            self.a2ui_schema_object = {"type": "array", "items": single_message_schema}
            logger.info("A2UI schema loaded and wrapped as an array validator.")
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse A2UI schema: %s", exc)

    def _build_agent(self, use_ui: bool):
        raise NotImplementedError

    def get_processing_message(self) -> str:
        return "Processing request..."

    def _build_retry_prompt(self, original_query: str, error_message: str) -> str:
        return (
            f"Your previous response was invalid. {error_message} "
            "You MUST generate a valid response that strictly follows the A2UI JSON SCHEMA. "
            "The response MUST be a JSON list of A2UI messages. "
            "Ensure the response is split by '---a2ui_JSON---' and the JSON part is well-formed. "
            f"Please retry the original request: '{original_query}'"
        )

    async def stream(self, query: str, session_id: str) -> AsyncIterable[dict[str, Any]]:
        session = await self._runner.session_service.get_session(
            app_name=self._agent.name,
            user_id=self._user_id,
            session_id=session_id,
        )
        if session is None:
            session = await self._runner.session_service.create_session(
                app_name=self._agent.name,
                user_id=self._user_id,
                state={"base_url": self.base_url},
                session_id=session_id,
            )
        elif "base_url" not in session.state:
            session.state["base_url"] = self.base_url

        if self.use_ui and self.a2ui_schema_object is None:
            yield {
                "is_task_complete": True,
                "content": "I'm sorry, there is an internal UI schema configuration error.",
            }
            return

        attempt = 0
        current_query_text = query
        while attempt <= self.max_retries:
            attempt += 1
            current_message = types.Content(
                role="user", parts=[types.Part.from_text(text=current_query_text)]
            )
            final_response_content = None

            async for event in self._runner.run_async(
                user_id=self._user_id,
                session_id=session.id,
                new_message=current_message,
            ):
                if event.is_final_response():
                    if event.content and event.content.parts and event.content.parts[0].text:
                        final_response_content = "\n".join(
                            [part.text for part in event.content.parts if part.text]
                        )
                    break

                yield {
                    "is_task_complete": False,
                    "updates": self.get_processing_message(),
                }

            if final_response_content is None:
                if attempt <= self.max_retries:
                    current_query_text = (
                        "I received no response. Please try again. "
                        f"Please retry the original request: '{query}'"
                    )
                    continue
                final_response_content = "I'm sorry, I couldn't process your request."

            is_valid = False
            error_message = ""

            if self.use_ui:
                try:
                    if "---a2ui_JSON---" not in final_response_content:
                        raise ValueError("Delimiter '---a2ui_JSON---' not found.")

                    _text_part, json_string = final_response_content.split("---a2ui_JSON---", 1)
                    json_string_cleaned = (
                        json_string.strip().lstrip("```json").rstrip("```").strip()
                    )

                    if not json_string_cleaned:
                        if self.allow_empty_json:
                            is_valid = True
                        else:
                            raise ValueError("JSON part is empty.")
                    else:
                        parsed_json_data = json.loads(json_string_cleaned)
                        jsonschema.validate(
                            instance=parsed_json_data,
                            schema=self.a2ui_schema_object,
                        )
                        is_valid = True
                except (
                    ValueError,
                    json.JSONDecodeError,
                    jsonschema.exceptions.ValidationError,
                ) as exc:
                    error_message = f"Validation failed: {exc}."
                    logger.warning("A2UI validation failed: %s", exc)
            else:
                is_valid = True

            if is_valid:
                yield {"is_task_complete": True, "content": final_response_content}
                return

            if attempt <= self.max_retries:
                current_query_text = self._build_retry_prompt(query, error_message)

        yield {
            "is_task_complete": True,
            "content": "I'm sorry, I'm having trouble generating the interface right now.",
        }
