# Phase 2: Compliance Engine - Architecture & Implementation Plan

**Status:** In Progress  
**Phase Duration:** Estimated 3-4 weeks  
**Target Completion:** December 2025

---

## 1. Phase 2 Overview

Phase 2 extends the core API with:

- **Compliance Rules Engine** - HIPAA, GDPR, PCI-DSS compliance rules
- **Risk Scoring** - Quantified risk levels for detected violations
- **Redaction Engine** - Multiple strategies to safely redact sensitive data
- **Async Processing** - Offload heavy tasks to Celery workers
- **Webhook Notifications** - Real-time event notifications
- **Token Tracking** - Usage-based billing foundation
- **Enhanced Logging** - Encrypted audit trails

---

## 2. Architecture Design

### 2.1 New Modules

```
app/
├── compliance/
│   ├── __init__.py
│   ├── engine.py              # ComplianceEngine class
│   ├── rules.py               # Rule loading & evaluation
│   ├── models.py              # ComplianceRule data classes
│   └── definitions/
│       ├── hipaa.yaml         # HIPAA rules
│       ├── gdpr.yaml          # GDPR rules
│       └── pci_dss.yaml       # PCI-DSS rules
│
├── redaction/
│   ├── __init__.py
│   ├── strategies.py          # Redaction strategy implementations
│   ├── service.py             # RedactionService
│   └── tests.py               # Redaction tests
│
├── risk_scoring/
│   ├── __init__.py
│   ├── calculator.py          # Risk calculation logic
│   └── scoring_rules.py       # Severity and weighting rules
│
├── webhooks/
│   ├── __init__.py
│   ├── models.py              # WebhookConfig model
│   ├── service.py             # Webhook sending logic
│   └── handlers.py            # Event handlers
│
└── billing/
    ├── __init__.py
    ├── token_counter.py       # Token counting (tiktoken)
    └── usage_tracker.py       # Usage tracking and reporting

workers/
├── tasks.py                   # Celery task definitions
└── celery_app.py              # Celery configuration

tests/
├── test_compliance.py
├── test_redaction.py
├── test_risk_scoring.py
├── test_webhooks.py
└── test_billing.py
```

### 2.2 Data Flow Diagram

```
Request → Auth → Rate Limit → Parse
   ↓
PII Detection
   ↓
Injection Detection
   ↓
Compliance Check (HIPAA/GDPR/PCI-DSS)
   ↓
Risk Calculation
   ↓
Redaction (if needed)
   ↓
Token Counting
   ↓
Log to Database
   ↓
Trigger Webhooks
   ↓
Return Response / Queue Async Task
```

### 2.3 Enhanced Response Format

```json
{
  "request_id": "uuid",
  "status": "completed",
  "detections": {
    "pii_found": true,
    "entities": [...],
    "injection_detected": false,
    "injection_score": 0.0234
  },
  "compliance": {
    "frameworks_checked": ["HIPAA", "GDPR", "PCI-DSS"],
    "violations": [
      {
        "framework": "HIPAA",
        "rule": "no_health_identifiers",
        "severity": "high",
        "message": "Medical record number detected"
      }
    ],
    "status": "compliant"
  },
  "risk": {
    "overall_score": 0.78,
    "level": "HIGH",
    "factors": [
      {"type": "pii", "weight": 0.5, "score": 1.0},
      {"type": "injection", "weight": 0.3, "score": 0.0},
      {"type": "compliance", "weight": 0.2, "score": 0.9}
    ]
  },
  "redaction": {
    "applied": true,
    "sanitized_prompt": "My name is [PERSON] and..."
  },
  "billing": {
    "input_tokens": 15,
    "output_tokens": 42,
    "total_tokens": 57
  }
}
```

---

## 3. Implementation Details

### 3.1 Compliance Engine

#### ComplianceRule Model

```python
class ComplianceRule:
    id: str                    # e.g., "HIPAA_PHI_001"
    framework: str             # "HIPAA", "GDPR", "PCI-DSS"
    name: str                  # "No Protected Health Information"
    severity: str              # "critical", "high", "medium", "low"
    description: str

    # Evaluation logic
    patterns: List[str]        # Regex patterns to check
    entity_types: List[str]    # PII types to block (e.g., ["SSN", "MEDICAL_ID"])
    keywords: List[str]        # Keywords that trigger rule

    # Compliance actions
    action: str                # "block", "redact", "flag"
    remediation: str           # User-friendly fix message
```

#### HIPAA Rules Example

```yaml
framework: HIPAA
name: "Protected Health Information (PHI)"
description: "HIPAA prohibits transmission of Protected Health Information"
rules:
  - id: HIPAA_001
    name: "Medical Record Numbers"
    severity: critical
    entity_types: [MEDICAL_ID]
    action: block
    remediation: "Remove all medical record numbers before submission"

  - id: HIPAA_002
    name: "Health Insurance Numbers"
    severity: high
    patterns: ["\\d{10,12}"] # Insurance ID patterns
    action: redact
    remediation: "Health insurance IDs will be redacted"
```

