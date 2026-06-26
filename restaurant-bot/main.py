import asyncio
import streamlit as st

from dotenv import load_dotenv
from agents import (
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
    Runner,
    SQLiteSession,
)
from config import is_debug_mode
from openai import OpenAI
from restaurant_agents.triage_agent import triage_agent

load_dotenv()

client = OpenAI()

if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "chat-history",
        "chat-gpt-clone-memory.db",
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
                        st.write(message["content"][0]["text"].replace("$", "\\$"))


asyncio.run(paint_history())


async def run_agent(message):
    agent = triage_agent

    with st.chat_message("ai"):
        handoff_placeholder = st.empty()
        text_placeholder = st.empty()
        response = ""

        st.session_state["handoff_placeholder"] = handoff_placeholder
        st.session_state["text_placeholder"] = text_placeholder

        try:

            stream = Runner.run_streamed(
                agent,
                message,
                session=session,
            )

            async for event in stream.stream_events():
                if event.type == "raw_response_event":

                    if event.data.type == "response.output_text.delta":
                        response += event.data.delta
                        text_placeholder.write(response)

        except InputGuardrailTripwireTriggered:
            text_placeholder.empty()
            st.warning(
                "레스토랑 관련 문의만 도와드릴 수 있습니다. "
                "메뉴, 주문, 예약, 불만 접수와 관련된 내용을 입력해 주세요."
            )

        except OutputGuardrailTripwireTriggered:
            text_placeholder.empty()
            st.warning(
                "응답을 안전하게 제공할 수 없어 요청을 완료하지 못했습니다. "
                "다시 말씀해 주시면 다른 방식으로 도와드리겠습니다."
            )



prompt = st.chat_input(
    "Write a message for your assistant",
)

if prompt:

    if "handoff_placeholder" in st.session_state:
        st.session_state["handoff_placeholder"].empty()

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

    if is_debug_mode():
        st.write(asyncio.run(session.get_items()))
