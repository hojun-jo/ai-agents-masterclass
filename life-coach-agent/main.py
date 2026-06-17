import asyncio
import os
import streamlit as st

from dotenv import load_dotenv
from agents import (
    Agent,
    Runner,
    SQLiteSession,
    WebSearchTool,
    FileSearchTool,
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


async def paint_history():
    messages = await session.get_items()

    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    content = message["content"]
                    if isinstance(content, str):
                        st.write(content)
                else:
                    if message["type"] == "message":
                        st.write(message["content"][0]["text"].replace("$", "\$"))
        if "type" in message:
            message_type = message["type"]
            if message_type == "web_search_call":
                with st.chat_message("ai"):
                    st.write("🔍 Searched the web...")
            elif message_type == "file_search_call":
                with st.chat_message("ai"):
                    st.write("📁 Searched your files...")


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
You have access to a **Web Search Tool**, a **File Search Tool**, and the user's prior conversation history.

- Use **File Search** to find and reference the user's uploaded goal documents, plans, and reflections when giving advice.
- Use **Web Search** for every piece of advice or recommendation you give.
- Every coaching response that includes advice or recommendations must be grounded in web search findings.
- When uploaded goals are available, base your coaching on those goals and combine them with web findings to provide personalized recommendations tied to the user's goals, challenges, habits, and progress.
- Reference prior conversations when helpful to compare progress over time.
- Do not dump tool results. Synthesize them into practical coaching.

## 3. Response Style
- Start with empathy and validation.
- Ground advice in the user's uploaded goals or prior history when available.
- If uploaded goals are available and web search is useful, explicitly connect the outside guidance back to the user's stated goals before giving recommendations.
- Mention progress, setbacks, or patterns over time when relevant.
- Give 2-3 actionable recommendations.
- Use short paragraphs, clear bullets or numbered lists, and brief headings when helpful.
- End with encouraging momentum or one reflective question.

## 4. Constraints
- Do not give generic coaching when the user's uploaded goals or history provide better context.
- Do not pretend to have found files or past history if none are available.
- Avoid toxic positivity. Acknowledge that growth takes time and setbacks are normal.
        """,
        tools=[
            WebSearchTool(),
            FileSearchTool(
                vector_store_ids=[VECTOR_STORE_ID],
                max_num_results=3,
            ),
        ],
    )

    with st.chat_message("ai"):
        status_container = st.status("⏳", expanded=False)
        text_placeholder = st.empty()
        response = ""

        st.session_state["text_placeholder"] = text_placeholder

        stream = Runner.run_streamed(
            agent,
            message,
            session=session,
        )

        async for event in stream.stream_events():
            if event.type == "raw_response_event":

                update_status(status_container, event.data.type)

                if event.data.type == "response.output_text.delta":
                    response += event.data.delta
                    text_placeholder.write(response)


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

    for file in prompt.files:
        if file.type.startswith("text/"):
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
