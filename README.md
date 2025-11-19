# Guardrails API

A high-performance, multi-tenant API for real-time content filtering, PII detection, and prompt injection prevention.

## Features
- **Multi-Tenancy**: Strict data isolation for multiple customers.
- **Real-time Analysis**: Detects PII and prompt injection attacks in milliseconds.
- **GraphQL API**: Flexible querying for tenants, logs, and analysis.
- **Analytics Dashboard**: Visual insights into usage and security threats.
- **Request Deduplication**: Redis-based caching for identical prompts.

## Quick Start

### Prerequisites
- Python 3.12+
- Redis (optional, for caching)
- PostgreSQL (optional, defaults to SQLite for dev)

### Local Setup
1.  **Clone the repository**:
    ```bash
    git clone <repo-url>
    cd guardrails
    ```

2.  **Create virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
    ```

4.  **Run the server**:
    ```bash
    uvicorn app.main:app --reload
    ```
    Access API at `http://localhost:8000`.

### Docker Setup
1.  **Build and run**:
    ```bash
    docker-compose up --build
    ```
    Access API at `http://localhost:8000`.

## API Documentation

### REST API
- **Swagger UI**: `http://localhost:8000/docs`
- **Analyze Prompt**: `POST /v1/analyze`
- **Health Check**: `GET /v1/health`
- **Tenant Management**: `/v1/tenants`

### GraphQL API
- **Endpoint**: `http://localhost:8000/graphql`
- **Playground**: Open the endpoint in a browser to use GraphiQL.

### Analytics Dashboard
- **URL**: `http://localhost:8000/dashboard`
- **Access**: Requires a valid Tenant API Key.

## Testing
Run the full test suite:
```bash
pytest
```

## Architecture
- **Framework**: FastAPI
- **Database**: SQLAlchemy (SQLite/PostgreSQL)
- **Caching**: Redis
- **GraphQL**: Strawberry
- **Containerization**: Docker & Docker Compose
