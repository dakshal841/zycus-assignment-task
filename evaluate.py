import json
import requests
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000"

# --- Test Cases ---
TASK_1_TESTS = [
    {"id": "t1_1", "type": "standard", "payload": {"subject": "Server Down", "body": "Total outage on US-East."}},
    {"id": "t1_2", "type": "standard", "payload": {"subject": "Billing issue", "body": "Need invoice for last month."}},
    {"id": "t1_3", "type": "standard", "payload": {"subject": "Bug in dashboard", "body": "Chart fails to load on refresh."}},
    {"id": "t1_4", "type": "standard", "payload": {"subject": "Feature request", "body": "Add dark mode."}},
    {"id": "t1_5", "type": "adversarial", "payload": {"subject": "broken", "body": "fix it now."}} # Vague/Adversarial
]

TASK_2_TESTS = [
    {"id": "t2_1", "type": "standard", "account_id": "ACC-3336"}, # At Risk
    {"id": "t2_2", "type": "standard", "account_id": "ACC-2535"}, # Assuming valid
    {"id": "t2_3", "type": "standard", "account_id": "ACC-1001"}, # Mock valid
    {"id": "t2_4", "type": "standard", "account_id": "ACC-1002"}, # Mock valid
    {"id": "t2_5", "type": "adversarial", "account_id": "ACC-9999"} # Missing/Invalid
]

def evaluate_task_1(test_case: Dict) -> Dict:
    """Rule-based evaluation for Task 1."""
    try:
        res = requests.post(f"{BASE_URL}/triage", json=test_case["payload"])
        if res.status_code != 200:
            return {"pass": False, "score": 0.0, "reason": f"HTTP {res.status_code}"}
        
        data = res.json()
        # Quality Gate: Urgency must be a valid Enum
        valid_urgency = data.get("urgency") in ["P1", "P2", "P3", "P4"]
        has_response = bool(data.get("draft_response"))
        
        score = 1.0 if (valid_urgency and has_response) else 0.5
        return {"pass": score == 1.0, "score": score, "reason": "Passed structure and logic checks"}
    except Exception as e:
        return {"pass": False, "score": 0.0, "reason": str(e)}

def evaluate_task_2(test_case: Dict) -> Dict:
    """Evaluation for Task 2."""
    try:
        res = requests.get(f"{BASE_URL}/tam/brief/{test_case['account_id']}")
        if test_case["type"] == "adversarial" and res.status_code == 404:
            return {"pass": True, "score": 1.0, "reason": "Correctly handled invalid account"}
            
        if res.status_code != 200:
            return {"pass": False, "score": 0.0, "reason": f"HTTP {res.status_code}"}
            
        data = res.json()
        # Quality Gate: Check if talking points exist
        has_points = len(data.get("talking_points", [])) >= 3
        
        score = 1.0 if has_points else 0.5
        return {"pass": score == 1.0, "score": score, "reason": "Passed synthesis checks"}
    except Exception as e:
        return {"pass": False, "score": 0.0, "reason": str(e)}

def run_evals():
    print("Running Task 1 Evals...")
    t1_results = {tc["id"]: evaluate_task_1(tc) for tc in TASK_1_TESTS}
    
    print("Running Task 2 Evals...")
    t2_results = {tc["id"]: evaluate_task_2(tc) for tc in TASK_2_TESTS}
    
    report = {
        "task_1_triage": t1_results,
        "task_2_tam_brief": t2_results,
        "summary": {
            "task_1_pass_rate": sum(1 for r in t1_results.values() if r["pass"]) / len(t1_results),
            "task_2_pass_rate": sum(1 for r in t2_results.values() if r["pass"]) / len(t2_results)
        }
    }
    
    with open("eval_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("Evaluation complete. Saved to eval_report.json")

if __name__ == "__main__":
    run_evals()