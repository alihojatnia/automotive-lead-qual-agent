from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json
import os
from sqlalchemy.orm import Session
from models import Lead
from database import get_db  # We'll create next

llm = ChatOllama(model="llama3.2", temperature=0)

# Mock Inventory (real: query DB/API)
MOCK_INVENTORY = [
    {"model": "Hyundai Tucson Hybrid", "type": "SUV", "price": 35000, "electric": True},
    {"model": "Tesla Model Y", "type": "SUV", "price": 45000, "electric": True},
    {"model": "Toyota Camry", "type": "Sedan", "price": 28000, "electric": False},
]

class LeadState(TypedDict):
    raw_message: str
    parsed: Dict[str, Any]
    score: float
    suggested_action: str
    lead_id: int

# 1. Parser Agent
def parser_agent(state: LeadState) -> LeadState:
    prompt = ChatPromptTemplate.from_template("""
    Parse this automotive lead message into JSON:
    {{"budget": "e.g. under 40k €", "vehicle_type": "SUV/Sedan/EV", "preferences": "electric, family-friendly", "timeline": "ASAP/3 months", "name_email": "John / john@email.com"}}

    Message: {message}
    Output ONLY valid JSON.
    """)
    chain = prompt | llm | JsonOutputParser()
    parsed = chain.invoke({"message": state["raw_message"]})
    print(f" Parsed: {parsed}")
    return {"parsed": parsed}

# 2. Scoring Agent
def scoring_agent(state: LeadState) -> LeadState:
    inv_str = json.dumps(MOCK_INVENTORY)
    prompt = ChatPromptTemplate.from_template("""
    Score this lead 1-10 (10=perfect fit).
    Match: vehicle_type/preferences to inventory: {inv}
    Budget fit: if budget covers price.
    Timeline: ASAP = +2 pts.

    Parsed: {parsed}

    Respond JSON: {{"score": 8.5, "reasoning": "Strong EV SUV match", "suggested_action": "Schedule test drive for Tesla Model Y"}}
    """)
    chain = prompt | llm | JsonOutputParser()
    result = chain.invoke({"parsed": state["parsed"], "inv": inv_str})
    print(f"Score: {result['score']}/10 | Action: {result['suggested_action']}")
    return {
        "score": result["score"],
        "suggested_action": result["suggested_action"]
    }

# 3. Action Agent (Mock CRM Update)
def action_agent(state: LeadState) -> LeadState:
    with get_db() as db:
        lead = Lead(
            raw_message=state["raw_message"],
            parsed_data=state["parsed"],
            score=state["score"],
            suggested_action=state["suggested_action"]
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)
        print(f"Saved Lead ID: {lead.id}")
    return {"lead_id": lead.id}

# Build DAG Graph
workflow = StateGraph(LeadState)
workflow.add_node("parser", parser_agent)
workflow.add_node("scorer", scoring_agent)
workflow.add_node("updater", action_agent)

workflow.set_entry_point("parser")
workflow.add_edge("parser", "scorer")
workflow.add_edge("scorer", "updater")
workflow.add_edge("updater", END)

app = workflow.compile()