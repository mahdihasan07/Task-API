# Task Management API

A RESTful API built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy** that lets users register, log in, and manage their personal tasks. Authentication is handled with JWT tokens. Each user can only access their own tasks.

---

## Tech stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Language | Python 3.12.3 |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Auth | JWT (python-jose) + bcrypt |
| Validation | Pydantic v2 |
| Testing | pytest + httpx |
| Runtime | Uvicorn (ASGI) |

---

## Features

- User registration and login with hashed passwords
- JWT-based authentication on all task endpoints
- Full task CRUD: create, list, update, delete
- Each user only sees and manages their own tasks (IDOR-safe)
- Auto-generated interactive API docs at `/docs`
- Database schema versioned with Alembic migrations

---

## Project structure

```
Task-API/
├── app/
│   ├── __init__.py
│   ├── main.py          # App entry point, router registration
│   ├── database.py      # DB engine and session factory
│   ├── models.py        # SQLAlchemy ORM models (DB tables)
│   ├── schemas.py       # Pydantic schemas (API request/response shapes)
│   ├── auth.py          # Password hashing and JWT utilities
│   └── routers/
│       ├── __init__.py
│       ├── auth.py      # /auth/register and /auth/login
│       └── tasks.py     # /tasks CRUD endpoints
├── tests/
│   ├── __init__.py
│   └── test_tasks.py
├── alembic/             # Auto-generated migration files
├── alembic.ini
├── .env                 # Local secrets — never commit this
├── .env.example         # Template for required environment variables
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Python 3.11+
- Docker (for running PostgreSQL locally)

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/mahdihasan07/Task-API.git
cd Task-API
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start PostgreSQL with Docker

```bash
docker run --name pg-taskapi \
  -e POSTGRES_PASSWORD=devpass \
  -e POSTGRES_DB=taskdb \
  -p 5432:5432 -d postgres:16
```

### 5. Configure environment variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql://postgres:devpass@localhost:5432/taskdb
SECRET_KEY=your-random-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> Generate a secure secret key with: `python3 -c "import secrets; print(secrets.token_hex(32))"`

### 6. Run database migrations

```bash
alembic upgrade head
```

### 7. Start the server

```bash
uvicorn app.main:app --reload
```

The API is now running at `http://localhost:8000`.
Interactive docs are available at `http://localhost:8000/docs`.

---

## API reference

### Auth

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/login` | Log in and receive a JWT token | No |

### Tasks

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| POST | `/tasks/` | Create a new task | Yes |
| GET | `/tasks/` | List all your tasks | Yes |
| PUT | `/tasks/{id}` | Update a task | Yes |
| DELETE | `/tasks/{id}` | Delete a task | Yes |

---

## Usage examples

### Register

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "yourpassword"}'
```

Response:

```json
{
  "id": 1,
  "email": "you@example.com",
  "created_at": "2026-07-05T10:00:00Z"
}
```

### Log in

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "yourpassword"}'
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Create a task

```bash
curl -X POST http://localhost:8000/tasks/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Write unit tests", "description": "Cover the auth endpoints"}'
```

Response:

```json
{
  "id": 1,
  "title": "Write unit tests",
  "description": "Cover the auth endpoints",
  "completed": false,
  "created_at": "2026-07-05T10:05:00Z"
}
```

### List tasks

```bash
curl http://localhost:8000/tasks/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Update a task

```bash
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Write unit tests", "description": "Done!", "completed": true}'
```

### Delete a task

```bash
curl -X DELETE http://localhost:8000/tasks/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Running tests

```bash
pytest tests/ -v
```

---

## Environment variables

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/taskdb` |
| `SECRET_KEY` | Secret used to sign JWT tokens — keep this private | `a3f8...` (32+ random hex chars) |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | How long tokens stay valid | `30` |

---

## Security notes

- Passwords are hashed with bcrypt before storage — plain-text passwords are never saved
- JWT tokens expire after the configured duration
- Every task endpoint filters by the authenticated user's ID, preventing one user from accessing another user's data
- The `.env` file is gitignored — never commit real credentials

---

## Database schema

```
users
  id            SERIAL PRIMARY KEY
  email         VARCHAR UNIQUE NOT NULL
  hashed_password VARCHAR NOT NULL
  created_at    TIMESTAMPTZ DEFAULT now()

tasks
  id            SERIAL PRIMARY KEY
  title         VARCHAR NOT NULL
  description   VARCHAR
  completed     BOOLEAN DEFAULT false
  owner_id      INTEGER REFERENCES users(id)
  created_at    TIMESTAMPTZ DEFAULT now()
```

