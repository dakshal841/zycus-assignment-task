from pydantic import BaseModel, Field
from typing import Optional, List

class TicketInput(BaseModel):
    subject: str
    body: str

class TicketTriageResult(BaseModel):
    product_area: str = Field(description="The primary product area the issue belongs to (e.g., Data Ingestion, Billing).")
    issue_category: str = Field(description="The specific category of the issue.")
    urgency: str = Field(description="Urgency tier: must be exactly P1, P2, P3, or P4.")
    reasoning: str = Field(description="Brief justification for the assigned urgency tier.")
    matched_kb_doc: Optional[str] = Field(description="Filename or title of the relevant knowledge base document, if any. Return null if none match.")
    recommended_team: str = Field(description="The suggested internal team to handle the ticket (e.g., Tier-1 Support, Billing Team).")
    draft_response: str = Field(description="A professional first-response message draft for the customer.")

class RiskFlag(BaseModel):
    risk_type: str = Field(description="Type of risk, e.g., 'Churn Signal', 'Unresolved Escalation', 'Low Usage'")
    description: str = Field(description="Explanation of the risk and potential business impact.")
    justification_quote: str = Field(description="Direct verbatim quote from a customer ticket supporting this flag.")
    ticket_id: str = Field(description="The ID of the ticket the quote came from (e.g., TKT-10000).")

class TAMAccountBrief(BaseModel):
    account_id: str
    company_name: str
    executive_summary: str = Field(description="A concise 3-5 sentence summary of account context, relationship health, and recent trends.")
    open_risks: List[RiskFlag] = Field(description="List of identified risks with direct ticket quotes.")
    talking_points: List[str] = Field(description="3 to 4 actionable talking points or strategic recommendations for the TAM during the next check-in.")