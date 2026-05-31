import json
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()
Faker.seed(101)  # Fixed seed for repeatable interview demonstrations
random.seed(101)

def build_deterministic_universe():
    csm_ids = [
        "CSM_MARK_R", "CSM_SARAH_K", "CSM_ALEX_B", "CSM_JESSICA_T",
        "CSM_DAVID_L", "CSM_EMILY_C", "CSM_MICHAEL_W"
    ]
    
    csm_names = {
        "CSM_MARK_R": "Mark Robinson",
        "CSM_SARAH_K": "Sarah Jenkins",
        "CSM_ALEX_B": "Alex Baldwin",
        "CSM_JESSICA_T": "Jessica Taylor",
        "CSM_DAVID_L": "David Lang",
        "CSM_EMILY_C": "Emily Chen",
        "CSM_MICHAEL_W": "Michael Wong"
    }

    # Generate 15 accounts per CSM
    accounts = []
    acc_idx = 1
    
    # We define distinct pools of actions and comments for realism
    critical_comments = [
        "Exec sync. Champion left. New leadership reviewing spending. Severe platform churn risk.",
        "User adoption dropping. Customer complains about API limits. Renewal at risk.",
        "Support escalations. Downtime last week. Agitated stakeholders. Health score dropping.",
        "Contraction risk. Champion has departed. Budget freeze on renewals.",
        "Unresolved bugs syncing CPQ. Technical blockers causing friction.",
        "Stakeholder churn. Champion left company. Platform adoption stalling.",
        "Support ticket escalation. API performance issues and latency errors reported."
    ]
    
    stable_comments = [
        "Sync complete. Product usage expanding into APAC division. No blockers reported.",
        "QBR completed. Customer seeing 2.5x ROI. Expansion scheduled for next Q.",
        "Healthy account. Stakeholder is highly active in Slack. High NPS score.",
        "Stable telemetry. Customer requested walkthrough of new automated GTM integrations.",
        "Touchpoint complete. User onboarding going smoothly. Integration active.",
        "Smooth operations. Trial period started on expansion modules. AE driving upsell.",
        "Platform usage is high. License count expanded into EMEA region last week."
    ]

    critical_actions = [
        ["Introduce new CSM to champion", "Provide SOC2 compliance report", "Share product roadmap deck"],
        ["Schedule Tech Audit call", "Send API rate limits proposal"],
        ["Review downtime RCA with AE", "Provide compliance validation"],
        ["Book meeting with executive buyer", "Share platform upgrade pricing"],
        ["Schedule Solution Architect sync", "Provide custom SDK patches"],
        ["Reach out to new GTM Director", "Schedule fresh team training"],
        ["Escalate API latency tickets", "Send API status dashboard link"]
    ]

    stable_actions = [
        ["Monitor adoption rates"],
        ["Send expansion pricing sheet"],
        ["Ask for case study reference"],
        ["Send integrations docs link"],
        ["Follow up on SSO set up"],
        ["Send roadmap slide deck"],
        ["Arrange QBR for expansion metrics"]
    ]

    stages = ["Discovery", "Qualification", "Proposal Sent", "Negotiation", "Closed Won", "Contract Signed"]

    for csm in csm_ids:
        for i in range(15):
            # 3 critical accounts per CSM (every 5th account)
            is_critical = (i % 5 == 0)
            accounts.append({
                "id": f"ACC_{acc_idx:03d}",
                "name": fake.company(),
                "csm": csm,
                "critical": is_critical
            })
            acc_idx += 1

    vitally = []
    salesforce = []
    weflow = []
    ts_portfolios = {}

    for acc in accounts:
        csm_id = acc["csm"]
        csm_name = csm_names[csm_id]
        
        # 1. Vitally Hydration
        h_score = round(random.uniform(2.5, 5.8), 1) if acc["critical"] else round(random.uniform(8.0, 10.0), 1)
        nps = random.randint(-50, 10) if acc["critical"] else random.randint(40, 95)
        
        vitally.append({
            "accountId": acc["id"],
            "companyName": acc["name"],
            "csmId": csm_id,
            "healthScore": h_score,
            "npsScore": nps
        })

        # 2. Salesforce Hydration
        days_to_renewal = random.randint(10, 45) if acc["critical"] else random.randint(120, 300)
        renewal_date = (datetime.now() + timedelta(days=days_to_renewal)).strftime('%Y-%m-%d')
        stage = random.choice(stages[:-2]) if acc["critical"] else random.choice(stages[-2:])
        arr = round(random.uniform(75000, 350000), 0)
        sfdc_opp_value = arr * round(random.uniform(1.0, 1.3), 2) if stage != "Closed Won" else arr
        primary_contact = fake.name()
        contact_role = random.choice(["VP of Engineering", "Director of IT Ops", "Head of Procurement", "CTO", "CEO", "VP of Operations"])

        salesforce.append({
            "accountId": acc["id"],
            "contractId": f"CON-{random.randint(1000,9999)}",
            "renewalOpportunityStage": stage,
            "contractEndDate": renewal_date,
            "arrValue": arr
        })

        # 3. Weflow Hydration
        summary = random.choice(critical_comments) if acc["critical"] else random.choice(stable_comments)
        actions = random.choice(critical_actions) if acc["critical"] else random.choice(stable_actions)
        
        weflow.append({
            "accountId": acc["id"],
            "lastInteractionDate": (datetime.now() - timedelta(days=random.randint(1, 5))).strftime('%Y-%m-%d'),
            "transcriptSummary": summary,
            "escalationFlag": acc["critical"]
        })

        # Pack into TypeScript Portfolios structure
        if csm_id not in ts_portfolios:
            ts_portfolios[csm_id] = {
                "csmName": csm_name,
                "accounts": []
            }
        
        ts_portfolios[csm_id]["accounts"].append({
            "id": acc["id"],
            "name": acc["name"],
            "health": h_score,
            "status": "CRITICAL" if acc["critical"] else "STABLE",
            "arr": int(arr),
            "renewal": renewal_date,
            "sentiment": "Negative" if acc["critical"] else "Positive",
            "summary": summary,
            "actions": actions,
            "contractStage": stage,
            "sfdcOppValue": int(sfdc_opp_value),
            "nps": nps,
            "primaryContact": primary_contact,
            "contactRole": contact_role
        })

    # Save backend JSON files
    with open("mock_data/vitally_mock.json", "w") as f: json.dump(vitally, f, indent=2)
    with open("mock_data/sfdc_mock.json", "w") as f: json.dump(salesforce, f, indent=2)
    with open("mock_data/weflow_mock.json", "w") as f: json.dump(weflow, f, indent=2)
    print("🎯 Backend JSON mock files hydrated.")

    # Output frontend TypeScript format
    with open("mock_data/frontend_db.json", "w") as f: json.dump(ts_portfolios, f, indent=2)
    print("🎯 Frontend TS format saved to mock_data/frontend_db.json.")

if __name__ == "__main__":
    build_deterministic_universe()
