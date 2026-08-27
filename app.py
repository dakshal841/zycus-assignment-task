import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Support & TAM Hub", layout="wide")
st.title("🛠️ AI Support & TAM Internal Tooling")

tab1, tab2 = st.tabs(["Ticket Triage (Task 1)", "TAM Account Brief (Task 2)"])

with tab1:
    st.header("Intelligent Ticket Triage")
    subject = st.text_input("Ticket Subject", "System outage on billing module")
    body = st.text_area("Ticket Body", "Users cannot process payments. Getting 500 errors.")
    
    if st.button("Triage Ticket"):
        with st.spinner("Analyzing..."):
            res = requests.post(f"{BASE_URL}/triage", json={"subject": subject, "body": body})
            if res.status_code == 200:
                st.json(res.json())
            else:
                st.error("Error connecting to API")

with tab2:
    st.header("TAM Account Health Summariser")
    
    # 1. Provide common valid accounts AND a manual entry option
    options = ["ACC-3336", "ACC-1001", "ACC-1002", "Other (Type manually)"]
    selected_option = st.selectbox("Select Account ID", options)
    
    # 2. Reveal text box if they choose manual entry
    if selected_option == "Other (Type manually)":
        account_id = st.text_input("Enter Account ID manually", placeholder="e.g., ACC-1234")
    else:
        account_id = selected_option
        
    if st.button("Generate Brief"):
        # Guardrail: Ensure they didn't leave it blank
        if not account_id or account_id.strip() == "":
            st.warning("Please provide an Account ID to search.")
        else:
            with st.spinner(f"Compiling insights for {account_id}..."):
                res = requests.get(f"{BASE_URL}/tam/brief/{account_id.strip()}")
                
                # Success parsing
                if res.status_code == 200:
                    data = res.json()
                    st.subheader(f"{data['company_name']} ({data['account_id']})")
                    st.write("**Executive Summary:**", data['executive_summary'])
                    
                    st.write("**Open Risks:**")
                    if not data['open_risks']:
                        st.success("No open risks or escalations detected.")
                    else:
                        for risk in data['open_risks']:
                            st.warning(f"**{risk['risk_type']}**: {risk['description']} (Ticket: {risk['ticket_id']})")
                            st.info(f"Quote: \"{risk['justification_quote']}\"")
                    
                    st.write("**Talking Points:**")
                    for pt in data['talking_points']:
                        st.write(f"- {pt}")
                
                # Handled Missing Account
                elif res.status_code == 404:
                    st.error(f"❌ Account ID '{account_id}' not found in the dataset.")
                
                # Server Error
                else:
                    st.error(f"Error generating brief: {res.text}")