<div align="center">

<h1>Averisq</h1>

<p><strong>API Reliability &amp; Observability Platform</strong></p>

<p>A secure foundation for API reliability and observability.</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white" alt="Python 3.13" />
  <img src="https://img.shields.io/badge/FastAPI-0.162.0-009688?logo=fastapi&logoColor=white" alt="FastAPI 0.162.0" />
  <img src="https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/SQLAlchemy-2.1.6-D71F00?logo=sqlalchemy&logoColor=white" alt="SQLAlchemy 2.1.6" />
  <img src="https://img.shields.io/badge/Pydantic-2.14.2-E92063?logo=pydantic&logoColor=white" alt="Pydantic 2.14.2" />
  <img src="https://img.shields.io/badge/Auth-JWT-000000?logo=jsonwebtokens&logoColor=white" alt="JWT authentication" />
  <img src="https://img.shields.io/badge/Tests-23%20passing-0A9EDC?logo=pytest&logoColor=white" alt="23 tests passing" />
</p>

<p><a href="https://github.com/Rohit-Ahire-22/averisq">github.com/Rohit-Ahire-22/averisq</a></p>

</div>

---

## Overview

Averisq is a backend platform for managing API monitors and, over time, observing the reliability of the APIs they track. The current version implements the authenticated control plane: users can register, log in, and manage only their own monitors.

The project is a foundation for API reliability and observability. Instead of spreading health checks across ad-hoc scripts and dashboards, Averisq is designed to become a single place to define which APIs matter, run checks against them, retain execution history, and surface failures. This repository currently delivers the secure monitor registry and user-isolation layer. Execution, scheduling, alerting, and dashboards are planned.

**Why this matters:** APIs fail in ways that are easy to miss, including slow responses, intermittent 5xx errors, expired certificates, and silent downtime. Reliable systems need consistent checks, retained evidence, and clear ownership of what is being monitored.

### At a glance

| Area | Current status |
|---|---|
| User registration and login | Implemented |
| Argon2id password hashing | Implemented |
| JWT access tokens | Implemented |
| Protected monitor CRUD | Implemented |
| Per-user ownership isolation | Implemented |
| Pagination | Implemented |
| PostgreSQL persistence | Implemented |
| Automated test suite | Implemented |
| Monitoring execution engine | Planned |
| Alerting and dashboards | Planned |

### Current capabilities

- **Authentication** — registration and login with email and password.
- **Password security** — Argon2id hashing through `pwdlib`; passwords are never stored or returned in plaintext.
- **JWT authorization** — signed access tokens with `sub`, `iat`, and `exp` claims.
- **Protected API endpoints** — monitor routes require a valid Bearer token.
- **Monitor CRUD** — create, list, retrieve, update, and delete monitors.
- **User ownership isolation** — every monitor query is scoped to the authenticated user; cross-user access returns `404`.
- **Pagination** — owner-scoped listing with `limit` and `offset`.
- **PostgreSQL integration** — SQLAlchemy 2.x models with UUID keys and cascading foreign keys.
- **Automated testing** — 23 tests covering authentication, security, monitor lifecycle, and database isolation.

### Planned capabilities

- Monitoring execution engine and background scheduling
- HTTP health checks and response-time measurement
- Persistent and queryable monitor execution history
- Alerting and an observability dashboard
- Docker, CI/CD, and cloud deployment
- Fresh-database Alembic migrations

> `MonitorResult` is currently a database model only. No execution engine, result-collection job, or result API exists yet.

---

## Architecture

```mermaid
flowchart TB
    Client["Client<br/>Swagger UI / HTTP"]

    subgraph API["FastAPI Application"]
        AuthRouter["Auth Router<br/>/api/v1/auth"]
        MonitorRouter["Monitor Router<br/>/api/v1/monitors"]
        AuthDeps["get_current_user<br/>HTTPBearer + JWT validation"]
    end

    subgraph Core["Core"]
        Security["Security Module<br/>Argon2id + PyJWT"]
        Config["Settings<br/>Pydantic Settings"]
    end

    subgraph Services["Service Layer"]
        AuthService["Auth Service"]
        MonitorService["Monitor Service"]
    end

    subgraph Persistence["Persistence"]
        ORM["SQLAlchemy ORM"]
        UserModel["User"]
        MonitorModel["Monitor"]
        ResultModel["MonitorResult"]
    end

    DB[("PostgreSQL")]

    Client -->|"register / login"| AuthRouter
    Client -->|"Bearer JWT"| MonitorRouter
    AuthRouter --> AuthService
    AuthRouter --> Security
    MonitorRouter --> AuthDeps
    MonitorRouter --> MonitorService
    AuthDeps --> Security
    AuthDeps --> ORM
    AuthService --> Security
    AuthService --> ORM
    MonitorService --> ORM
    ORM --> UserModel
    ORM --> MonitorModel
    ORM --> ResultModel
    ORM --> DB
    Config -.-> Security
    Config -.-> ORM
```

