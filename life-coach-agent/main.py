import asyncio
import os
import streamlit as st
import base64

from dotenv import load_dotenv
from agents import (
    Agent,
    RunConfig,
    Runner,
    SQLiteSession,
    WebSearchTool,
    FileSearchTool,
    ImageGenerationTool,
)
from openai import OpenAI

load_dotenv()

VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")

client = OpenAI()

if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "chat-history",
        "chat-memory.db",
    )
session = st.session_state["session"]


def exclude_image_generation_calls(history, new_items):
    filtered_history = [
        item
        for item in history
        if not (
            isinstance(item, dict)
            and item.get("type") == "image_generation_call"
        )
    ]
    sanitized_history = []
    for item in filtered_history:
        if not (
            isinstance(item, dict)
            and item.get("type") == "message"
            and item.get("role") == "assistant"
        ):
            sanitized_history.append(item)
            continue

        sanitized_item = dict(item)
        content = sanitized_item.get("content")
        if isinstance(content, list):
            sanitized_content = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "output_text":
                    sanitized_part = dict(part)
                    sanitized_part.pop("annotations", None)
                    sanitized_content.append(sanitized_part)
                else:
                    sanitized_content.append(part)
            sanitized_item["content"] = sanitized_content
        sanitized_history.append(sanitized_item)
    return sanitized_history + new_items


async def paint_history():
    messages = await session.get_items()

    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    content = message["content"]
                    if isinstance(content, str):
                        st.write(content)
                    elif isinstance(content, list):
                        for part in content:
                            if "image_url" in part:
                                st.write(part["image_url"])
                else:
                    if message["type"] == "message":
                        st.write(message["content"][0]["text"].replace("$", "\\$"))
        if "type" in message:
            message_type = message["type"]
            if message_type == "web_search_call":
                with st.chat_message("ai"):
                    st.write("🔍 Searched the web...")
            elif message_type == "file_search_call":
                with st.chat_message("ai"):
                    st.write("📁 Searched your files...")
            elif message_type == "image_generation_call":
                image = base64.b64decode(message["result"])
                with st.chat_message("ai"):
                    st.image(image)


asyncio.run(paint_history())


def update_status(status_container, event):
    status_messages = {
        "response.web_search_call.completed": (
            "✅ Web search completed.",
            "complete",
        ),
        "response.web_search_call.in_progress": (
            "🔍 Starting web search...",
            "running",
        ),
        "response.web_search_call.searching": (
            "🔍 Web search in progress...",
            "running",
        ),
        "response.completed": ("", "complete"),
        "response.file_search_call.completed": (
            "✅ File search completed.",
            "complete",
        ),
        "response.file_search_call.in_progress": (
            "📁 Starting file search...",
            "running",
        ),
        "response.file_search_call.searching": (
            "📁 File search in progress...",
            "running",
        ),
        "response.image_generation_call.generating": (
            "🎨 Drawing image...",
            "running",
        ),
        "response.image_generation_call.in_progress": (
            "🎨 Drawing image...",
            "running",
        ),
    }

    if event in status_messages:
        label, state = status_messages[event]
        status_container.update(label=label, state=state)


status = st.status


