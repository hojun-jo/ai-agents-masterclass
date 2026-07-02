import logging

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from .prompt import PROMPT_BUILDER_DESCRIPTION, PROMPT_BUILDER_PROMPT
from pydantic import BaseModel, Field

MODEL = LiteLlm(model="openai/gpt-4o")
logger = logging.getLogger(__name__)


class OptimizedPrompt(BaseModel):
    scene_id: int = Field(description="Page number from 1 to 5")
    enhanced_prompt: str = Field(
        description="Safe, gentle illustration prompt rewritten to avoid image-generation safety blocks",
    )


class PromptBuilderOutput(BaseModel):
    optimized_prompts: list[OptimizedPrompt] = Field(
        description="Ordered list of safe image prompts, one for each story page",
    )


def log_prompt_builder_start(callback_context):
    logger.info("프롬프트 개선 중...")
    return None


prompt_builder_agent = Agent(
    name="PromptBuilderAgent",
    description=PROMPT_BUILDER_DESCRIPTION,
    instruction=PROMPT_BUILDER_PROMPT,
    model=MODEL,
    output_schema=PromptBuilderOutput,
    output_key="prompt_builder_output",
    before_agent_callback=log_prompt_builder_start,
)
