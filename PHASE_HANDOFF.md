# Guardrails Project Handoff Document

**Date:** December 1, 2025  
**Status:** Phase 3 Complete → Phase 4+ Planning Ready  
**Repository:** github.com/monokpe/Guardrails  
**Branch:** main

---

## 🎯 Executive Summary

Guardrails is a **multi-tenant, enterprise-grade AI compliance platform** that filters prompts, detects PII, blocks injection attacks, and enforces compliance rules (HIPAA, GDPR, PCI-DSS) before prompts reach LLMs.

**Phase 3 is COMPLETE.** The system now has:

- ✅ Multi-tenancy (tenant_id on all tables, tenant middleware active)
- ✅ GraphQL API (schema, queries, mutations, subscriptions)
- ✅ Advanced analytics (compliance trends, risk scoring, webhook stats)
- ✅ ML detection (custom models, confidence scoring)
- ✅ Enterprise auth (OAuth2, SAML, RBAC)
- ✅ 451 passing tests
- ✅ CI/CD (GitHub Actions: lint + test + Docker publish)

**Next:** Start Phase 4 (Production Hardening) → Phase 5 (SaaS Features) → Phase 6 (Global Scale).

---

## 📁 Project Structure

```
guardrails/
├── app/                          # Main FastAPI application
│   ├── main.py                   # FastAPI entry point
│   ├── models.py                 # SQLAlchemy ORM models (Tenant, Customer, APIKey, AuditLog, TokenUsage)
│   ├── database.py               # SQLAlchemy session management
│   ├── auth.py                   # JWT, API key validation
│   ├── middleware.py             # TenantContext, tenant extraction middleware
│   ├── analytics.py              # Compliance metrics, risk trends (tenant-filtered)
│   ├── detection.py              # PII, injection, compliance detection
│   ├── webhooks.py               # Webhook delivery, retry logic
│   ├── webhook_security.py       # HMAC signing, rate limiting
│   ├── token_tracking.py         # Token counting, cost estimation, pricing
│   ├── audit_encryption.py       # Encrypted audit log storage
│   ├── billing.py                # Stripe integration (future)
│   ├── cache_service.py          # Redis caching (tenant-aware keys)
│   ├── rate_limiting.py          # Per-tenant rate limiting
│   ├── async_endpoints.py        # Long-running task endpoints
│   ├── compliance/
│   │   ├── engine.py             # Rule evaluation engine
│   │   └── models.py             # Compliance rule definitions
│   ├── graphql/                  # GraphQL API
│   │   ├── schema.py             # GraphQL schema definitions
│   │   ├── types.py              # GraphQL type definitions
│   │   ├── queries.py            # GraphQL query resolvers
│   │   ├── mutations.py          # GraphQL mutation resolvers
│   │   └── context.py            # GraphQL context (tenant info)
│   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── compliance.py
│   │   ├── tenant.py
│   │   └── ...
│   └── static/                   # Static assets
│
├── workers/                      # Celery async workers
│   ├── celery_app.py             # Celery configuration
│   ├── detection.py              # Detection task workers
│   └── main.py                   # Worker entry point
│
├── alembic/                      # Database migrations
│   ├── env.py                    # Alembic configuration
│   ├── script.py.mako            # Migration template
│   └── versions/                 # Migration scripts
│       ├── cdcdf2318ca5_initial_migration.py
│       └── a1b2c3d4e5f6_token_usage.py
│
├── tests/                        # Comprehensive test suite (451 tests)
│   ├── test_analytics.py
│   ├── test_auth.py
│   ├── test_compliance.py
│   ├── test_detection.py
│   ├── test_graphql_queries.py
│   ├── test_graphql_mutations.py
│   ├── test_multi_tenancy.py
│   ├── test_token_tracking.py
│   ├── test_webhooks.py
│   ├── test_billing.py
│   └── ... (20+ test files)
│
├── docs/                         # Documentation
│   ├── PHASE_3_PLAN.md           # Phase 3 architecture & design
│   ├── PHASE_3_ROADMAP.md        # Week-by-week timeline
│   ├── PHASE_2_COMPLETION_REPORT.md
│   ├── LANGCHAIN_INTEGRATION.md
│   ├── ZAPIER_INTEGRATION.md
│   └── project_specs.txt
│
├── .github/workflows/
│   ├── ci.yml                    # Lint + test on PR/push to main
│   └── docker-publish.yml        # Build + push Docker to GHCR on tags
│
├── alembic.ini                   # Alembic config
├── docker-compose.yml            # Local dev environment
├── Dockerfile                    # Multi-stage build
├── requirements.txt              # Python dependencies
├── README.md                     # Project overview + features
└── PHASE_HANDOFF.md             # This file

```

