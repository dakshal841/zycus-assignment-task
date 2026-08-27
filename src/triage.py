import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv, find_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from src.schemas import TicketTriageResult, TicketInput, TAMAccountBrief
from src.rag import retrieve_relevant_kb
from src.summarizer import generate_tam_brief

load_dotenv(find_dotenv())
app = FastAPI(title="Ticket Triage Agent")

# Initialize Groq LLM and bind the Pydantic schema
llm = ChatGroq(
    model="openai/gpt-oss-20b", 
    temperature=0.1, 
    api_key=os.getenv("GROQ_API_KEY")
)
structured_llm = llm.with_structured_output(TicketTriageResult)

SYSTEM_PROMPT = """
You are an expert Technical Support Triage Agent.
Your job is to analyze incoming support tickets and output structured JSON.

Rules for Urgency Tier:
- P1: Total system outage, severe data loss, or high churn risk.
- P2: Core feature broken for multiple users, no immediate workaround.
- P3: Minor bug, intermittent issue, or valid workaround exists.
- P4: Feature request, general inquiry, or billing question.

Draft a polite first response and recommend an internal handling team.
"""

def triage_ticket(ticket: TicketInput) -> TicketTriageResult:
    kb_context = retrieve_relevant_kb(f"{ticket.subject}\n{ticket.body}")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "SUBJECT: {subject}\nBODY: {body}\n\nKB MATCH:\n{kb_context}")
    ])
    
    chain = prompt | structured_llm
    return chain.invoke({
        "subject": ticket.subject,
        "body": ticket.body,
        "kb_context": kb_context
    })

@app.post("/triage", response_model=TicketTriageResult)
async def api_triage_ticket(ticket: TicketInput):
    try:
        return triage_ticket(ticket)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tam/brief/{account_id}", response_model=TAMAccountBrief)
async def api_tam_brief(account_id: str):
    """Generates an actionable account brief with direct quote justifications for TAMs."""
    try:
        brief = generate_tam_brief(account_id)
        return brief
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))