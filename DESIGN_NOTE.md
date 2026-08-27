# System Design Note

## 1. Failure Modes
**Top 3 ways the solution could fail in production and mitigations:**
*   **LLM Hallucinations on Urgency:** The LLM might misclassify a P3 ticket as P1 due to emotive customer language. *Mitigation:* Implement a secondary deterministic rule-engine (e.g., if ticket mentions "billing", cap urgency at P3) and flag low-confidence LLM outputs for human-in-the-loop review.
*   **Vector Database Retrieval Misses:** The local sentence-transformer might fail to match a ticket to the KB if the customer uses non-standard terminology. *Mitigation:* Implement hybrid search (BM25 keyword search + semantic vector search) and track "zero-hit" queries to improve KB documentation.
*   **Third-Party API Outages (Groq/LLM):** The external LLM provider goes down, blocking the triage pipeline. *Mitigation:* Implement exponential backoff retries and maintain a fallback connection to a secondary provider (e.g., Azure OpenAI) or a small, locally hosted SLM (Small Language Model).

## 2. Latency vs. Quality
**Concrete Trade-off:** We traded slight semantic accuracy for zero API latency and zero cost by using a local `all-MiniLM-L6-v2` embedding model instead of OpenAI's `text-embedding-3`.
**If Latency were the Hard Constraint:** I would entirely remove the generative LLM draft response from Task 1. Classification (Product Area, Urgency) is much faster than text generation. For ultra-low latency, I would route triage through a fine-tuned BERT classification model (sub-50ms response) rather than a generative LLM prompt.

## 3. Data Sensitivity
**Handling PII:** Support tickets and account data frequently contain PII (emails, API keys, phone numbers). To prevent leaking this to external LLM APIs (like Groq), the system should integrate a PII scrubbing middleware (like Microsoft Presidio) to mask sensitive entities before the payload leaves our VPC. The scrubbed entities would be temporarily cached and re-injected into the LLM's response post-generation.

## 4. Scaling
**10x Ticket Volume:** If ticket volume scales 10x, the synchronous FastAPI `POST /triage` endpoint will bottleneck and time out as multiple requests wait for the LLM API to respond. 
**What breaks first:** The blocking HTTP connections and external LLM API rate limits.
**Mitigation:** Transition to an asynchronous, event-driven architecture. Incoming tickets should be published to a message broker (e.g., RabbitMQ or Kafka). Celery workers will consume the queue, process the LLM calls in parallel batches, and write the structured output to a database.