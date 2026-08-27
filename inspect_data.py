import os
import json
import glob

def inspect_dataset():
    print("=== INSPECTING MOCK DATASET ===\n")
    
    # 1. Inspect Tickets
    ticket_files = glob.glob("data/*ticket*.*")
    if ticket_files:
        path = ticket_files[0]
        print(f"Found Tickets File: {path}")
        with open(path, "r", encoding="utf-8") as f:
            tickets = json.load(f)
            print(f"Total tickets: {len(tickets)}")
            if len(tickets) > 0:
                print(f"Sample Ticket Keys: {list(tickets[0].keys())}")
                print(f"Sample Ticket:\n{json.dumps(tickets[0], indent=2)}\n")
    
    # 2. Inspect Accounts
    account_files = glob.glob("data/*account*.*")
    if account_files:
        path = account_files[0]
        print(f"Found Accounts File: {path}")
        with open(path, "r", encoding="utf-8") as f:
            accounts = json.load(f)
            print(f"Total accounts: {len(accounts)}")
            if len(accounts) > 0:
                print(f"Sample Account Keys: {list(accounts[0].keys())}")
                print(f"Sample Account:\n{json.dumps(accounts[0], indent=2)}\n")
                
    # 3. Inspect Knowledge Base Docs
    kb_files = glob.glob("data/**/*.md", recursive=True)
    print(f"Found {len(kb_files)} Knowledge Base Markdown document(s).")
    if kb_files:
        sample_kb = kb_files[0]
        print(f"Sample Doc: {sample_kb}")
        with open(sample_kb, "r", encoding="utf-8") as f:
            print("--- Snippet (first 300 chars) ---")
            print(f.read()[:300])
            print("---------------------------------")

if __name__ == "__main__":
    inspect_dataset()