import json
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()
Faker.seed(101)  # Fixed seed for repeatable interview demonstrations

def build_deterministic_universe():
    # Complete roster of 7 Enterprise CSMs and their mock accounts
    accounts = [
        # Mark's Portfolio
        {"id": "ACC_001", "name": "Acme Corp", "csm": "CSM_MARK_R", "critical": True},
        {"id": "ACC_002", "name": "Globex Inc", "csm": "CSM_MARK_R", "critical": False},
        
        # Sarah's Portfolio
        {"id": "ACC_003", "name": "Initech LLC", "csm": "CSM_SARAH_K", "critical": True},
        {"id": "ACC_004", "name": "Umbrella Corp", "csm": "CSM_SARAH_K", "critical": False},
        
        # Alex's Portfolio
        {"id": "ACC_005", "name": "Stark Industries", "csm": "CSM_ALEX_B", "critical": True},
        {"id": "ACC_006", "name": "Wayne Enterprises", "csm": "CSM_ALEX_B", "critical": False},
        
        # Jessica's Portfolio
        {"id": "ACC_007", "name": "Cyberdyne Systems", "csm": "CSM_JESSICA_T", "critical": False},
        {"id": "ACC_008", "name": "Soylent Corp", "csm": "CSM_JESSICA_T", "critical": True},
        
        # David's Portfolio
        {"id": "ACC_009", "name": "Massive Dynamic", "csm": "CSM_DAVID_L", "critical": True},
        {"id": "ACC_012", "name": "Tyrell Corp", "csm": "CSM_DAVID_L", "critical": False},
        
        # Emily's Portfolio
        {"id": "ACC_010", "name": "Hooli", "csm": "CSM_EMILY_C", "critical": False},
        {"id": "ACC_013", "name": "Pied Piper", "csm": "CSM_EMILY_C", "critical": True},
        
        # Michael's Portfolio
        {"id": "ACC_011", "name": "Oscorp", "csm": "CSM_MICHAEL_W", "critical": True},
        {"id": "ACC_014", "name": "LexCorp", "csm": "CSM_MICHAEL_W", "critical": False},
    ]
    
    vitally = []
    salesforce = []
    weflow = []

    for acc in accounts:
        # 1. Vitally Hydration
        h_score = round(random.uniform(2.5, 5.8), 1) if acc["critical"] else round(random.uniform(8.0, 10.0), 1)
        vitally.append({
            "accountId": acc["id"],
            "companyName": acc["name"],
            "csmId": acc["csm"],
            "healthScore": h_score,
            "npsScore": random.randint(-50, 10) if acc["critical"] else random.randint(40, 95)
        })

        # 2. Salesforce Hydration
        days_to_renewal = random.randint(10, 45) if acc["critical"] else random.randint(120, 300)
        renewal_date = (datetime.now() + timedelta(days=days_to_renewal)).strftime('%Y-%m-%d')
        salesforce.append({
            "accountId": acc["id"],
            "contractId": f"CON-{random.randint(1000,9999)}",
            "renewalOpportunityStage": "Discovery" if acc["critical"] else "Closed Won",
            "contractEndDate": renewal_date,
            "arrValue": round(random.uniform(75000, 300000), 2)
        })

        # 3. Weflow Hydration
        crit_summary = f"Exec sync on {acc['name']}. Champion left the company last week. New leadership is reviewing spending. Severe platform churn risk identified."
        std_summary = f"Weekly sync complete. Product usage expanding steadily into APAC division. No blockers reported."
        weflow.append({
            "accountId": acc["id"],
            "lastInteractionDate": (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            "transcriptSummary": crit_summary if acc["critical"] else std_summary,
            "escalationFlag": acc["critical"]
        })

    with open("mock_data/vitally_mock.json", "w") as f: json.dump(vitally, f, indent=2)
    with open("mock_data/sfdc_mock.json", "w") as f: json.dump(salesforce, f, indent=2)
    with open("mock_data/weflow_mock.json", "w") as f: json.dump(weflow, f, indent=2)
    print("🎯 Data generation complete. 7 CSM Target schemas unified.")

if __name__ == "__main__":
    build_deterministic_universe()