async def run_agent(message):

    agent = Agent(
        name="LifeCoach",
        instructions="""
# System Prompt: Empathetic & Motivating Life Coach Agent

## 1. Persona & Tone
- You are an empathetic, insightful, and motivating Life Coach.
- Be warm, encouraging, practical, and grounded.
- Validate the user's effort, celebrate small wins, and gently push toward growth.

## 2. Tool Use
You have access to a **Web Search Tool**, a **File Search Tool**, an **Image Generation Tool**, and the user's prior conversation history.

- Use **File Search** to find and reference the user's uploaded goal documents, plans, and reflections when giving advice.
- You must use **Web Search** before giving any advice, tip, recommendation, motivational guidance, or encouragement.
- Advice, tips, recommendations, and motivational encouragement are never allowed to rely only on your built-in knowledge or intuition.
- Every coaching response that includes advice, tips, recommendations, or motivational encouragement must explicitly be grounded in web search findings from the current turn.
- When uploaded goals are available, base your coaching on those goals and combine them with web findings to provide personalized recommendations tied to the user's goals, challenges, habits, and progress.
- Reference prior conversations when helpful to compare progress over time.
- Do not dump tool results. Synthesize them into practical coaching.

## 3. Multi-Tool Workflow
- Use the tools together naturally when it helps the user: search the user's files for goals and plans, use web search for grounded guidance or inspiration, then generate an image when a visual artifact would help.
- If the user asks for a vision board, motivational poster, celebration image, or visual progress summary, you should normally create an image instead of only describing it.
- You can generate images for at least these use cases:
  1. Goal-based vision boards.
  2. Motivational posters with a customized message.
  3. Visual representations of progress, milestones, streaks, or achievements.
- For vision boards and personalized progress visuals, search the user's uploaded files first when relevant so the image reflects their actual goals.
- For motivational posters and celebration images, personalize the text using the user's stated achievement, goal, or challenge.
- When useful, use web search before image generation to gather timely ideas, examples, or evidence-based framing, then turn that into a concrete image prompt.
- Before generating the image, briefly tell the user what you found or what theme you are using.
- The final user-facing response should feel like one seamless coaching interaction, not a list of separate tool outputs.

## 4. Response Style
- Start with empathy and validation.
- Ground advice in the user's uploaded goals or prior history when available.
- If the user asks for advice, tips, or motivation, do the web search first and only then answer.
- Ground tips and motivational encouragement in web search findings, not just general intuition.
- If uploaded goals are available and web search is useful, explicitly connect the outside guidance back to the user's stated goals before giving recommendations.
- Mention progress, setbacks, or patterns over time when relevant.
- Give 2-3 actionable recommendations when the user is asking for coaching.
- If the user is primarily asking for an image, keep the text concise and supportive, then generate the image.
- Use short paragraphs, clear bullets or numbered lists, and brief headings when helpful.
- End with encouraging momentum or one reflective question when appropriate.

## 5. Constraints
- Do not give generic coaching when the user's uploaded goals or history provide better context.
- Do not pretend to have found files or past history if none are available.
- Avoid toxic positivity. Acknowledge that growth takes time and setbacks are normal.
- Do not claim to have generated an image unless you actually call the image generation tool.
- Do not answer advice, tip, or motivation requests without first calling the web search tool.
        """,
        tools=[
            WebSearchTool(),
            FileSearchTool(
                vector_store_ids=[VECTOR_STORE_ID],
                max_num_results=3,
            ),
            ImageGenerationTool(
                tool_config={
                    "type": "image_generation",
                    "quality": "low",
                    "output_format": "jpeg",
                    "moderation": "low",
                    "partial_images": 1,
                }
            ),
        ],
    )

    with st.chat_message("ai"):
        status_container = st.status("⏳", expanded=False)
        text_placeholder = st.empty()
        image_placeholder = st.empty()
        response = ""

        st.session_state["text_placeholder"] = text_placeholder
        st.session_state["image_placeholder"] = image_placeholder

        stream = Runner.run_streamed(
            agent,
            message,
            session=session,
            run_config=RunConfig(
                session_input_callback=exclude_image_generation_calls,
            ),
        )

        async for event in stream.stream_events():
            if event.type == "raw_response_event":

                update_status(status_container, event.data.type)

                if event.data.type == "response.output_text.delta":
                    response += event.data.delta
                    text_placeholder.write(response)

                elif (
                    event.data.type
                    == "response.image_generation_call.partial_image"
                ):
                    image = base64.b64decode(event.data.partial_image_b64)
                    image_placeholder.image(image)


prompt = st.chat_input(
    "Write a message for your assistant",
    accept_file=True,
    file_type=[
        "txt",
        "pdf",
    ],
)


if prompt:

    if "text_placeholder" in st.session_state:
        st.session_state["text_placeholder"].empty()
    if "image_placeholder" in st.session_state:
        st.session_state["image_placeholder"].empty()

    for file in prompt.files:
        if file.type.startswith("text/") or file.type == "application/pdf":
            with st.chat_message("ai"):
                with st.status("⏳ Uploading file...") as status:
                    uploaded_file = client.files.create(
                        file=(file.name, file.getvalue()),
                        purpose="user_data",
                    )
                    status.update(label="⏳ Attaching file...")
                    client.vector_stores.files.create(
                        vector_store_id=VECTOR_STORE_ID,
                        file_id=uploaded_file.id,
                    )
                    status.update(label="✅ File uploaded", state="complete")

    if prompt.text:
        with st.chat_message("human"):
            st.write(prompt.text)
        asyncio.run(run_agent(prompt.text))

with st.sidebar:
    reset = st.button("Reset memory")
    if reset:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))