### 3.2 Redaction Service

#### Redaction Strategies

```python
class RedactionStrategy(Enum):
    FULL_MASK = "***"           # Replace entire entity with ***
    PARTIAL_MASK = "J*** D***"  # Keep first and last chars
    HASH = "[HASH_abc123]"      # Replace with hash reference
    TOKEN = "[PII_PERSON_001]"  # Replace with token for later lookup
    TYPE_ONLY = "[PERSON]"      # Replace with entity type
    REMOVE = ""                 # Remove entirely
```

**Example**

```python
# Input: "My name is John Doe and SSN is 123-45-6789"

# FULL_MASK
Output: "My name is *** and SSN is ***"

# PARTIAL_MASK
Output: "My name is J*** D*** and SSN is 1**-**-****"

# TOKEN
Output: "My name is [PII_PERSON_001] and SSN is [PII_SSN_001]"

# TYPE_ONLY
Output: "My name is [PERSON] and SSN is [SSN]"
```

### 3.3 Risk Scoring Algorithm

```python
class RiskCalculator:
    """
    Risk Score Formula:

    overall_risk = (
        w_pii * pii_score +
        w_injection * injection_score +
        w_compliance * compliance_score
    )

    Weights:
    - PII Detection: 50% (most critical)
    - Injection Detection: 30% (security threat)
    - Compliance Violations: 20% (regulatory)

    Score Calculation:
    - 0.0-0.3: LOW RISK (green)
    - 0.3-0.6: MEDIUM RISK (yellow)
    - 0.6-0.8: HIGH RISK (orange)
    - 0.8-1.0: CRITICAL RISK (red)
    """
```

**Scoring Details**

- **PII Score**: Number and severity of entities detected

  - Sensitive (SSN, Medical ID): 1.0
  - Moderate (Phone, Email): 0.6
  - Low (Name, Address): 0.3

- **Injection Score**: Direct from model output (0.0-1.0)

- **Compliance Score**: Number and severity of violations
  - Critical violation: 1.0
  - High: 0.7, Medium: 0.4, Low: 0.2

### 3.4 Async Processing Flow

#### Celery Tasks

```python
# workers/tasks.py

@app.task
def detect_pii_task(prompt_id: str, prompt: str):
    """Background task for PII detection"""

@app.task
def detect_injection_task(prompt_id: str, prompt: str):
    """Background task for injection detection"""

@app.task
def evaluate_compliance_task(prompt_id: str, prompt: str, frameworks: List[str]):
    """Background task for compliance evaluation"""

@app.task
def redact_prompt_task(prompt_id: str, entities: List[dict], strategy: str):
    """Background task for redaction"""

@app.task
def send_webhook_task(webhook_id: str, event_data: dict):
    """Background task for webhook delivery"""

@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # Periodic token usage aggregation
    sender.add_periodic_task(300.0, aggregate_token_usage.s())
```

#### API Endpoints

```python
# Synchronous (existing)
POST /v1/analyze

# Asynchronous (new)
POST /v1/analyze?async=true
  → Returns 202 Accepted with request_id

GET /v1/status/{request_id}
  → Returns current status and results (when ready)

POST /v1/webhooks
  → Create webhook subscription

DELETE /v1/webhooks/{webhook_id}
  → Remove webhook
```

### 3.5 Token Tracking

```python
# Using tiktoken for accurate OpenAI token counting

class TokenCounter:
    """Count tokens using tiktoken (OpenAI's token encoder)"""

    def count_tokens(prompt: str) -> int:
        """Count input tokens"""

    def count_tokens_for_response(response: str) -> int:
        """Count output tokens"""

# Store in AuditLog
audit_log.tokens_analyzed = token_counter.count_tokens(prompt)
audit_log.tokens_billable = calculate_billable_tokens(tokens_analyzed, tier)
```

---

## 4. Implementation Roadmap

### Phase 2.1: Core Compliance Engine (Week 1)

- [ ] Create compliance module structure
- [ ] Implement ComplianceRule and ComplianceEngine
- [ ] Define HIPAA/GDPR/PCI-DSS rules in YAML
- [ ] Create rule loader and evaluator
- [ ] Unit tests for compliance engine

### Phase 2.2: Redaction Service (Week 1-2)

- [ ] Implement all redaction strategies
- [ ] Create RedactionService
- [ ] Integrate with PII detection
- [ ] Add redaction tests

### Phase 2.3: Risk Scoring (Week 2)

- [ ] Implement RiskCalculator
- [ ] Create weighting algorithm
- [ ] Integrate with compliance violations
- [ ] Add tests

### Phase 2.4: Async Processing (Week 2-3)

- [ ] Set up Celery configuration
- [ ] Create task definitions
- [ ] Update docker-compose
- [ ] Implement task retry logic

### Phase 2.5: Async API Endpoints (Week 3)

- [ ] Add async parameter to /v1/analyze
- [ ] Implement /v1/status/{request_id}
- [ ] Result storage in database
- [ ] Response status logic

### Phase 2.6: Token Tracking (Week 3)