The application is split into HTTP routes, a service layer, and a persistence layer. Routes handle request validation and HTTP status codes; services contain database operations; SQLAlchemy maps the `User`, `Monitor`, and `MonitorResult` models to PostgreSQL.

---

## Authentication Flow

### Registration

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant R as Auth Router
    participant P as Pydantic
    participant S as Auth Service
    participant H as Security
    participant DB as PostgreSQL

    C->>R: POST /api/v1/auth/register
    R->>P: Validate UserCreate
    alt Invalid payload
        P-->>C: 422 Validation Error
    else Valid payload
        P-->>R: Validated data
        R->>S: register_user(db, data)
        S->>S: Normalize email
        S->>DB: SELECT user by email
        alt Email already registered
            DB-->>S: Existing user
            S-->>R: ValueError: Email already registered
            R-->>C: 409 Conflict
        else New email
            DB-->>S: No user
            S->>H: hash_password(password)
            H-->>S: Argon2id hash
            S->>DB: INSERT user and COMMIT
            DB-->>S: User
            S-->>R: User
            R-->>C: 201 UserRead
        end
    end
    Note over S,DB: Concurrent duplicate inserts are rolled back and mapped to 409.
```

### Login

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant R as Auth Router
    participant P as Pydantic
    participant S as Auth Service
    participant H as Security
    participant DB as PostgreSQL

    C->>R: POST /api/v1/auth/login
    R->>P: Validate UserLogin
    alt Invalid payload
        P-->>C: 422 Validation Error
    else Valid payload
        P-->>R: Validated data
        R->>S: authenticate_user(db, data)
        S->>DB: SELECT user by email
        alt User not found
            DB-->>S: No user
            S-->>R: ValueError: Invalid email or password
            R-->>C: 401 Unauthorized
        else User found
            DB-->>S: User
            S->>H: verify_password(password, password_hash)
            alt Password mismatch
                H-->>S: False
                S-->>R: ValueError: Invalid email or password
                R-->>C: 401 Unauthorized
            else Password valid
                H-->>S: True
                S-->>R: User
                R->>H: create_access_token(user.id)
                H-->>R: JWT with sub, iat, exp
                R-->>C: 200 TokenResponse
            end
        end
    end
```

Both failure paths return the same generic message, `Invalid email or password`, with a `WWW-Authenticate: Bearer` header.

---

## Protected Monitor Flow

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant R as Monitor Router
    participant B as HTTPBearer
    participant D as get_current_user
    participant H as Security
    participant S as Monitor Service
    participant DB as PostgreSQL

    C->>R: GET /api/v1/monitors/{id} with Bearer token
    R->>B: Extract Authorization credentials
    B-->>D: HTTPAuthorizationCredentials
    D->>H: decode_access_token(token)
    H->>H: Verify signature and expiration
    alt Invalid or expired token
        H-->>D: ValueError
        D-->>C: 401 Unauthorized
    else Valid token
        H-->>D: user_id (UUID)
        D->>DB: SELECT user WHERE id = user_id
        alt User missing
            DB-->>D: None
            D-->>C: 401 Unauthorized
        else User found
            DB-->>D: User
            D-->>R: current_user
            R->>S: get_monitor_by_id(db, monitor_id, user_id)
            S->>DB: SELECT monitor WHERE id = ? AND user_id = ?
            alt Monitor missing or owned by another user
                DB-->>S: None
                S-->>R: None
                R-->>C: 404 Monitor not found
            else Monitor owned by current user
                DB-->>S: Monitor
                S-->>R: Monitor
                R-->>C: 200 MonitorResponse
            end
        end
    end
