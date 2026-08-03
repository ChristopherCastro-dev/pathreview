## Solution plan

**Issue:** #159 — structlog output is not captured by pytest caplog

### Understand
`core/logging.py` defines `configure_logging()`, which sets up `structlog.configure()` with `logger_factory=structlog.stdlib.LoggerFactory()` — meaning structlog is designed to route through Python's standard `logging` module when this function runs. However, `configure_logging()` is currently only called in one place in the whole codebase: `scripts/seed_db.py`. It is never called during the pytest test run (confirmed via `grep -rn "configure_logging()" .` — no references in `api/main.py`, `tests/conftest.py`, or anywhere else).

Without that call, structlog falls back to its own default configuration, which renders and prints directly to stdout rather than routing through stdlib `logging`. That's why the warning message appears visibly in the terminal (structlog prints it directly) but pytest's `caplog` — which attaches a handler to the standard `logging` module — never sees it, since the message never passes through `logging` at all.

**Root cause:** `configure_logging()` (in `core/logging.py`) is never invoked in the test environment, so structlog isn't wired into stdlib `logging`, and `caplog` has nothing to capture.

### Map
Files I expect to touch:
- `core/logging.py` — `configure_logging()` (lines 8-43): reuse this function rather than duplicating its processor list, since it already defines the correct `logger_factory=structlog.stdlib.LoggerFactory()` setup.
- `tests/conftest.py` — currently has no structlog setup at all (confirmed — only `sample_resume_text` and `sample_readme_text` fixtures exist). I'll add an autouse fixture here that calls `configure_logging()` before each test/session runs.
- I will not touch `api/main.py`, since `configure_logging()` isn't called there either — that looks like a separate, pre-existing gap outside the scope of this issue. I'll note this as an observation but won't fix it here to avoid scope creep.

### Plan
1. Confirm where `configure_logging()` is called in the app (checked — only `scripts/seed_db.py`, not `api/main.py`) to understand there's no existing startup call pattern to follow for tests.
2. In `tests/conftest.py`, add an autouse pytest fixture (session or function scope) that calls `configure_logging()` (or a stripped-down structlog config ending in `structlog.stdlib.ProcessorFormatter.wrap_for_formatter`), so structlog output is routed through stdlib `logging` and becomes visible to `caplog`.
3. Confirm `logger_factory=structlog.stdlib.LoggerFactory()` and `cache_logger_on_first_use=False` are set for tests (caching could cause stale config between test runs).
4. Run the previously-failing test to confirm it now passes: `pytest tests/unit/test_batch_processor.py::TestBatchEmbeddingProcessor::test_empty_chunks_list_returns_empty -s`
5. Run the full test suite (`make test-unit` or equivalent) to confirm no other tests that rely on structlog/caplog break or regress.
6. Run lint/type checks (`make check` or equivalent) to confirm formatting and typing are clean.

### Inputs & outputs
**Function I'm changing/adding:** a new fixture in `tests/conftest.py`, tentatively `configure_test_logging()` or similar, marked `@pytest.fixture(autouse=True)`.

**Existing (broken) behavior:**
- Input: `processor.process([])` triggers `logger.warning("Empty chunks list...")`
- Output: message printed to stdout via structlog's default renderer; `caplog.text` stays empty

**Expected (fixed) behavior:**
- Input: same call
- Output: message routed through stdlib `logging`, so `caplog.text` contains "Empty chunks list" and the existing assertion in `test_empty_chunks_list_returns_empty` passes without modification

**Test I'll verify (already exists, no new test needed for this fix):**
`tests/unit/test_batch_processor.py::TestBatchEmbeddingProcessor::test_empty_chunks_list_returns_empty`

This test itself doesn't need rewriting — the fix should make the existing assertion pass, since the issue is a config gap, not a broken test.

### Risks & unknowns
1. **Global vs. per-test config.** If `configure_logging()` uses `cache_logger_on_first_use=True`, calling it fresh per-test might not fully reset structlog's cached loggers between tests. I'll check whether test config needs `cache_logger_on_first_use=False`.
2. **Might affect other tests silently.** Since many modules (`batch_processor.py`, `pipeline.py`, `review_service.py`, etc.) all use `structlog.get_logger()`, wiring structlog into stdlib logging for tests could surface `caplog` output in other tests that weren't expecting it. I'll run the full suite, not just the one failing test, to check for this.
3. **Duplicate logging setup between app and test config.** I want to avoid the test fixture and `configure_logging()` drifting out of sync over time. I may consider having the test fixture call `configure_logging()` directly rather than duplicating the processor list, but need to confirm it doesn't depend on `settings.app_env` in a way that breaks in test context.
4. **`configure_logging()` isn't called anywhere except `scripts/seed_db.py`.** This suggests the actual running API may also not have structured logging configured properly at startup, which is arguably a separate, more significant bug — but it's out of scope for issue #159. I'll mention this as an observation in my PR description but won't fix it, to keep this change scoped.

### Edge cases
- A test that never triggers a log call: should be unaffected (no caplog assertions, no output either way).
- A test that intentionally checks absence of a log: should still work, since caplog just starts empty.
- Tests running in parallel (if pytest-xdist or similar is used): structlog config being global/session-scoped could interact oddly across workers — I'll check if the test suite runs in parallel and confirm this isn't an issue.