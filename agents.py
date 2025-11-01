# from database import get_db
# from typing import TypedDict, Dict, Any
# from langgraph.graph import StateGraph, END
# from langchain_ollama import ChatOllama
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import JsonOutputParser
# import json
# import os
# from sqlalchemy.orm import Session
# from models import Lead
# from database import get_db  # We'll create next

# llm = ChatOllama(model="llama3.2:1b", temperature=0)

# # Mock Inventory (real: query DB/API)
# MOCK_INVENTORY = [
#     {"model": "Hyundai Tucson Hybrid", "type": "SUV", "price": 35000, "electric": True},
#     {"model": "Tesla Model Y", "type": "SUV", "price": 45000, "electric": True},
#     {"model": "Toyota Camry", "type": "Sedan", "price": 28000, "electric": False},
# ]

# class LeadState(TypedDict):
#     raw_message: str
#     parsed: Dict[str, Any]
#     score: float
#     suggested_action: str
#     lead_id: int

# # 1. Parser Agent
# def parser_agent(state: LeadState) -> LeadState:
#     prompt = ChatPromptTemplate.from_template("""
#     Parse this automotive lead message into JSON:
#     {{"budget": "e.g. under 40k €", "vehicle_type": "SUV/Sedan/EV", "preferences": "electric, family-friendly", "timeline": "ASAP/3 months", "name_email": "John / john@email.com"}}

#     Message: {message}
#     Output ONLY valid JSON.
#     """)
#     chain = prompt | llm | JsonOutputParser()
#     parsed = chain.invoke({"message": state["raw_message"]})
#     print(f" Parsed: {parsed}")
#     return {"parsed": parsed}

# # 2. Scoring Agent
# def scoring_agent(state: LeadState) -> LeadState:
#     inv_str = json.dumps(MOCK_INVENTORY)
#     prompt = ChatPromptTemplate.from_template("""
#     Score this lead 1-10 (10=perfect fit).
#     Match: vehicle_type/preferences to inventory: {inv}
#     Budget fit: if budget covers price.
#     Timeline: ASAP = +2 pts.

#     Parsed: {parsed}

#     Respond JSON: {{"score": 8.5, "reasoning": "Strong EV SUV match", "suggested_action": "Schedule test drive for Tesla Model Y"}}
#     """)
#     chain = prompt | llm | JsonOutputParser()
#     result = chain.invoke({"parsed": state["parsed"], "inv": inv_str})
#     print(f"Score: {result['score']}/10 | Action: {result['suggested_action']}")
#     return {
#         "score": result["score"],
#         "suggested_action": result["suggested_action"]
#     }

# # 3. Action Agent (Mock CRM Update)
# def action_agent(state: LeadState) -> LeadState:
#     with get_db() as db:
#         lead = Lead(
#             raw_message=state["raw_message"],
#             parsed_data=state["parsed"],
#             score=state["score"],
#             suggested_action=state["suggested_action"]
#         )
#         db.add(lead)
#         db.commit()
#         db.refresh(lead)
#         print(f"Saved Lead ID: {lead.id}")
#     return {"lead_id": lead.id}

# # Build DAG Graph
# workflow = StateGraph(LeadState)
# workflow.add_node("parser", parser_agent)
# workflow.add_node("scorer", scoring_agent)
# workflow.add_node("updater", action_agent)

# workflow.set_entry_point("parser")
# workflow.add_edge("parser", "scorer")
# workflow.add_edge("scorer", "updater")
# workflow.add_edge("updater", END)

# app = workflow.compile()


from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json
from database import get_db  # Must be imported
from models import Lead



from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json
import re
from database import get_db
from models import Lead

# LLM
llm = ChatOllama(model="llama3.2:1b", temperature=0)

# Mock Inventory
MOCK_INVENTORY = [
    {"model": "Hyundai Tucson Hybrid", "type": "SUV", "price": 35000, "electric": True},
    {"model": "Tesla Model Y", "type": "SUV", "price": 45000, "electric": True},
    {"model": "Toyota Camry", "type": "Sedan", "price": 28000, "electric": False},
]

# State
class LeadState(TypedDict):
    raw_message: str
    parsed: Dict[str, Any]
    score: float
    suggested_action: str
    lead_id: int

# Helper: Extract JSON with regex fallback
def extract_json(text: str) -> dict:
    try:
        # Try normal JSON
        return json.loads(text)
    except:
        # Fallback: find first { ... }
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
    return {}

# 1. Parser Agent
def parser_agent(state: LeadState) -> LeadState:
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a lead parser. 
Return ONLY a JSON object with:
- budget
- vehicle_type
- preferences
- timeline
- name_email

Example:
{{"budget": "under €40k", "vehicle_type": "SUV", "preferences": "electric, family of 4", "timeline": "ASAP", "name_email": "John - john@test.com"}}
"""),
        ("human", "Parse this message: {message}")
    ])
    chain = prompt | llm
    try:
        raw = chain.invoke({"message": state["raw_message"]}).content
        parsed = extract_json(raw)
        print(f"Parsed: {parsed}")
        return {"parsed": parsed or {}}
    except Exception as e:
        print(f"Parser failed: {e}")
        return {"parsed": {}}

# 2. Scoring Agent
def scoring_agent(state: LeadState) -> LeadState:
    inv_str = json.dumps(MOCK_INVENTORY, indent=2)
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a lead scoring expert.
Return ONLY a JSON object with:
- score (0.0 to 10.0)
- reasoning (1 short sentence)
- suggested_action (1 short action)

Example:
{{"score": 9.0, "reasoning": "Strong match", "suggested_action": "Schedule test drive"}}

Inventory:
{inv}

Parsed Lead:
{parsed}
"""),
        ("human", "Score this lead.")
    ])
    chain = prompt | llm
    try:
        raw = chain.invoke({"parsed": state["parsed"], "inv": inv_str}).content
        result = extract_json(raw)
        score = float(result.get("score", 0.0))
        action = result.get("suggested_action", "Follow up")
        print(f"Score: {score}/10 | Action: {action}")
        return {"score": score, "suggested_action": action}
    except Exception as e:
        print(f"Scoring failed: {e}")
        return {"score": 0.0, "suggested_action": "Manual review"}

# 3. Action Agent
def action_agent(state: LeadState) -> LeadState:
    try:
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
    except Exception as e:
        print(f"DB Error: {e}")
        return {"lead_id": -1}

# Build Graph
workflow = StateGraph(LeadState)
workflow.add_node("parser", parser_agent)
workflow.add_node("scorer", scoring_agent)
workflow.add_node("updater", action_agent)

workflow.set_entry_point("parser")
workflow.add_edge("parser", "scorer")
workflow.add_edge("scorer", "updater")
workflow.add_edge("updater", END)

app = workflow.compile()