```

The same ownership filter applies to list, update, and delete operations. A monitor belonging to another user is treated as not found.

---

## Database Schema

```mermaid
erDiagram
    USER ||--o{ MONITOR : owns
    MONITOR ||--o{ MONITOR_RESULT : produces

    USER {
        uuid id PK
        string email UK
        text password_hash
        timestamptz created_at
    }

    MONITOR {
        uuid id PK
        uuid user_id FK
        string name
        text url
        int interval_seconds
        string status
        timestamptz created_at
    }

    MONITOR_RESULT {
        uuid id PK
        uuid monitor_id FK
        int status_code
        int response_time_ms
        boolean is_success
        text error_message
        timestamptz checked_at
    }
```

- `users.id`, `monitors.id`, and `monitor_results.id` are UUID primary keys.
- `monitors.user_id` references `users.id` with `ON DELETE CASCADE`.
- `monitor_results.monitor_id` references `monitors.id` with `ON DELETE CASCADE`.
- The Python attribute `Monitor.interval` maps to the database column `interval_seconds`.
- `MonitorResult` exists in the schema but is not yet populated by an execution engine.

---

## Technology Stack

| Technology | Version | Role |
|---|---|---|
| Python | 3.13 | Runtime |
| FastAPI | 0.162.0 | HTTP API framework and dependency injection |
| PostgreSQL | — | Relational database |
| SQLAlchemy | 2.1.6 | ORM and typed model definitions |
| Alembic | 1.20.1 | Database schema version tracking |
| Pydantic | 2.14.2 | Request and response validation |
| Pydantic Settings | 2.16.2 | Environment-based configuration |
| PyJWT | 2.15.1 | JWT creation and validation |
| pwdlib + Argon2 | 0.3.1 | Password hashing and verification |
| Psycopg | 3.3.7 | PostgreSQL driver |
| pytest | 9.2.0 | Test runner |
| HTTPX | 0.28.1 | HTTP client used by the test suite |

Versions match `backend/requirements.txt`. PostgreSQL has no pinned server version in the repository.

---

## Project Structure

```text
averisq/
├── .gitignore
├── README.md
└── backend/
    ├── .env.example
    ├── .gitignore
    ├── alembic.ini
    ├── requirements.txt
    ├── app/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── api/
    │   │   ├── __init__.py
    │   │   ├── auth.py
    │   │   ├── deps.py
    │   │   └── monitors.py
    │   ├── core/
    │   │   ├── config.py
    │   │   └── security.py
    │   ├── db/
    │   │   ├── __init__.py
    │   │   ├── base.py
    │   │   └── database.py
    │   ├── models/
    │   │   ├── __init__.py
    │   │   ├── monitor.py
    │   │   ├── monitor_result.py
    │   │   └── user.py
    │   ├── schemas/
    │   │   ├── __init__.py
    │   │   ├── monitor.py
    │   │   └── user.py
    │   └── services/
    │       ├── __init__.py
    │       ├── auth.py
    │       └── monitor_service.py
    ├── migrations/
    │   ├── README
    │   ├── env.py
    │   ├── script.py.mako
    │   └── versions/
    │       └── b6362a0c6d9f_baseline_existing_schema.py
    └── tests/
        ├── __init__.py
        ├── conftest.py
        ├── test_auth.py
        ├── test_database.py
        ├── test_monitors.py
        └── test_security.py
```

---

## Getting Started

### Prerequisites

- Python 3.13
- PostgreSQL running locally or reachable over the network
- Git

### 1. Clone the repository

```powershell
git clone https://github.com/Rohit-Ahire-22/averisq.git
Set-Location averisq
Set-Location backend
```

Linux/macOS:

```bash
git clone https://github.com/Rohit-Ahire-22/averisq.git
cd averisq/backend
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

Edit `.env` and replace the placeholders for `DATABASE_URL`, `TEST_DATABASE_URL`, and `JWT_SECRET_KEY`.

Generate a strong JWT secret with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Never commit `.env`. It is already excluded by the repository's `.gitignore` files.

### 5. Set up PostgreSQL

Create the application and test databases:

```powershell
psql -U postgres -c "CREATE DATABASE averisq;"
psql -U postgres -c "CREATE DATABASE averisq_test_db;"
```

Update `DATABASE_URL` and `TEST_DATABASE_URL` in `.env` with your PostgreSQL username, password, host, port, and database names.

### 6. Prepare the schema

The repository's Alembic baseline (`b6362a0c6d9f`) is intentionally empty. It records an existing schema but does not create application tables on a fresh database. `alembic upgrade head` therefore does not provision the `users`, `monitors`, or `monitor_results` tables.

For a fresh development database, bootstrap the tables from the SQLAlchemy metadata. This mirrors the approach used by the test suite:

```powershell
python -c "from app.db.base import Base; import app.models; from app.db.database import engine; Base.metadata.create_all(bind=engine)"
```

The automated tests create and drop their own tables in the test database, so no manual schema setup is required for `pytest` beyond creating the database and setting `TEST_DATABASE_URL`.

To inspect the current Alembic revision:

```powershell
alembic current
```

### 7. Start the development server

Run from the `backend` directory:

```powershell
python -m uvicorn app.main:app --reload
```

The API is available at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

---

## Environment Variables

`backend/.env.example` is the source of truth for local configuration.

| Variable | Purpose | Required | Safe placeholder |
|---|---|---|---|
| `DATABASE_URL` | Application PostgreSQL connection | Yes | `postgresql+psycopg://USERNAME:PASSWORD@localhost:5432/DATABASE_NAME` |
| `TEST_DATABASE_URL` | PostgreSQL connection used by the test suite | Yes for tests | `postgresql+psycopg://postgres:password@localhost:5432/averisq_test_db` |
| `JWT_SECRET_KEY` | Secret used to sign and verify JWTs | Yes | `replace-with-a-long-random-secret` |
| `JWT_ALGORITHM` | JWT signing algorithm | No, defaults to `HS256` | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime in minutes | No, defaults to `30` | `30` |

Replace every placeholder with a real value for your environment. Keep `JWT_SECRET_KEY` private and use a different secret for each deployment.

---

## API Reference

Base URL: `http://127.0.0.1:8000`

### Authentication

| Method | Path | Authentication | Success | Description |
|---|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Public | `201` | Register a user and return `id`, `email`, and `created_at` |
| `POST` | `/api/v1/auth/login` | Public | `200` | Verify credentials and return an access token |

### Monitors

All monitor endpoints require `Authorization: Bearer <token>`.

| Method | Path | Authentication | Success | Description |
|---|---|---|---|---|
| `POST` | `/api/v1/monitors/` | Bearer JWT | `201` | Create a monitor owned by the current user |
| `GET` | `/api/v1/monitors/` | Bearer JWT | `200` | List the current user's monitors with pagination |
| `GET` | `/api/v1/monitors/{monitor_id}` | Bearer JWT | `200` | Retrieve one of the current user's monitors |
| `PATCH` | `/api/v1/monitors/{monitor_id}` | Bearer JWT | `200` | Update one of the current user's monitors |
| `DELETE` | `/api/v1/monitors/{monitor_id}` | Bearer JWT | `204` | Delete one of the current user's monitors |

Pagination parameters for `GET /api/v1/monitors/`:

| Parameter | Default | Constraints |
|---|---|---|
| `limit` | `10` | `1` to `100` |
| `offset` | `0` | `0` or greater |

### Service

| Method | Path | Authentication | Success | Description |
|---|---|---|---|---|
| `GET` | `/` | Public | `200` | Welcome message |

### Common responses

| Status | Meaning |
|---|---|
| `401` | Missing, invalid, expired, or unauthenticated user token |
| `404` | Monitor not found or not owned by the current user |
| `409` | Email already registered, or a monitor constraint conflict |
| `422` | Request validation failed |

### Authenticating in Swagger UI

1. Open `http://127.0.0.1:8000/docs`.
2. Call `POST /api/v1/auth/login` with a registered email and password.
3. Copy the `access_token` from the response.
4. Click **Authorize** and paste the token into the HTTPBearer field. Swagger UI adds the `Bearer` prefix.
5. Call any `/api/v1/monitors` endpoint.

---

## Authentication and Security

### Implemented

- **Argon2id password hashing** through `pwdlib`'s recommended password hasher.
- **Password verification** during login; plaintext passwords are never stored or returned.
- **Password length validation** of 8 to 128 characters.
- **JWT access tokens** signed with `JWT_SECRET_KEY` and `JWT_ALGORITHM` (default `HS256`).
- **JWT claims** include `sub` (user UUID), `iat`, and `exp`; all three are required during validation.
- **Signature and expiration validation** via PyJWT. Invalid, malformed, and expired tokens return `401`.
- **HTTP Bearer extraction** using `HTTPBearer(auto_error=False)`.
- **FastAPI dependency injection** through `get_current_user`.
- **Current-user database lookup** on every protected request; a missing user returns `401`.
- **Monitor ownership enforcement** by filtering every query on the authenticated user's ID.
- **Consistent unauthorized responses** with `WWW-Authenticate: Bearer`.
- **Generic invalid-credential messages** during login to avoid revealing whether an email exists.

### Not implemented

The current version does not include refresh tokens, OAuth2 authorization code flow, role-based access control, rate limiting, email verification, password reset, or token revocation. Do not assume these protections are present.

---

## Testing

Run the suite from the `backend` directory:

```powershell
python -m pytest -v
```

**Current verified result: 23 tests passing.**

| Test area | Coverage |
|---|---|
| Authentication API | Registration, duplicate email, login, wrong password, nonexistent email, token-protected access |
| Security | Password hashing and salting, verification, token creation and decoding, invalid signature, expiration, missing `exp`, invalid UUID subject |
| Monitors | Creation, invalid interval, listing, cross-user isolation, unauthenticated access |
| Database | Transaction rollback, non-persistence across tests, monitor lifecycle, not-found behavior |

The test suite requires a reachable PostgreSQL database configured through `TEST_DATABASE_URL`. Test fixtures create the schema, run each test inside a transaction, and roll back afterwards.

---

## Engineering Highlights

- **Route/service separation** — HTTP concerns live in routers; database operations live in services.
- **Dependency injection** — database sessions and the authenticated user are injected through FastAPI dependencies.
- **Typed SQLAlchemy models** — SQLAlchemy 2.x `Mapped` and `mapped_column` declarations.
- **Pydantic validation** — request and response schemas validate input and shape output.
- **Explicit transaction handling** — services commit explicitly, roll back on `IntegrityError`, and rely on `get_db` for rollback and cleanup.
- **Consistent HTTP semantics** — `201` for creation, `204` for deletion, `401` for authentication failures, `404` for missing or non-owned resources, `409` for conflicts, and `422` for validation errors.
- **User data isolation** — every monitor query is scoped to the authenticated user.
- **Automated testing** — authentication, security, monitor behavior, and database isolation are covered by the test suite.

---

## Roadmap

### Completed

- [x] User registration and login
- [x] Argon2id password hashing
- [x] JWT access token creation and validation
- [x] HTTP Bearer authentication dependency
- [x] Protected monitor CRUD
- [x] Per-user monitor ownership isolation
- [x] Owner-scoped pagination
- [x] PostgreSQL persistence with SQLAlchemy
- [x] Automated authentication, security, monitor, and database tests
- [x] `MonitorResult` model scaffolded

### Planned

- [ ] Monitoring execution engine
- [ ] Background scheduling
- [ ] HTTP health checks
- [ ] Response-time measurement
- [ ] Persist and expose monitor execution history
- [ ] Alerting
- [ ] Observability dashboard
- [ ] Alembic migrations that provision a fresh database
- [ ] Docker
- [ ] CI/CD
- [ ] Cloud deployment
- [ ] Optional hardening: rate limiting, refresh tokens, and token revocation

---

## Contributing

1. Fork the repository and create a focused feature branch.
2. Set up the backend using the instructions above.
3. Add or update tests for behavior you change.
4. Run `python -m pytest -v` from `backend/`.
5. Keep `.env`, credentials, and generated files out of commits.
6. Open a pull request with a clear description of the change and the tests you ran.

For small fixes, a concise pull request is welcome. For larger changes, open an issue first so the approach can be discussed.

---

## License

This repository does not currently include a license file. Add a license before distributing or reusing the code.

---

## Author

Maintained by [Rohit-Ahire-22](https://github.com/Rohit-Ahire-22).

Repository: [github.com/Rohit-Ahire-22/averisq](https://github.com/Rohit-Ahire-22/averisq)
