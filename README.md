\# Averisq



\*\*API Reliability \& Observability Platform\*\*



Averisq is a backend platform being built to help developers manage API monitors and, as the platform evolves, observe API reliability and understand failures.



\## Current Features



\- Create API monitors.

\- Retrieve all monitors.

\- Retrieve an individual monitor.

\- Update monitor configuration.

\- Delete monitors.

\- PostgreSQL persistence using SQLAlchemy.

\- Database schema version tracking using Alembic.

\- Request and response validation using Pydantic.



\## Technology Stack



\- \*\*Language:\*\* Python 3.13

\- \*\*API Framework:\*\* FastAPI

\- \*\*Database:\*\* PostgreSQL

\- \*\*ORM:\*\* SQLAlchemy

\- \*\*Migrations:\*\* Alembic

\- \*\*Validation:\*\* Pydantic

\- \*\*Database Driver:\*\* Psycopg



\## Project Structure



```text

averisq/

├── .gitignore

├── README.md

└── backend/

&#x20;   ├── .env.example

&#x20;   ├── .gitignore

&#x20;   ├── requirements.txt

&#x20;   ├── alembic.ini

&#x20;   ├── app/

&#x20;   │   ├── api/

&#x20;   │   │   └── monitors.py

&#x20;   │   ├── db/

&#x20;   │   │   ├── base.py

&#x20;   │   │   └── database.py

&#x20;   │   ├── models/

&#x20;   │   ├── schemas/

&#x20;   │   ├── services/

&#x20;   │   └── main.py

&#x20;   └── migrations/

&#x20;       └── versions/

```



\## API Endpoints



Base path: `/api/v1/monitors`



| Method | Endpoint | Description |

|---|---|---|

| POST | `/` | Create a monitor |

| GET | `/` | Retrieve all monitors |

| GET | `/{monitor\_id}` | Retrieve a monitor |

| PATCH | `/{monitor\_id}` | Update a monitor |

| DELETE | `/{monitor\_id}` | Delete a monitor |



Interactive API documentation is available at `/docs` when the development server is running.



\## Local Setup



\### 1. Clone the repository



```bash

git clone <repository-url>

cd averisq/backend

```



\### 2. Create a virtual environment



```bash

python -m venv venv

```



Activate it on Windows PowerShell:



```powershell

.\\venv\\Scripts\\Activate.ps1

```



\### 3. Install dependencies



```bash

python -m pip install -r requirements.txt

```



\### 4. Configure environment variables



Create your local environment file from the example:



```powershell

Copy-Item .env.example .env

```



Update `DATABASE\_URL` inside `.env` with your PostgreSQL connection details.



\### 5. Database setup



Ensure PostgreSQL is running and the database schema has been provisioned.



The current Alembic baseline represents an existing database schema and is empty. It does not independently create all application tables on a fresh database.



Check the current migration revision:



```bash

alembic current

```



\### 6. Start the development server



Run from the `backend` directory:



```bash

python -m fastapi dev app/main.py

```



API documentation:



```text

http://127.0.0.1:8000/docs

```



\## Development Notes



\- Monitor routes currently use a temporary development user ID.

\- Authentication and user-specific identity management are not implemented yet.

\- Scheduled API checks and monitoring-result collection are planned.

\- Future development will introduce authentication, monitoring execution, analytics and observability capabilities.



\## Project Status



\*\*Under active development.\*\*



Averisq is being developed incrementally with an emphasis on backend engineering fundamentals, maintainable architecture, database design and production-oriented practices.