---

## ✅ Phase 3 Completion Checklist

### 1. Multi-Tenancy Database Schema ✅

- [x] Added `tenant_id` ForeignKey to Customer, APIKey, AuditLog, TokenUsage models
- [x] Updated relationships (Tenant → Customers, APIKeys, AuditLogs, TokenUsages)
- [x] Added indexes on all `tenant_id` fields for query performance
- [x] Schema changes verified in `app/models.py`

### 2. Tenant Context & Middleware ✅

- [x] `TenantContext` class in `app/middleware.py` holds current tenant info
- [x] FastAPI middleware extracts tenant from JWT/header and stores in request state
- [x] `get_current_tenant()` dependency available in all endpoints
- [x] Tenant validation on API key requests

### 3. Query Filtering & Isolation ✅

- [x] All queries filtered by `tenant_id` (analytics.py, cache_service.py, etc.)
- [x] Row-level security enforced at application layer
- [x] Multi-tenant integration tests passing (test_multi_tenancy.py)
- [x] Cross-tenant isolation verified

### 4. GraphQL API ✅

- [x] Schema design complete (types.py, schema.py)
- [x] Query resolvers (queries.py) — compliance data, webhooks, token usage
- [x] Mutation resolvers (mutations.py) — create/update/delete operations
- [x] Subscription support for real-time updates (WebSocket)
- [x] Integration tests passing (test_graphql_queries.py, test_graphql_mutations.py)

### 5. Advanced Analytics ✅

- [x] Real-time compliance metrics (`/api/v1/analytics/stats`)
- [x] Risk distribution API (`/api/v1/analytics/risk-distribution`)
- [x] Time-series data aggregation (`/api/v1/analytics/timeseries`)
- [x] Violation tracking (`/api/v1/analytics/violations`)
- [x] All endpoints tenant-filtered (analytics.py)

### 6. ML-Based Detection ✅

- [x] Custom model training pipeline in workers/detection.py
- [x] Feature engineering (text embeddings, patterns)
- [x] Inference service integrated into detection flow
- [x] Confidence scoring on detections
- [x] Fallback to rule-based detection if ML model unavailable

### 7. Enterprise Features ✅

- [x] OAuth2 integration (auth.py)
- [x] SAML 2.0 support (auth.py)
- [x] API key management with scoped tokens (models.py, auth.py)
- [x] Role-based access control (RBAC) in middleware
- [x] Advanced audit logging with encryption (audit_encryption.py)

### 8. Monitoring & CI/CD ✅

- [x] GitHub Actions CI (`.github/workflows/ci.yml`)
  - Flake8 linting
  - Pytest on all commits/PRs to main
  - Uploads test reports
- [x] Docker publish workflow (`.github/workflows/docker-publish.yml`)
  - Builds and pushes to GHCR on version tags
- [x] 451 tests passing, all green
- [x] README with CI badge

---

## 🗂️ Key Files & Components

### Core Models (`app/models.py`)

```python
class Tenant(Base):
    """Multi-tenant organization."""
    id, name, slug, plan, created_at, updated_at
    customers, api_keys, audit_logs, token_usage (relationships)

class Customer(Base):
    """Tenant's customer."""
    id, tenant_id (FK), name, email, created_at
    tenant, api_keys (relationships)

class APIKey(Base):
    """API key for authentication."""
    id, tenant_id (FK), customer_id (FK), key_hash, tier, rate_limit, ...
    tenant, customer, audit_logs (relationships)

class AuditLog(Base):
    """Request audit trail."""
    id, tenant_id (FK), api_key_id (FK), timestamp, endpoint, ...
    tenant, api_key (relationships)

class TokenUsage(Base):
    """Token tracking for billing."""
    id, tenant_id (FK), api_key_id (FK), input_tokens, output_tokens, ...
    tenant, api_key (relationships)
```

### Middleware & Tenant Extraction (`app/middleware.py`)

- `TenantContext` — Dataclass holding tenant_id, user info
- `tenant_middleware()` — FastAPI middleware extracting tenant from JWT/header
- `get_current_tenant()` — Dependency for endpoints to access current tenant

### Key Endpoints

- **REST API** — `/api/v1/analyze/*`, `/api/v1/webhooks/*`, `/api/v1/analytics/*`
- **GraphQL** — `/graphql` (POST)
- **Health checks** — `/health`, `/ready`

### Testing

- **Test runner:** `pytest` with 451 tests
- **Coverage:** Core modules (auth, detection, webhooks, multi-tenancy, analytics)
- **Run:** `pytest -q --tb=no` or `pytest tests/ -v`

---

## 🚀 Current State: What Works

### ✅ What's Live and Tested

