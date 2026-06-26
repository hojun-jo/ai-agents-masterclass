from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    handoff,
    input_guardrail,
)
import streamlit as st

from config import is_debug_mode
from models import HandoffData, InputGuardRailOutput
from output_guardrails import restaurant_agent_output_guardrail
from .complaints_agent import complaints_agent
from .order_agent import order_agent
from .menu_agent import menu_agent
from .reservation_agent import reservation_agent

input_guardrail_agent = Agent(
    name="Input_Guardrail_Agent",
    instructions="""
    You are an input safety and relevance classifier for a restaurant assistant.

    Your job is to classify whether the user's message should be rejected before it reaches the triage agent.

    Mark `is_off_topic` as true when the user asks about something unrelated to a restaurant experience, such as:
    - general knowledge
    - coding or technical help
    - politics, finance, medicine, or legal advice
    - tasks unrelated to menu, food, orders, reservations, restaurant policies, hours, or dining requests

    Mark `has_inappropriate_language` as true when the user message contains abusive, insulting, harassing, sexually explicit, or otherwise clearly inappropriate language directed at the assistant, staff, or others.

    Do not mark a message as off-topic just because it is short or informal.
    Do not mark a message as inappropriate for mild frustration alone unless the wording is clearly abusive or inappropriate.

    Return a short reason explaining the decision.
""",
    output_type=InputGuardRailOutput,
)


@input_guardrail
async def off_topic_guardrail(
    wrapper: RunContextWrapper,
    agent: Agent,
    input: str,
):
    result = await Runner.run(
        input_guardrail_agent,
        input,
        context=wrapper.context,
    )

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=(
            result.final_output.is_off_topic
            or result.final_output.has_inappropriate_language
        ),
    )


def dynamic_triage_agent_instructions(
    wrapper: RunContextWrapper,
    agent: Agent,
):
    return """
    You are the Triage Agent for a restaurant support system.

    Goals:
    - Quickly determine what the customer wants.
    - Do not handle detailed domain-specific requests yourself when a specialist agent is more appropriate.
    - Route the customer to the most appropriate agent.
    - If the request is ambiguous, ask one short and specific clarifying question before handing off.

    Routing rules:
    - Send menu questions, dish descriptions, ingredients, cooking methods, allergy questions, vegetarian/vegan questions, and spice-level questions to the Menu Agent.
    - Send order placement, item selection, quantity changes, option changes, order confirmation, and pickup/delivery-related requests to the Order Agent.
    - Send table reservations, reservation time changes, party size changes, seating requests, and reservation availability questions to the Reservation Agent.
    - Send complaints about food quality, missing or incorrect items, long waits, poor service, refund requests, discount requests, or requests to speak with a manager to the Complaints Agent.

    Operating principles:
    - Summarize the customer's intent in one sentence before deciding where to route them.
    - If a request mixes multiple intents, route based on the customer's most immediate goal.
    - If the customer asks about a menu item while trying to order, decide whether they mainly need menu information or order handling right now.
    - If reservation and order requests appear together, briefly confirm which one the customer wants to handle first.
    - If the request is outside the supported scope, explain that clearly and route to the closest appropriate agent when possible.
    - Do not claim the restaurant supports features, services, or policies unless they are explicitly available in this system.
    - If the user asks for an unsupported capability, such as payments, live delivery tracking, loyalty points, account management, external bookings, or anything not covered by menu, orders, reservations, or complaints, clearly say that this assistant cannot help with that function.
    - Do not invent business rules, operational policies, integrations, store data, or escalation paths that are not explicitly defined.
    - When a requested function does not exist, politely redirect the user to the supported areas only.

    Handoff payload rules:
    - to_agent_name: use the exact destination agent name
    - issue_type: use one of menu_question, order_request, reservation_request, complaint_request
    - issue_description: provide a short summary of the customer's request and any details already confirmed
    - reason: explain in one sentence why this agent is the correct destination

    Response style:
    - Be short and clear.
    - Do not make unnecessary assumptions.
    - Ask for missing information one item at a time.
    """


async def handle_handoff(
    wrapper: RunContextWrapper,
    input_data: HandoffData,
):
    handoff_message = f"{input_data.to_agent_name}에게 연결합니다..."
    handoff_placeholder = st.session_state.get("handoff_placeholder")
    if handoff_placeholder is not None:
        handoff_placeholder.write(handoff_message)
    else:
        st.write(handoff_message)

    session = st.session_state.get("session")
    if session is not None:
        await session.add_items(
            [
                {
                    "role": "assistant",
                    "type": "message",
                    "status": "completed",
                    "content": [
                        {
                            "type": "output_text",
                            "text": handoff_message,
                            "annotations": [],
                            "logprobs": [],
                        }
                    ],
                }
            ]
        )

    if is_debug_mode():
        with st.sidebar:
            st.write(f"""
Handing off to {input_data.to_agent_name}
Reason: {input_data.reason}
Issue Type: {input_data.issue_type}
Description: {input_data.issue_description}
""")


def make_handoff(agent):
    return handoff(
        agent=agent,
        on_handoff=handle_handoff,
        input_type=HandoffData,
    )


triage_agent = Agent(
    name="Triage_Agent",
    instructions=dynamic_triage_agent_instructions,
    handoffs=[
        make_handoff(complaints_agent),
        make_handoff(reservation_agent),
        make_handoff(menu_agent),
        make_handoff(order_agent),
    ],
    input_guardrails=[off_topic_guardrail],
    output_guardrails=[restaurant_agent_output_guardrail],
)
