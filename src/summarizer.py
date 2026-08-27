import os
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv, find_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from src.schemas import TAMAccountBrief

load_dotenv(find_dotenv())

# LLM initialized with temperature=0 for deterministic outputs
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.0,
    api_key=os.getenv("GROQ_API_KEY")
)
structured_summarizer = llm.with_structured_output(TAMAccountBrief)

def load_data(data_dir: str = "data"):
    """Loads accounts and tickets from the data directory."""
    with open(os.path.join(data_dir, "accounts.json"), "r", encoding="utf-8") as f:
        accounts = json.load(f)
    with open(os.path.join(data_dir, "tickets.json"), "r", encoding="utf-8") as f:
        tickets = json.load(f)
    return accounts, tickets

def get_account_context(account_id: str, data_dir: str = "data") -> Optional[Dict[str, Any]]:
    """Filters account info and tickets within the last 90 days."""
    accounts, tickets = load_data(data_dir)
    
    # 1. Find the target account
    account = next((acc for acc in accounts if acc.get("account_id") == account_id), None)
    if not account:
        return None
        
    # 2. Filter tickets for this account
    account_tickets = [t for t in tickets if t.get("account_id") == account_id]
    
    # Sort tickets deterministically by created_at descending
    account_tickets = sorted(
        account_tickets,
        key=lambda x: x.get("created_at", ""),
        reverse=True
    )
    
    # Calculate 90-day window based on the most recent ticket date in dataset (or current date)
    if account_tickets and "created_at" in account_tickets[0]:
        try:
            # Parse reference date from the newest ticket
            newest_date_str = account_tickets[0]["created_at"].replace("Z", "+00:00")
            ref_date = datetime.fromisoformat(newest_date_str)
        except Exception:
            ref_date = datetime.now(timezone.utc)
    else:
        ref_date = datetime.now(timezone.utc)
        
    cutoff_date = ref_date - timedelta(days=90)
    
    # Filter tickets to the last 90 days
    recent_tickets = []
    for t in account_tickets:
        try:
            t_date_str = t.get("created_at", "").replace("Z", "+00:00")
            t_date = datetime.fromisoformat(t_date_str)
            if t_date >= cutoff_date:
                recent_tickets.append(t)
        except Exception:
            recent_tickets.append(t)
            
    return {
        "account": account,
        "recent_tickets": recent_tickets
    }

TAM_PROMPT = """
You are a Principal Technical Account Manager (TAM) Assistant.
Your task is to analyze the provided Account Summary and recent Support Ticket history to create a concise, high-value QBR brief.

Rules:
1. Executive Summary: Exactly 3 to 5 sentences. Highlight ARR, license utilization, health status, and ticket volume/trend.
2. Open Risks & Escalations: Highlight any churn risk, dissatisfaction, or recurring P1/P2 issues. 
   CRITICAL REQUIREMENT: For every risk flagged, provide a direct verbatim quote from a support ticket body or subject justifying the risk, along with the ticket_id. 
   ***IF THERE ARE NO RISKS, RETURN AN EMPTY LIST [] FOR open_risks. DO NOT FABRICATE QUOTES.***
3. Talking Points: Provide 3 to 4 actionable, strategic talking points for the TAM's upcoming executive call.
4. Determinism: Maintain an objective, professional tone without speculative hallucinations.
"""

def generate_tam_brief(account_id: str, data_dir: str = "data") -> TAMAccountBrief:
    """Generates the structured TAM brief for a specific account."""
    context = get_account_context(account_id, data_dir)
    if not context:
        raise ValueError(f"Account ID '{account_id}' not found in dataset.")
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", TAM_PROMPT),
        ("human", "ACCOUNT DETAILS:\n{account_json}\n\nRECENT TICKETS (LAST 90 DAYS):\n{tickets_json}")
    ])
    
    chain = prompt | structured_summarizer
    
    result = chain.invoke({
        "account_json": json.dumps(context["account"], indent=2),
        "tickets_json": json.dumps(context["recent_tickets"], indent=2)
    })
    
    return result