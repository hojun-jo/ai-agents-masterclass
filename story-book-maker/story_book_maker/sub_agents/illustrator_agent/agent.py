import logging
from typing import AsyncGenerator

from google.adk.agents import BaseAgent, ParallelAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events.event import Event
from google.adk.tools.tool_context import ToolContext
from .tools import generate_scene_image

logger = logging.getLogger(__name__)
ILLUSTRATOR_DESCRIPTION = "Generates the image for one assigned scene."


def build_scene_logger(scene_id: int):
    def log_scene_start(callback_context):
        logger.info(f"장면 {scene_id} 생성 중...")
        return None

    return log_scene_start


class IllustratorSceneAgent(BaseAgent):
    scene_id: int

    async def _run_async_impl(
        self,
        ctx: InvocationContext,
    ) -> AsyncGenerator[Event, None]:
        tool_context = ToolContext(ctx)
        result = await generate_scene_image(tool_context, self.scene_id)

        yield Event(
            invocation_id=ctx.invocation_id,
            author=self.name,
            branch=ctx.branch,
            actions=tool_context._event_actions,
        )

        if result.get("status") not in {"complete", "already_exists"}:
            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                branch=ctx.branch,
                content={
                    "role": "model",
                    "parts": [
                        {
                            "text": (
                                f"Failed to generate scene {self.scene_id}: "
                                f"{result.get('status')}"
                            )
                        }
                    ],
                },
            )


def build_scene_agent(scene_id: int) -> IllustratorSceneAgent:
    return IllustratorSceneAgent(
        name=f"IllustratorScene{scene_id}Agent",
        description=ILLUSTRATOR_DESCRIPTION,
        scene_id=scene_id,
        before_agent_callback=build_scene_logger(scene_id),
    )


scene_1_agent = build_scene_agent(1)
scene_2_agent = build_scene_agent(2)
scene_3_agent = build_scene_agent(3)
scene_4_agent = build_scene_agent(4)
scene_5_agent = build_scene_agent(5)


parallel_illustrator_agent = ParallelAgent(
    name="ParallelIllustratorAgent",
    sub_agents=[
        scene_1_agent,
        scene_2_agent,
        scene_3_agent,
        scene_4_agent,
        scene_5_agent,
    ],
)
