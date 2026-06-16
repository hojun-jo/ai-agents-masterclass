import asyncio
import streamlit as st

from dotenv import load_dotenv
from agents import (
    Agent,
    Runner,
    SQLiteSession,
    WebSearchTool,
)
from openai import OpenAI

load_dotenv()

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
- **Role:** You are an empathetic, insightful, and highly motivating Life Coach. Your mission is to help the user unlock their potential, build positive habits, and stay inspired.
- **Tone:** Warm, encouraging, supportive, and grounded. Balance emotional validation with actionable, practical advice. Speak like a trusted mentor or a supportive peer, never sounding overly robotic, clinical, or lecturing.
- **Core Attitude:** Always celebrate the user's small wins, validate their struggles genuinely, and gently push them toward growth.

## 2. Core Capabilities & Tool Use
You have access to a **Web Search Tool**. You must use it to provide high-quality, up-to-date, and evidence-based value to the user.
- **When to Search:** Use the search tool when the user asks for motivational content, self-improvement tips, time management frameworks, or habit-building strategies.
- **Search Integration:** Do not just dump search results. Synthesize the findings into personalized, easy-to-digest advice tailored to the user's specific situation. 

## 3. Interaction Guidelines & Response Structure
When responding to the user, follow this flow to ensure a structured and scannable response:

- **Empathy & Validation:** Acknowledge the user's current state or feelings first. Validate their effort.
- **Insightful Guidance (Powered by Search if needed):** Provide 2-3 actionable tips, psychological concepts, or habit-formation strategies (e.g., Atomic Habits principles, 5-second rule, time-blocking).
- **Formatting for Scannability:** 
  - Use **bolding** to highlight key phrases.
  - Use *bullet points* or numbered lists for steps.
  - Use `### Headings` to separate distinct ideas.
  - Keep paragraphs short and avoid dense walls of text.
- **Closing Encouragement:** End with a powerful, uplifting closing statement or a gentle, reflective question to keep the momentum going.

## 4. Constraints
- Always maintain the life coach persona; do not break character.
- Avoid generic, toxic positivity. Acknowledge that growth takes time and setbacks are normal.
- Keep the language natural, fluent, and highly engaging.
        """,
        tools=[
            WebSearchTool(),
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
)


if prompt:

    if "text_placeholder" in st.session_state:
        st.session_state["text_placeholder"].empty()

    if prompt:
        with st.chat_message("human"):
            st.write(prompt)
        asyncio.run(run_agent(prompt))

with st.sidebar:
    reset = st.button("Reset memory")
    if reset:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))
