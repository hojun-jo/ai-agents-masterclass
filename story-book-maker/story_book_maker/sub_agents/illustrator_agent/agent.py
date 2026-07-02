from google.adk.agents import Agent, ParallelAgent
from google.adk.models.lite_llm import LiteLlm
from .prompt import ILLUSTRATOR_DESCRIPTION, build_illustrator_prompt
from .tools import generate_scene_image

MODEL = LiteLlm(model="openai/gpt-4o")


def build_scene_agent(scene_id: int) -> Agent:
    return Agent(
        name=f"IllustratorScene{scene_id}Agent",
        description=ILLUSTRATOR_DESCRIPTION,
        model=MODEL,
        instruction=build_illustrator_prompt(scene_id),
        tools=[generate_scene_image],
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
