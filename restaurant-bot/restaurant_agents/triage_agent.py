from agents import Agent, RunContextWrapper, handoff
import streamlit as st

from models import HandoffData
from .order_agent import order_agent
from .menu_agent import menu_agent
from .reservation_agent import reservation_agent


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

    Operating principles:
    - Summarize the customer's intent in one sentence before deciding where to route them.
    - If a request mixes multiple intents, route based on the customer's most immediate goal.
    - If the customer asks about a menu item while trying to order, decide whether they mainly need menu information or order handling right now.
    - If reservation and order requests appear together, briefly confirm which one the customer wants to handle first.
    - If the request is outside the supported scope, explain that clearly and route to the closest appropriate agent when possible.

    Handoff payload rules:
    - to_agent_name: use the exact destination agent name
    - issue_type: use one of menu_question, order_request, reservation_request
    - issue_description: provide a short summary of the customer's request and any details already confirmed
    - reason: explain in one sentence why this agent is the correct destination

    Response style:
    - Be short and clear.
    - Do not make unnecessary assumptions.
    - Ask for missing information one item at a time.
    """


def handle_handoff(
    wrapper: RunContextWrapper,
    input_data: HandoffData,
):
    with st.status(f"{input_data.to_agent_name}에게 연결합니다..."):
        st.write(f"{input_data.to_agent_name}에게 연결합니다...")

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
        make_handoff(reservation_agent),
        make_handoff(menu_agent),
        make_handoff(order_agent),
    ],
)
