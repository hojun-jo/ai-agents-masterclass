import logging

from google.genai import types
from google.adk.agents import Agent, ParallelAgent
from google.adk.models.lite_llm import LiteLlm
from .prompt import ILLUSTRATOR_DESCRIPTION, build_illustrator_prompt
from .tools import generate_scene_image

MODEL = LiteLlm(model="openai/gpt-4o")
logger = logging.getLogger(__name__)
TOOL_ONLY_CONFIG = types.GenerateContentConfig(
    tool_config=types.ToolConfig(
        function_calling_config=types.FunctionCallingConfig(
            mode=types.FunctionCallingConfigMode.ANY,
            allowed_function_names=["generate_scene_image"],
        )
    )
)


def build_scene_logger(scene_id: int):
    def log_scene_start(callback_context):
        logger.info(f"장면 {scene_id} 생성 중...")
        return None

    return log_scene_start


def build_scene_agent(scene_id: int) -> Agent:
    return Agent(
        name=f"IllustratorScene{scene_id}Agent",
        description=ILLUSTRATOR_DESCRIPTION,
        model=MODEL,
        mode="single_turn",
        instruction=build_illustrator_prompt(scene_id),
        generate_content_config=TOOL_ONLY_CONFIG,
        tools=[generate_scene_image],
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
