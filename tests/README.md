# Tests

Run all Python tests from the project root:

```powershell
.venv\Scripts\python.exe -m pytest
```

`pytest.ini` puts `backend/` and the project root on the import path, so tests can `import app` and (later) `import ml`.

| Folder | Contents |
|---|---|
| `integration/` | API tests using FastAPI's `TestClient` (no server needed) |
| `unit/` | Pure-function tests: recoding, BMI, interpretation, suggestion rules (from Task 3) |
| `data/` | Checks on processed datasets (from Task 2–3; skipped if data is not downloaded) |

Frontend tests (Vitest) live in `frontend/` and arrive in Task 8.
