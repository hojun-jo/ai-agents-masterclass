from pydantic import BaseModel


class HandoffData(BaseModel):

    to_agent_name: str
    issue_type: str
    issue_description: str
    reason: str