- [ ] Integrate tiktoken
- [ ] Implement token counting
- [ ] Add to audit logging
- [ ] Create billing models

### Phase 2.7: Webhooks (Week 4)

- [ ] Create webhook models
- [ ] Implement webhook endpoint
- [ ] Add HMAC signing
- [ ] Integrate with async flow

### Phase 2.8: Enhanced Logging & Tests (Week 4)

- [ ] Implement log encryption
- [ ] Add key management
- [ ] Comprehensive testing
- [ ] Documentation updates

---

## 5. Database Schema Updates

### New Tables

```sql
-- Compliance rules (loaded from YAML)
CREATE TABLE compliance_rules (
    id VARCHAR PRIMARY KEY,
    framework VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    severity VARCHAR NOT NULL,
    patterns JSON,
    entity_types JSON,
    action VARCHAR,
    created_at TIMESTAMP
);

-- Webhook configurations
CREATE TABLE webhooks (
    id UUID PRIMARY KEY,
    api_key_id UUID FOREIGN KEY,
    event_types JSON,  -- ["pii.detected", "injection.detected", ...]
    url VARCHAR NOT NULL,
    secret VARCHAR NOT NULL,  -- For HMAC signing
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Async task results
CREATE TABLE task_results (
    request_id UUID PRIMARY KEY,
    api_key_id UUID FOREIGN KEY,
    status VARCHAR,  -- "pending", "processing", "completed", "failed"
    result JSON,
    error_message VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    expires_at TIMESTAMP
);

-- Token usage tracking
CREATE TABLE token_usage (
    id SERIAL PRIMARY KEY,
    api_key_id UUID FOREIGN KEY,
    request_id UUID FOREIGN KEY,
    input_tokens INTEGER,
    output_tokens INTEGER,
    billable_tokens INTEGER,
    created_at TIMESTAMP
);
```

### Updated AuditLog Table

```python
# Add to existing AuditLog model
compliance_violations: JSON      # Array of violations
risk_score: DECIMAL(5,4)         # Overall risk 0.0-1.0
risk_level: VARCHAR              # LOW, MEDIUM, HIGH, CRITICAL
redaction_applied: BOOLEAN
redaction_strategy: VARCHAR
tokens_analyzed: INTEGER
tokens_billable: INTEGER
```

---

## 6. Configuration Files

### Requirements Update

```txt
# New for Phase 2
celery==5.3.0
redis==5.0.0  # For Celery broker
tiktoken==0.5.0  # Token counting
cryptography==41.0.0  # Encryption
pydantic-settings==2.0.0  # Config management
python-dotenv==1.0.0
requests==2.31.0  # For webhooks
pydantic[email]==2.0.0
```

### Environment Variables (.env)

```env
# Celery Configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
CELERY_TASK_TIME_LIMIT=300

# Encryption
ENCRYPTION_KEY=<generated-key>

# Webhook settings
WEBHOOK_TIMEOUT=30
WEBHOOK_MAX_RETRIES=3
WEBHOOK_RETRY_DELAY=60

# Token counting
TIKTOKEN_CACHE_DIR=/tmp/tiktoken

# Compliance rules path
COMPLIANCE_RULES_PATH=/app/compliance/definitions/
```

---

## 7. Testing Strategy

### Unit Tests

- [ ] ComplianceEngine rule loading and evaluation
- [ ] All RedactionStrategy implementations
- [ ] RiskCalculator algorithm
- [ ] TokenCounter accuracy
- [ ] WebhookService delivery and retry logic

### Integration Tests

- [ ] End-to-end /v1/analyze with all features
- [ ] Async flow from request to completion
- [ ] Webhook triggering and delivery
- [ ] Database logging and retrieval

### Performance Tests

- [ ] Async processing throughput
- [ ] Large prompt handling (10K+ tokens)
- [ ] Webhook batch delivery
- [ ] Database query performance

---

## 8. Success Criteria

✅ Phase 2 is complete when:

1. **Compliance Engine**

   - Loads and evaluates HIPAA/GDPR/PCI-DSS rules
   - Correctly identifies compliance violations
   - Suggests remediation actions

2. **Redaction Service**

   - All 6 redaction strategies implemented
   - Works with all PII types
   - Maintains data integrity

3. **Risk Scoring**

   - Calculates accurate risk scores (0.0-1.0)
   - Properly weights different risk factors
   - Matches real-world threat levels

4. **Async Processing**

   - Tasks queue and process correctly
   - Status tracking works reliably
   - Results persist after completion

5. **Webhooks**

   - Events fire correctly
   - HMAC signatures verify
   - Retries work on failure

6. **Token Tracking**

   - Accurate token counting
   - Proper billing calculation
   - Usage reports available

7. **Testing**
   - 90%+ code coverage
   - All integration tests pass
   - Performance benchmarks met

---

## 9. Next Steps

**Ready to begin implementation?**

1. Create compliance module structure
2. Define compliance rules in YAML
3. Implement ComplianceRule/ComplianceEngine classes
4. Create unit tests for compliance
5. Build redaction service

**Let's start Phase 2.1 now!**
