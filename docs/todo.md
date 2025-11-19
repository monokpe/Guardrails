### Phase 1 TODO List

**Done:**
*   Basic FastAPI app structure (`app/main.py`).
*   Health check endpoint (`/v1/health`).
*   Placeholder for the `/v1/analyze` endpoint.
*   Docker and Docker Compose setup for the API, database, and Redis.
*   Project dependencies listed in `requirements.txt`.
*   **Database Setup:** Defined schema and ran initial migration.
*   **Authentication:** Implemented API key authentication.
*   **Rate Limiting:** Implemented rate limiting for the API.
*   **PII Detection:** Implemented the core PII detection logic.
*   **API Endpoints:** Completed the `/v1/analyze` endpoint logic.
*   **Logging:** Implemented structured logging to the database.
*   **Testing:** Wrote unit tests for the new functionality.

**TODO:**

All tasks for Phase 1 are complete!

### Phase 2 TODO List

**TODO:**

*   **Prompt Injection Detection:**
    *   [x] Set up HuggingFace Transformers library.
    *   [x] Integrate DistilBERT model for prompt injection classification.
    *   [/] Create a service to process text and return an injection score.
    *   [ ] Add unit tests for the injection detection service.

*   **Compliance Engine:**
    *   [ ] Design and implement the `ComplianceRule` and `ComplianceEngine` classes.
    *   [ ] Define HIPAA, GDPR, and PCI-DSS rules in a structured format (e.g., YAML or JSON).
    *   [ ] Implement the logic to load and evaluate rules based on the request context.
    *   [ ] Write tests for each compliance framework's rules.

*   **Redaction Service:**
    *   [ ] Implement different redaction strategies (full mask, token replacement, etc.).
    *   [ ] Create a service that takes text and a list of entities to redact.
    *   [ ] Integrate the redaction service into the main processing flow.
    *   [ ] Add tests for all redaction strategies.

*   **Async Processing with Celery:**
    *   [ ] Install and configure Celery with a message broker (Redis).
    *   [ ] Create Celery tasks for detection, compliance, and redaction.
    *   [ ] Refactor the `/v1/analyze` endpoint to offload processing to Celery tasks.
    *   [ ] Set up Celery workers in the Docker Compose configuration.

*   **Async API Endpoints:**
    *   [ ] Modify the `/v1/analyze` endpoint to support an `async` parameter.
    *   [ ] When `async` is true, return a `202 Accepted` response with a `request_id`.
    *   [ ] Implement the `GET /v1/status/{request_id}` endpoint to check the status and retrieve results.
    *   [ ] Store and retrieve task status/results from a persistent store (e.g., Redis or PostgreSQL).

*   **Webhook Notifications:**
    *   [ ] Create database models for storing webhook configurations.
    *   [ ] Implement a `POST /v1/webhooks` endpoint to create/manage webhooks.
    *   [ ] Create a service to send webhook notifications for specified events (e.g., `pii.detected`).
    *   [ ] Integrate webhook calls into the async processing flow.
    *   [ ] Implement HMAC signature generation for webhook security.

*   **Enhanced Audit Logging:**
    *   [ ] Implement encryption for sensitive data in audit logs (e.g., the original prompt).
    *   [ ] Use a secure key management solution (like AWS KMS, or a local alternative for now).
    *   [ ] Update the audit logging service to include the encrypted data.
    *   [ ] Ensure that access to decrypted data is restricted and audited.

*   **Token Usage & Deduplication:**
    *   [ ] Design a schema to track token usage per API key (input/output tokens).
    *   [ ] Implement logic to count tokens for each `/v1/analyze` request.
    *   [ ] Store token counts in the database, associated with the request log.
    *   [ ] (Optional) Implement a caching mechanism (e.g., Redis) for request deduplication to avoid re-processing identical prompts in a short time frame.
    