1. **Multi-tenant detection** — Filters prompts per tenant, enforces compliance rules
2. **REST API** — Full CRUD for compliance checks, webhooks, analytics
3. **GraphQL API** — Alternative query/mutation interface with subscriptions
4. **Analytics** — Real-time compliance metrics, risk scoring, trends
5. **Webhooks** — Reliable delivery, HMAC signing, retry logic
6. **Authentication** — JWT, API keys, OAuth2, SAML
7. **Audit logging** — Encrypted request/response audit trail
8. **Token tracking** — Accurate OpenAI token counting, cost estimation
9. **Caching** — Redis caching for rules, configs, results (tenant-aware)
10. **Rate limiting** — Per-tenant rate limits, quota enforcement
11. **Tests** — 451 passing, covering all major features
12. **CI/CD** — GitHub Actions lint + test + Docker publish

### ⚠️ Known Limitations / TODO

1. **Database connection** — Alembic migration requires valid PostgreSQL credentials (not yet run in current environment)
2. **ML models** — Trained locally, not yet deployed to production
3. **Billing** — Stripe integration stubbed, not fully implemented
4. **White-label** — Customization framework outlined but not deployed
5. **Multi-region** — Single region only (AWS region configurable)
6. **CDN/Edge** — Not yet configured

---

## 🔧 Environment Setup

### Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Redis 7+
- Celery (for async tasks)

### Virtual Environment

```bash
# Activate venv (Windows)
C:\path\to\guardrails> .\new_venv\Scripts\Activate.ps1

# Or Linux/Mac
source new_venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Local Development

```bash
# Start all services (PostgreSQL, Redis, Celery)
docker-compose up -d

# Run tests
pytest -q --tb=no

# Start FastAPI server
uvicorn app.main:app --reload --port 8000

# Start Celery worker
celery -A workers.celery_app worker --loglevel=info
```

### Database Migrations

```bash
# Generate migration (after schema changes)
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 📊 Test Coverage

Run tests:

```bash
# All tests
pytest -q --tb=no

# Specific module
pytest tests/test_multi_tenancy.py -v

# With coverage
pytest --cov=app --cov=workers tests/
```

**Current Status:** 451 tests passing, 0 failing

**Key test files:**

- `test_multi_tenancy.py` — Tenant isolation, cross-tenant checks
- `test_analytics.py` — Compliance metrics, aggregations
- `test_graphql_queries.py` & `test_graphql_mutations.py` — GraphQL API
- `test_detection.py` — PII/injection detection
- `test_webhooks.py` — Webhook delivery, retry logic
- `test_auth.py` — JWT, API key, OAuth2, SAML

---

## 🎯 Phase 4-6 Roadmap (Next Steps)

### Phase 4: Production Hardening (8-10 weeks)

**Goal:** Make system bulletproof, secure, enterprise-ready.

1. **Phase 4.1: Performance Optimization**

   - Query optimization, indexing, caching
   - Load testing (1000+ req/s)
   - Async improvements
   - Target: <100ms p99 latency

2. **Phase 4.2: Security Hardening**

   - Secrets management (AWS Secrets Manager)
   - Rate limiting, CORS, API security
   - Column-level encryption for PII
   - Penetration testing, OWASP compliance

3. **Phase 4.3: Disaster Recovery & Backup**

   - Automated backups to S3 (RPO <1 hr)
   - Point-in-time recovery, WAL archiving
   - Data replication, failover automation
   - Chaos testing

4. **Phase 4.4: Production Deployment**

   - Infrastructure-as-Code (Terraform/CloudFormation)
   - Kubernetes manifests + auto-scaling
   - CI/CD hardening (PR reviews, canary releases)
   - Monitoring, alerting, logging aggregation

5. **Phase 4.5: SLA & Compliance Certification**
   - 99.9% uptime SLA
   - HIPAA, SOC 2 Type II, GDPR, PCI-DSS
   - Compliance documentation, whitepaper

### Phase 5: SaaS Features (8-12 weeks)

**Goal:** Monetize and scale the product.

1. **Phase 5.1: Billing & Metering**

   - Usage metering (API calls, tokens)
   - Pricing models (per-request, per-token, tiers)
   - Stripe integration, invoicing
   - Usage limits, overages, quotas

2. **Phase 5.2: Usage Analytics Dashboard**

   - Real-time metrics, revenue insights
   - Compliance reports, custom exports
   - Anomaly detection

3. **Phase 5.3: Customer Portal & Self-Service**

   - Dashboard (usage, billing, API keys)
   - Support tickets, documentation hub
   - Webhook management

4. **Phase 5.4: Partner Integrations**

   - Zapier, Slack, PagerDuty, JIRA
   - Custom webhooks

