from pydantic import BaseModel


class HandoffData(BaseModel):

    to_agent_name: str
    issue_type: str
    issue_description: str
    reason: str


class InputGuardRailOutput(BaseModel):

    is_off_topic: bool
    has_inappropriate_language: bool
    reason: str


class OutputGuardRailOutput(BaseModel):

    is_professional_and_polite: bool
    contains_internal_information: bool
    reason: str
