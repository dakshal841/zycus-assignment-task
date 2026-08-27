# zycus-assignment-task
# Production-Grade AI for Technical Support & TAM Teams

A robust, full-stack AI internal tooling system built for customer-facing Technical Support and Technical Account Management (TAM) units. The system features an intelligent ticket triage pipeline with Retrieval-Augmented Generation (RAG) and an automated Quarterly Business Review (QBR) account health summarizer.

---

## 🚀 Key Features

* **Task 1: Intelligent Ticket Triage Agent**
  * Ingests raw tickets (subject + body)[cite: 1] and classifies them into product areas, issue categories, and urgency tiers (`P1`–`P4`)[cite: 1] using strict Pydantic structured outputs.
  * Performs local semantic search across the product knowledge base to surface relevant documentation[cite: 1].
  * Generates a recommended responder team and a draft professional first-response message[cite: 1].
  * Exposed via a high-performance **FastAPI** REST endpoint (`POST /triage`)[cite: 1].

* **Task 2: TAM Account Health Summariser**[cite: 1]
  * Pulls account context and filters the last 90 days of tickets for a given `account_id`[cite: 1].
  * Auto-generates a 3-section QBR brief: Executive Summary, Open Risks with verbatim ticket quote justifications, and Actionable TAM Talking Points[cite: 1].
  * Engineered for determinism (`temperature=0.0`)[cite: 1].

* **Task 3: Evaluation Harness**[cite: 1]
  * Systematic evaluation script (`evaluate.py`) testing standard and adversarial cases (vague tickets, missing accounts)[cite: 1].
  * Reports rule-based quality scores and pass/fail metrics, exporting results to `eval_report.json`[cite: 1].

* **Bonus Streamlit UI**[cite: 1]
  * A lightweight interactive web application (`app.py`) allowing non-technical TAMs and support leads to interact with both pipelines seamlessly[cite: 1].

---

## 📂 Project Structure

```text
ai-support-internship/
├── data/                 # Mock dataset (tickets, accounts, KB markdown files)
├── src/                  
│   ├── triage.py         # Task 1: FastAPI app & triage logic
│   ├── summarizer.py     # Task 2: TAM brief generation logic
│   ├── rag.py            # Local ChromaDB vector store & embeddings
│   └── schemas.py        # Pydantic data models for structured outputs
├── tests/                # Unit/Integration tests
├── app.py                # Streamlit UI demo (+5 Bonus)
├── evaluate.py           # Task 3 Evaluation harness
├── eval_report.json      # Evaluation results report[cite: 1]
├── DESIGN_NOTE.md        # Task 4 Written architectural design note[cite: 1]
├── .env.example          # Environment variables template[cite: 1]
├── requirements.txt      # Python dependencies
└── README.md

🛠️ Setup & Installation Instructions
1. Clone the Repository & Set Up Virtual Environment
Bash
git clone [https://github.com/dakshal841/zycus-assignment-task.git](https://github.com/dakshal841/zycus-assignment-task.git)
cd zycus-assignment-task

python -m venv venv
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
2. Install Dependencies
Bash
pip install --upgrade pip
pip install -r requirements.txt
3. Configure Environment Variables
Create a .env file in the root directory based on .env.example:

Code snippet
GROQ_API_KEY=your_groq_api_key_here
(Ensure .env is never committed to version control).

🏃‍♂️ Running the Application
Step 1: Start the FastAPI Backend
Launch the backend server using Uvicorn:

Bash
uvicorn src.triage:app --reload
The API will run locally at http://127.0.0.1:8000. You can explore interactive API docs at http://127.0.0.1:8000/docs.

Step 2: Run the Streamlit UI Demo (Optional Bonus)
In a separate terminal window with your virtual environment activated, launch the UI[cite: 1]:

Bash
streamlit run app.py
Step 3: Run the Evaluation Harness
Execute the evaluation script to test both pipelines and generate the score report[cite: 1]:

Bash
python evaluate.py
📝 Sample API Runs
Task 1: Ticket Triage (POST /triage)
Request Body:

JSON
{
  "subject": "Request: bulk archive entries in DataBridge Pro Data Ingestion",
  "body": "Currently DataBridge Pro only allows individual archive entries in the Data Ingestion module. As our usage has scaled to 116 users we urgently need bulk operations."
}
Task 2: TAM Account Brief (GET /tam/brief/{account_id})
Example endpoint URL: http://127.0.0.1:8000/tam/brief/ACC-3336

📄 Task 4: Design Note Summary
For a complete breakdown, see DESIGN_NOTE.md.

Failure Modes & Mitigations: Addressed LLM hallucinations on urgency by coupling outputs with deterministic fallback rules and tracking vector database retrieval misses.

Latency vs. Quality: Optimized speed and cost by leveraging local sentence-transformer embeddings (all-MiniLM-L6-v2) instead of paid API calls.

Data Sensitivity: Proposed PII-masking middleware (e.g., Microsoft Presidio) to scrub sensitive fields prior to external LLM processing.

Scaling (10x Volume): Outlined transition from synchronous FastAPI routes to an asynchronous Celery message queue architecture to handle increased throughput.


Save this file as `README.md` in your root directory, commit it using Git, and you will have a pristine, professional repository ready for your Loom recording!