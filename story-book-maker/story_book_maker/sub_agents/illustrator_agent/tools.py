import base64
import re
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


async def generate_images(tool_context: ToolContext):
    prompt_builder_output = tool_context.state.get("prompt_builder_output") or {}
    optimized_prompts = prompt_builder_output.get("optimized_prompts") or []

    if not optimized_prompts:
        return {
            "total_images": 0,
            "generated_images": [],
            "status": "no_prompts",
        }

    existing_artifacts = await tool_context.list_artifacts()

    generated_images = []

    for prompt in optimized_prompts:
        scene_id = prompt.get("scene_id")
        enhanced_prompt = prompt.get("enhanced_prompt")
        safe_prompt = sanitize_illustration_prompt(enhanced_prompt)
        filename = f"scene_{scene_id}_image.jpeg"

        if filename in existing_artifacts:
            generated_images.append(
                {
                    "scene_id": scene_id,
                    "prompt": safe_prompt[:100],
                    "filename": filename,
                }
            )
            continue

        image = client.images.generate(
            model="gpt-image-1.5",
            prompt=safe_prompt,
            n=1,
            quality="low",
            moderation="low",
            output_format="jpeg",
            background="opaque",
            size="1024x1024",
        )

        image_bytes = base64.b64decode(image.data[0].b64_json)

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

        generated_images.append(
            {
                "scene_id": scene_id,
                "prompt": safe_prompt[:100],
                "filename": filename,
            }
        )

    return {
        "total_images": len(generated_images),
        "generated_images": generated_images,
        "status": "complete",
    }
