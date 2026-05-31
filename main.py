import os
import json
from typing import Dict, List, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()

# 1. Schema Definitions for Deterministic Output
class AccountDigest(BaseModel):
    accountId: str = Field(description="The source reference Account ID")
    companyName: str = Field(description="Name of the enterprise company")
    riskLevel: str = Field(description="Must be strictly classified as: CRITICAL, ELEVATED, or STABLE")
    commercialUrgency: str = Field(description="Days remaining until contract completion + stage analysis")
    executiveSummary: str = Field(description="Synthesized operational summary of product health and transcript risks")
    actionItems: List[str] = Field(description="Explicit actionable items parsed from transcripts")

class PortfolioDigestCollection(BaseModel):
    csmId: str
    digests: List[AccountDigest]

# LangGraph State Machine Schema
class GraphState(TypedDict):
    target_csm: str
    aggregated_raw_data: List[Dict[str, Any]]
    synthesized_digests: List[Dict[str, Any]]
    slack_payloads: List[Dict[str, Any]]

# Initialize FastAPI
app = FastAPI(title="GTM Automation Engine Execution Hub")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Graph Node Functions

def node_aggregate_telemetry(state: GraphState) -> Dict[str, Any]:
    """Node 1: Parses local mock databases and performs a relational join on account_name."""
    csm = state["target_csm"]
    
    # Load the mock data we generated in Phase 2
    with open("mock_data/vitally_mock.json", "r") as f: vitally = json.load(f)
    with open("mock_data/sfdc_mock.json", "r") as f: sfdc = json.load(f)
    with open("mock_data/weflow_mock.json", "r") as f: weflow = json.load(f)

    # Filter for the target CSM. If the requested CSM is not found (e.g. "CSM_MARK_R"), 
    # fallback to the first CSM in the database for demo testing.
    csm_accounts = [acc for acc in vitally if acc.get("customer_success_manager") == csm]
    if not csm_accounts and vitally:
        fallback_csm = vitally[0].get("customer_success_manager")
        csm_accounts = [acc for acc in vitally if acc.get("customer_success_manager") == fallback_csm]

    hydrated_portfolio = []

    # Join the records on account_name
    for acc in csm_accounts:
        acc_name = acc.get("account_name")
        sfdc_record = next((s for s in sfdc if s.get("account_name") == acc_name), {})
        weflow_record = next((w for w in weflow if w.get("account_name") == acc_name), {})
        
        hydrated_portfolio.append({
            "meta": acc,
            "commercial": sfdc_record,
            "conversational": weflow_record
        })
        
    return {"aggregated_raw_data": hydrated_portfolio}


def node_synthesize_intelligence(state: GraphState) -> Dict[str, Any]:
    """Node 2: Passes the raw JSON through GPT-4o-mini to extract compound risks, or falls back to mock logic."""
    raw_bundle = state["aggregated_raw_data"]
    csm = state["target_csm"]
    
    # Check if a valid OpenAI API key is set. If not, use the mock analyzer.
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or "YOUR_ACTUAL_OPENAI_KEY" in api_key:
        print("WARNING: Using mock fallback for node_synthesize_intelligence because OPENAI_API_KEY is placeholder or not set.")
        digests = []
        for item in raw_bundle:
            meta = item.get("meta", {})
            comm = item.get("commercial", {})
            conv = item.get("conversational", {})
            
            # Simple rule-based logic to mimic the LLM risk classification
            health_score = meta.get("health_score", 100)
            sentiment = conv.get("customer_sentiment", "Positive")
            
            if health_score < 50 or sentiment == "Negative":
                risk_level = "CRITICAL"
            elif health_score < 75:
                risk_level = "ELEVATED"
            else:
                risk_level = "STABLE"
                
            digests.append({
                "accountId": meta.get("account_id", "unknown"),
                "companyName": meta.get("account_name", "Unknown Corp"),
                "riskLevel": risk_level,
                "commercialUrgency": f"Renewal: {comm.get('renewal_date', 'N/A')} (Stage: {comm.get('stage', 'N/A')})",
                "executiveSummary": f"Automated summary: Health score is {health_score} ({meta.get('health_status', 'N/A')}) with {sentiment} customer sentiment. Transcript shows: '{conv.get('transcript_summary', 'N/A')}'",
                "actionItems": conv.get("action_items", ["Review account status"])
            })
        return {"synthesized_digests": digests}

    # Using gpt-4o-mini for rapid execution during the live demo
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    structured_llm = llm.with_structured_output(PortfolioDigestCollection)

    system_prompt = (
        "You are an elite Revenue Operations Data Analyst. Analyze the raw multi-system JSON "
        "payload and extract compound risks. Classify risk as CRITICAL if the Vitally health "
        "score is below 60 and renewal is within 60 days, or if Weflow transcript shows severe issues. "
        "Summarize the context professionally. Map all accountId fields to the vitally account_id."
    )
    
    user_content = f"Target CSM: {csm}. Data: {json.dumps(raw_bundle, indent=2)}"
    
    # Execute the LLM call
    response = structured_llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ])
    
    return {"synthesized_digests": response.model_dump()["digests"]}


def node_format_slack_blocks(state: GraphState) -> Dict[str, Any]:
    """Node 3: Translates the structured Pydantic output into raw Slack Block Kit UI JSON."""
    digests = state["synthesized_digests"]
    blocks = []
    
    # Standard Slack Header
    blocks.append({
        "type": "header",
        "text": {"type": "plain_text", "text": "📅 Monday Portfolio Intelligence Briefing", "emoji": True}
    })
    blocks.append({"type": "divider"})

    # Iterate through each account and build the UI blocks
    for d in digests:
        color = "🔴" if d["riskLevel"] == "CRITICAL" else "🟡" if d["riskLevel"] == "ELEVATED" else "🟢"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{color} *{d['companyName']}* ({d['accountId']})\n*Risk Status:* {d['riskLevel']} | *Timeline:* {d['commercialUrgency']}\n\n*Analysis:* {d['executiveSummary']}"
            }
        })
        
        # Add action items if the LLM identified any
        if d["actionItems"]:
            action_list = "\n".join([f"• {item}" for item in d["actionItems"]])
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Required Actions:*\n{action_list}"}
            })
            
        blocks.append({"type": "divider"})
        
    return {"slack_payloads": blocks}


# 3. Compile the Automation Graph Topology
workflow = StateGraph(GraphState)

# Add nodes to the graph
workflow.add_node("DataAggregator", node_aggregate_telemetry)
workflow.add_node("IntelligenceAnalyzer", node_synthesize_intelligence)
workflow.add_node("SlackFormatter", node_format_slack_blocks)

# Define the chronological execution flow
workflow.set_entry_point("DataAggregator")
workflow.add_edge("DataAggregator", "IntelligenceAnalyzer")
workflow.add_edge("IntelligenceAnalyzer", "SlackFormatter")
workflow.add_edge("SlackFormatter", END)

# Compile the engine
orchestrator_engine = workflow.compile()

# 4. REST API Routing (The Webhook)
class TriggerRequest(BaseModel):
    csmId: str

@app.post("/api/trigger-digest")
async def execute_pipeline(payload: TriggerRequest):
    """The webhook endpoint that our Next.js frontend will hit."""
    initial_state = {
        "target_csm": payload.csmId,
        "aggregated_raw_data": [],
        "synthesized_digests": [],
        "slack_payloads": []
    }
    
    # Run the graph
    execution_result = orchestrator_engine.invoke(initial_state)
    
    return {
        "status": "SUCCESS",
        "csmProcessed": payload.csmId,
        "slackBlockKitPayload": execution_result["slack_payloads"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
