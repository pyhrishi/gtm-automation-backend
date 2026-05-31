import os
import json
import random
import uuid
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

# Directory containing the script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MOCK_DATA_DIR = os.path.join(SCRIPT_DIR, "mock_data")

# Ensure the mock_data directory exists
os.makedirs(MOCK_DATA_DIR, exist_ok=True)

# Generate a consistent list of accounts
ACCOUNTS = [
    "Acme Corp", "Globex Corporation", "Initech", "Umbrella Corp",
    "Soylent Corp", "Hooli", "Vehement Capital Partners", "Massive Dynamic",
    "Stark Industries", "Wayne Enterprises", "Cyberdyne Systems", "Oscorp"
]

def generate_vitally_data():
    data = []
    csm_names = [fake.name() for _ in range(3)]
    for name in ACCOUNTS:
        score = random.randint(30, 100)
        if score >= 75:
            status = "Green"
        elif score >= 50:
            status = "Yellow"
        else:
            status = "Red"
            
        account = {
            "account_id": f"vit-{str(uuid.uuid4())[:8]}",
            "account_name": name,
            "health_score": score,
            "health_status": status,
            "monthly_active_users": random.randint(10, 500),
            "license_utilization": round(random.uniform(0.3, 0.98), 2),
            "nps_score": random.randint(4, 10),
            "customer_success_manager": random.choice(csm_names)
        }
        data.append(account)
    return data

def generate_sfdc_data():
    data = []
    ae_names = [fake.name() for _ in range(3)]
    stages = ["Negotiation", "Proposal", "Contracting", "Closed Won"]
    
    for name in ACCOUNTS:
        days_offset = random.randint(-10, 90)
        renewal_date = (datetime.now() + timedelta(days=days_offset)).strftime("%Y-%m-%d")
        
        opportunity = {
            "opportunity_id": f"006{str(uuid.uuid4())[:15].upper()}",
            "account_name": name,
            "arr": float(random.randint(50000, 350000)),
            "renewal_date": renewal_date,
            "stage": random.choice(stages),
            "account_executive": random.choice(ae_names)
        }
        data.append(opportunity)
    return data

def generate_weflow_data():
    data = []
    
    summaries = [
        "Customer is concerned about the latest API rate limits but is generally satisfied. Looking to expand license count next quarter.",
        "AE conducted a renewal sync. Customer raised issues with Vitally integration syncing. Next step is a call with solutions engineer.",
        "Mid-quarter check-in. The user adoption is high, but the champion is leaving the company. High risk of contraction.",
        "Product walkthrough done. Customer loved the new automated GTM feature. Requested contract draft for upgrade.",
        "Support escalation follow-up. The customer experienced 2 hours of downtime yesterday and is highly agitated. Health score is dropping.",
        "QBR completed. Customer validated that they are seeing 2.5x ROI. Looking forward to expansion next year.",
        "Routine touchpoint. The platform is running smoothly. Customer asked about SOC2 compliance document.",
        "Kickoff call for the new trial period. Set success criteria and timeline. Customer AE is tracking tightly."
    ]
    
    sentiments = ["Positive", "Neutral", "Negative"]
    
    action_items_pool = [
        "Send API documentation link",
        "Schedule follow-up call with Solution Architect",
        "Send updated pricing proposal for 20 extra seats",
        "Introduce new CSM to the account champion",
        "Provide SOC2 compliance report",
        "Set up meeting to review downtime root-cause analysis",
        "Share product roadmap deck"
    ]
    
    for name in ACCOUNTS:
        days_offset = random.randint(-15, 0)
        interaction_date = (datetime.now() + timedelta(days=days_offset)).strftime("%Y-%m-%d")
        
        summary = random.choice(summaries)
        sentiment = random.choice(sentiments)
        action_items = random.sample(action_items_pool, k=random.randint(1, 3))
        
        interaction = {
            "interaction_id": f"int-{str(uuid.uuid4())[:8]}",
            "account_name": name,
            "last_interaction_date": interaction_date,
            "transcript_summary": summary,
            "customer_sentiment": sentiment,
            "action_items": action_items
        }
        data.append(interaction)
    return data

def main():
    print("Generating mock data...")
    
    vitally_data = generate_vitally_data()
    sfdc_data = generate_sfdc_data()
    weflow_data = generate_weflow_data()
    
    vitally_path = os.path.join(MOCK_DATA_DIR, "vitally_mock.json")
    sfdc_path = os.path.join(MOCK_DATA_DIR, "sfdc_mock.json")
    weflow_path = os.path.join(MOCK_DATA_DIR, "weflow_mock.json")
    
    with open(vitally_path, "w") as f:
        json.dump(vitally_data, f, indent=2)
    print(f"Saved {len(vitally_data)} Vitally records to {vitally_path}")
        
    with open(sfdc_path, "w") as f:
        json.dump(sfdc_data, f, indent=2)
    print(f"Saved {len(sfdc_data)} SFDC records to {sfdc_path}")
        
    with open(weflow_path, "w") as f:
        json.dump(weflow_data, f, indent=2)
    print(f"Saved {len(weflow_data)} Weflow records to {weflow_path}")
    
    print("Mock data generation complete!")

if __name__ == "__main__":
    main()