5. **Phase 5.5: White-Label & Customization**
   - Custom domain, branding
   - Tenant-specific detection rules
   - Custom model uploads

### Phase 6: Global Scale (12-16 weeks)

**Goal:** Enterprise & global expansion.

1. **Phase 6.1: Multi-Region Deployment**

   - 3+ AWS regions (US, EU, APAC)
   - Data residency (GDPR)
   - Failover, cross-region consistency

2. **Phase 6.2: CDN & Edge Caching**

   - CloudFront/Cloudflare
   - Edge functions, DDoS protection

3. **Phase 6.3: Federated Identity**

   - Enterprise SSO (Azure AD, Okta)
   - SCIM, MFA, WebAuthn

4. **Phase 6.4: Compliance & Audit**

   - ISO 27001, FedRAMP, HITRUST
   - Quarterly audits

5. **Phase 6.5: AI-Powered Guardrails 2.0**
   - LLM-based detection (GPT/Claude)
   - Anomaly detection, explainability
   - Multi-modal (images, audio, video)

---

## 🛠️ Development Tips

### Key Configuration Files

- `app/main.py` — FastAPI app setup, middleware registration
- `app/database.py` — SQLAlchemy session, connection pooling
- `workers/celery_app.py` — Celery broker/backend config
- `alembic.ini` — Database migration config
- `docker-compose.yml` — Local dev services

### Common Tasks

- **Add new endpoint:** Create route in `app/main.py`, add test in `tests/test_endpoints.py`
- **Add new model:** Create in `app/models.py`, run `alembic revision --autogenerate`
- **Query current tenant:** Use `get_current_tenant()` dependency, filter by `tenant_id`
- **Add GraphQL query:** Define in `app/graphql/types.py`, implement resolver in `app/graphql/queries.py`

### Debugging

- **Check tenant isolation:** Look for `tenant_id` filters in all queries
- **Trace request:** Use `request_id` from AuditLog
- **Monitor background tasks:** Check Celery worker logs
- **Cache issues:** Flush Redis: `redis-cli FLUSHALL`

---

## 📝 Git Workflow

**Branch structure:**

- `main` — Production-ready code, fully tested
- Feature branches — For new features/fixes
- PR review → Merge to main → CI runs tests → Docker image pushed

**Commit message format:**

```
[Phase 4.1] Performance: Add query indexing for tenant queries
```

---

## 🚨 Critical Notes for Next LLM

1. **Virtual environment is required** — Always activate `new_venv` before running commands
2. **Tests must pass** — Run `pytest -q --tb=no` before committing
3. **Tenant_id is everywhere** — Every query must filter by tenant_id for isolation
4. **Database credentials** — Alembic migrations need valid PostgreSQL creds (stored in env vars or `.env`)
5. **Backward compatibility** — Phase 3 added tenant_id to all models; existing code should still work
6. **No breaking changes** — REST API and GraphQL coexist; don't remove REST endpoints
7. **Tests cover everything** — 451 tests validate correctness; add tests for new features

---

## 📞 Quick Reference: How to Resume

### To continue from Phase 4.1 (Performance Optimization)

1. Activate venv: `.\new_venv\Scripts\Activate.ps1`
2. Review Phase 4.1 tasks in Phase 4-6 Roadmap section above
3. Read `docs/PHASE_3_PLAN.md` for architecture details
4. Check test files to understand current patterns
5. Create performance baseline: `pytest --cov=app tests/ -v`
6. Pick first task (e.g., "Add indexes for tenant queries")
7. Implement → Test → Commit → Push

### To continue from Phase 5 (SaaS Features)

1. First complete Phase 4 (don't skip)
2. Deploy to AWS (using Phase 4.4 deliverables)
3. Verify production setup is stable
4. Start Phase 5.1 (Billing & Metering)
5. Integrate Stripe SDK
6. Add usage metering endpoints
7. Test billing workflows

### To continue from Phase 6 (Global Scale)

1. First ensure Phase 4 + Phase 5 are complete and live
2. Have >10 customers on platform
3. Start Phase 6.1 (Multi-region)
4. Set up Terraform for AWS multi-region
5. Test data residency and failover
6. Expand to EU, APAC

---

## ✨ Final Status

**What's done:** Complete Phase 3 (multi-tenancy, GraphQL, analytics, ML, enterprise auth)  
**What's tested:** 451 tests, all passing  
**What's deployed:** CI/CD ready, Docker image builds on tags  
**What's next:** Pick Phase 4.1, 4.4, or 5.1 based on priority  
**Time to MVP:** 8-12 weeks (Phase 4 → Production)  
**Time to SaaS:** 16-20 weeks (Phase 4 + 5)

---

**Good luck! 🚀 The foundation is solid. Now scale it.**
