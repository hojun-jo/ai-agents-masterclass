import base64
import re
import asyncio
from google.genai import types
from openai import OpenAI
from google.adk.tools.tool_context import ToolContext

client = OpenAI()


def sanitize_illustration_prompt(text: str) -> str:
    replacements = {
        "child": "storybook character",
        "children": "storybook characters",
        "kid": "storybook character",
        "baby": "storybook character",
        "scared": "surprised",
        "terrified": "surprised",
        "crying": "teary-eyed",
        "injured": "tired",
        "hurt": "upset",
        "blood": "",
        "bloody": "",
        "wound": "",
        "weapon": "",
        "knife": "",
        "gun": "",
        "attack": "",
        "fight": "",
        "dead": "still",
        "naked": "fully clothed",
    }

    sanitized = text.strip()
    for source, target in replacements.items():
        sanitized = re.sub(
            rf"\b{re.escape(source)}\b",
            target,
            sanitized,
            flags=re.IGNORECASE,
        )

    sanitized = re.sub(r"\s+", " ", sanitized).strip(" ,.")

    return (
        "Soft watercolor storybook illustration. "
        "Gentle, non-violent scene. Fully clothed characters. "
        "Warm mood. Consistent character design across pages. "
        f"{sanitized}"
    )[:1500]


async def generate_scene_image(tool_context: ToolContext, scene_id: int):
    story_writer_output = tool_context.state.get("story_writer_output") or {}
    title = story_writer_output.get("title") or ""
    prompt_builder_output = tool_context.state.get("prompt_builder_output") or {}
    optimized_prompts = prompt_builder_output.get("optimized_prompts") or []

    if not optimized_prompts or not title:
        return {
            "status": "no_prompts",
            "scene_id": scene_id,
        }

    existing_artifacts = await tool_context.list_artifacts()
    prompt = next(
        (item for item in optimized_prompts if item.get("scene_id") == scene_id),
        None,
    )

    if not prompt:
        return {
            "status": "scene_not_found",
            "scene_id": scene_id,
        }

    enhanced_prompt = (prompt.get("enhanced_prompt") or "").strip()
    if not enhanced_prompt:
        return {
            "status": "invalid_prompt",
            "scene_id": scene_id,
        }

    safe_prompt = sanitize_illustration_prompt(enhanced_prompt)
    filename = f"{title}_{scene_id}_image.jpeg"

    if filename in existing_artifacts:
        return {
            "status": "already_exists",
            "scene_id": scene_id,
            "filename": filename,
            "prompt": safe_prompt[:100],
        }

    try:
        image = await asyncio.to_thread(
            client.images.generate,
            model="gpt-image-1.5",
            prompt=safe_prompt,
            n=1,
            quality="low",
            moderation="low",
            output_format="jpeg",
            background="opaque",
            size="1024x1024",
        )
    except Exception as exc:
        return {
            "status": "generation_failed",
            "scene_id": scene_id,
            "error": str(exc),
        }

    try:
        image_bytes = base64.b64decode(image.data[0].b64_json)
    except Exception as exc:
        return {
            "status": "decode_failed",
            "scene_id": scene_id,
            "error": str(exc),
        }

    artifact = types.Part(
        inline_data=types.Blob(
            mime_type="image/jpeg",
            data=image_bytes,
        )
    )

    await tool_context.save_artifact(
        filename=filename,
        artifact=artifact,
    )

    return {
        "status": "complete",
        "scene_id": scene_id,
        "filename": filename,
        "prompt": safe_prompt[:100],
    }
