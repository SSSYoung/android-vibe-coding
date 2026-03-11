import json
import logging
from datetime import datetime
from pathlib import Path

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import DataPart, Part, Task, TaskState, TextPart, UnsupportedOperationError
from a2a.utils import new_agent_parts_message, new_agent_text_message, new_task
from a2a.utils.errors import ServerError
from a2ui.extension.a2ui_extension import create_a2ui_part, try_activate_a2ui_extension

logger = logging.getLogger(__name__)


class SimpleA2uiAgentExecutor(AgentExecutor):
    """Shared executor flow for samples that return text and A2UI JSON."""

    def __init__(self, ui_agent, text_agent, raw_log_filename: str | None = None, raw_log_dir: str | None = None):
        self.ui_agent = ui_agent
        self.text_agent = text_agent
        self.raw_log_filename = raw_log_filename
        self.raw_log_dir = Path(raw_log_dir) if raw_log_dir else None

    def resolve_query_from_event(self, action: str | None, context_data: dict) -> str:
        return f"User submitted an event: {action} with data: {context_data}"

    def get_final_state(self, action: str | None) -> TaskState:
        return TaskState.input_required

    def _write_raw_content_log(self, content: str) -> None:
        if not self.raw_log_filename:
            return
        try:
            log_dir = self.raw_log_dir or Path.cwd()
            log_path = log_dir / self.raw_log_filename
            with log_path.open("a", encoding="utf-8") as fp:
                fp.write(f"\n--- {datetime.utcnow().isoformat()}Z ---\n")
                fp.write(content)
                fp.write("\n")
            logger.info("Raw LLM response written to %s", log_path)
        except Exception as exc:
            logger.warning("Failed to write raw LLM response: %s", exc)

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        query = ""
        ui_event_part = None
        action = None

        use_ui = try_activate_a2ui_extension(context)
        agent = self.ui_agent if use_ui else self.text_agent

        if context.message and context.message.parts:
            for part in context.message.parts:
                if isinstance(part.root, DataPart) and "userAction" in part.root.data:
                    ui_event_part = part.root.data["userAction"]

        if ui_event_part:
            action = ui_event_part.get("name") or ui_event_part.get("actionName")
            query = self.resolve_query_from_event(action, ui_event_part.get("context", {}))
        else:
            query = context.get_user_input()

        task = context.current_task
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.context_id)

        async for item in agent.stream(query, task.context_id):
            if not item["is_task_complete"]:
                await updater.update_status(
                    TaskState.working,
                    new_agent_text_message(item["updates"], task.context_id, task.id),
                )
                continue

            final_state = self.get_final_state(action)
            content = item["content"]
            self._write_raw_content_log(content)

            final_parts: list[Part] = []
            if "---a2ui_JSON---" in content:
                text_content, json_string = content.split("---a2ui_JSON---", 1)
                if text_content.strip():
                    final_parts.append(Part(root=TextPart(text=text_content.strip())))

                if json_string.strip():
                    try:
                        json_string_cleaned = (
                            json_string.strip().lstrip("```json").rstrip("```").strip()
                        )
                        logger.info("Raw A2UI JSON (cleaned): %s", json_string_cleaned[:2000])
                        json_data = json.loads(json_string_cleaned)
                        if isinstance(json_data, list):
                            for message in json_data:
                                final_parts.append(create_a2ui_part(message))
                        else:
                            final_parts.append(create_a2ui_part(json_data))
                    except json.JSONDecodeError as exc:
                        logger.error("Failed to parse UI JSON: %s", exc)
                        final_parts.append(Part(root=TextPart(text=json_string)))
            else:
                final_parts.append(Part(root=TextPart(text=content.strip())))

            await updater.update_status(
                final_state,
                new_agent_parts_message(final_parts, task.context_id, task.id),
                final=(final_state == TaskState.completed),
            )
            break

    async def cancel(self, request: RequestContext, event_queue: EventQueue) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())
