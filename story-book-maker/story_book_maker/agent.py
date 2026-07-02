from google.adk.agents import Agent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from .sub_agents.illustrator_agent.agent import parallel_illustrator_agent
from .sub_agents.prompt_builder.agent import prompt_builder_agent
from .prompt import STORY_WRITER_DESCRIPTION, STORY_WRITER_PROMPT
from pydantic import BaseModel, Field

MODEL = LiteLlm(model="openai/gpt-4o")


class SceneDescription(BaseModel):
    scene_id: int = Field(description="Page number from 1 to 5")
    scene_text: str = Field(
        description="Short children's story text for that page",
    )
    scene_description: str = Field(
        description="Original visual scene description for the page, to be rewritten into a safer image prompt later",
    )


class StoryWriterOutput(BaseModel):
    scene_descriptions: list[SceneDescription] = Field(
        description="Ordered list of the 5 story pages with text and illustration descriptions",
    )


story_wirter_agent = Agent(
    name="StoryWriterAgent",
    model=MODEL,
    description=STORY_WRITER_DESCRIPTION,
    instruction=STORY_WRITER_PROMPT,
    output_schema=StoryWriterOutput,
    output_key="story_writer_output",
)


root_agent = SequentialAgent(
    name="StoryBookMaker",
    sub_agents=[
        story_wirter_agent,
        prompt_builder_agent,
        parallel_illustrator_agent,
    ],
)
