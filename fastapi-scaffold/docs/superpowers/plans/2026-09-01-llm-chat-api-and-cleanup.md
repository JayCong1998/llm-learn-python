# LLM Chat API and Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver authenticated synchronous LLM chat APIs using an OpenAI-compatible endpoint and remove the obsolete brand and car-model feature.

**Architecture:** API routes delegate to a chat service, which owns authorization, persistence transaction boundaries, prompt construction, and one synchronous OpenAI-compatible HTTP request. Conversation, message, and call-log repositories isolate SQLAlchemy operations; tool calls remain request-memory-only and are not persisted.

**Tech Stack:** FastAPI, Pydantic, SQLAlchemy 2, httpx, Alembic, pytest.

---

### Task 1: Add failing chat API tests

**Files:**
- Create: `fastapi-scaffold/tests/test_chat.py`
- Modify: `fastapi-scaffold/tests/test_foundation.py`

- [ ] Write tests for authenticated conversation creation, message submission producing a saved assistant reply and `llm_call_log`, history retrieval, logical deletion, and a mocked OpenAI-compatible HTTP response.
- [ ] Run `python -m pytest tests/test_chat.py -q` and confirm the tests fail because `/chat/conversations` is absent.
- [ ] Implement schemas, repositories, client, service, and API routes with Chinese comments before each changed Python statement.
- [ ] Re-run `python -m pytest tests/test_chat.py -q` and confirm it passes.

### Task 2: Remove vehicle management

**Files:**
- Delete: `app/api/brands.py`, `app/api/car_models.py`, `app/models/brand.py`, `app/models/car_model.py`, `app/repositories/brand_repository.py`, `app/repositories/car_model_repository.py`, `app/schemas/brand.py`, `app/schemas/car_model.py`, `app/services/brand_service.py`, `app/services/car_model_service.py`, `tests/test_brands.py`, `tests/test_car_models.py`
- Modify: `app/main.py`, `alembic/env.py`, `alembic/versions/20260901_0003_remove_vehicle_tables.py`, `README.md`, and remaining tests.

- [ ] Write a failing migration-content test requiring the two vehicle tables to be dropped.
- [ ] Run the focused test and confirm the migration is absent.
- [ ] Remove routes and imports, add a migration that drops `car_models` before `brands`, and remove vehicle assertions.
- [ ] Run the complete suite and migrate a temporary SQLite database through `head`.
