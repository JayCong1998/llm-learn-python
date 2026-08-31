# FastAPI Vehicle Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend `fastapi-scaffold` with SQLite-backed JWT authentication, RBAC, and brand/model CRUD APIs.

**Architecture:** Keep FastAPI routes thin, put database models and repositories below service functions, and use dependency injection for database sessions and current-user/administrator checks. SQLite schema changes are managed by Alembic and tests use a temporary SQLite database.

**Tech Stack:** FastAPI, SQLAlchemy 2.x, Alembic, Pydantic, PyJWT, pwdlib, pytest.

---

### Task 1: Add database and security foundations

**Files:**
- Create: `fastapi-scaffold/app/core/database.py`, `app/core/security.py`, `app/models/base.py`, `app/models/user.py`, `app/models/brand.py`, `app/models/car_model.py`
- Modify: `fastapi-scaffold/app/core/config.py`, `fastapi-scaffold/requirements.txt`, `.env.example`
- Test: `fastapi-scaffold/tests/test_auth.py`

- [ ] Write tests that register a user and log in to obtain a bearer token; run them and verify import/route failure.
- [ ] Add SQLAlchemy SQLite engine/session, settings, password hashing, JWT encoding/decoding, and `User` model; run tests to green.

### Task 2: Implement authentication and role dependencies

**Files:**
- Create: `fastapi-scaffold/app/schemas/auth.py`, `app/services/auth_service.py`, `app/api/auth.py`, `app/api/dependencies.py`
- Modify: `fastapi-scaffold/app/main.py`
- Test: `fastapi-scaffold/tests/test_auth.py`

- [ ] Write failing tests for duplicate registration (409), wrong password (401), and a normal user rejected from an admin-only endpoint (403).
- [ ] Implement register/login routes and current-user/admin dependencies; run tests to green.

### Task 3: Implement brand CRUD

**Files:**
- Create: `fastapi-scaffold/app/schemas/brand.py`, `app/repositories/brand_repository.py`, `app/services/brand_service.py`, `app/api/brands.py`
- Test: `fastapi-scaffold/tests/test_brands.py`

- [ ] Write failing tests for public list/detail, administrator create/update/delete, normal-user write rejection, duplicate brand conflict, and missing brand 404.
- [ ] Implement brand routes/services/repository with the specified authorization and errors; run tests to green.

### Task 4: Implement car-model CRUD and relationships

**Files:**
- Create: `fastapi-scaffold/app/schemas/car_model.py`, `app/repositories/car_model_repository.py`, `app/services/car_model_service.py`, `app/api/car_models.py`
- Modify: `fastapi-scaffold/app/main.py`, `app/models/brand.py`
- Test: `fastapi-scaffold/tests/test_car_models.py`, `tests/test_brands.py`

- [ ] Write failing tests for public filtered/paginated reads, administrator model CRUD, invalid brand 404, and preventing a brand delete when models exist.
- [ ] Implement the model routes, foreign-key relationship, filtering/pagination, and business errors; run the full suite to green.

### Task 5: Add migrations, administrator initialization, and documentation

**Files:**
- Create: `fastapi-scaffold/alembic.ini`, `fastapi-scaffold/alembic/env.py`, `fastapi-scaffold/alembic/versions/001_initial_schema.py`, `fastapi-scaffold/app/scripts/create_admin.py`
- Modify: `fastapi-scaffold/README.md`
- Test: `fastapi-scaffold/tests/test_health.py`, `tests/test_auth.py`, `tests/test_brands.py`, `tests/test_car_models.py`

- [ ] Add a migration for all three tables and an idempotent environment-configured administrator initializer.
- [ ] Document install, migration, administrator initialization, token use, and test commands; run `python -m pytest -q` from `fastapi-scaffold` and verify all tests pass.
