# FastAPI Scaffold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a minimal, runnable FastAPI learning scaffold with environment configuration and a tested health endpoint.

**Architecture:** The `fastapi-scaffold` module keeps application construction in `app/main.py`, routes in `app/api`, and typed settings in `app/core`. `main.py` serves as the Uvicorn entry point, while tests exercise the API through FastAPI's `TestClient`.

**Tech Stack:** Python 3.11+, FastAPI, Uvicorn, Pydantic Settings, pytest, HTTPX.

---

### Task 1: Define the health-check contract

**Files:**
- Create: `fastapi-scaffold/tests/test_health.py`

- [ ] **Step 1: Write the failing test**

```python
from fastapi.testclient import TestClient

from app.main import app


def test_health_check_returns_service_status() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "fastapi-scaffold"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_health.py -v`

Expected: FAIL because `app.main` does not exist.

### Task 2: Implement the minimal application

**Files:**
- Create: `fastapi-scaffold/app/__init__.py`
- Create: `fastapi-scaffold/app/api/__init__.py`
- Create: `fastapi-scaffold/app/api/health.py`
- Create: `fastapi-scaffold/app/core/__init__.py`
- Create: `fastapi-scaffold/app/core/config.py`
- Create: `fastapi-scaffold/app/main.py`

- [ ] **Step 1: Create typed configuration and the health router**

```python
class Settings(BaseSettings):
    app_name: str = "fastapi-scaffold"


settings = Settings()


router = APIRouter(tags=["system"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
```

- [ ] **Step 2: Create the FastAPI application and register the router**

```python
app = FastAPI(title=settings.app_name)
app.include_router(router)
```

- [ ] **Step 3: Run the health test to verify it passes**

Run: `python -m pytest tests/test_health.py -v`

Expected: PASS with 1 passed.

### Task 3: Add project tooling and usage guidance

**Files:**
- Create: `fastapi-scaffold/requirements.txt`
- Create: `fastapi-scaffold/.env.example`
- Create: `fastapi-scaffold/README.md`

- [ ] **Step 1: Declare runtime and test dependencies**

```text
fastapi>=0.115,<1.0
uvicorn[standard]>=0.30,<1.0
pydantic-settings>=2.0,<3.0
pytest>=8.0,<9.0
httpx>=0.27,<1.0
```

- [ ] **Step 2: Document local installation, startup, and tests**

```text
python -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
python -m pytest
```

- [ ] **Step 3: Run the complete test suite from the scaffold**

Run: `python -m pytest -v`

Expected: PASS with no failures.
