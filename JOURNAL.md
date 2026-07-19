## Week 7 — Issue selection

**Issue link:** https://github.com/ascherj/pathreview/issues/159

**Issue title:** structlog output is not captured by pytest caplog — log assertions fail suite-wide

**Tier:** [x] Tier 1  [ ] Tier 2  [ ] Tier 3

**Problem summary:**
The application logs through structlog, but structlog isn't configured to propagate its output into Python's standard logging system during tests. As a result, any test that asserts against `caplog` (like `test_empty_chunks_list_returns_empty` in `tests/unit/test_batch_processor.py`) fails, even though the code correctly emits the expected log event — it's just not being captured. The fix involves configuring structlog in `tests/conftest.py` (likely using `structlog.stdlib` processors or `capture_logs`) so that `caplog`-based assertions can actually see the log events.

**Is this right for me? — checklist reasoning:**
I can explain this issue without re-reading it: structlog isn't wired into stdlib logging during tests, so `caplog` assertions fail even when the correct log event is emitted. This is a Tier 1 issue and matches my experience level as a first-time contributor — the fix is scoped to a single file (`tests/conftest.py`) and doesn't require understanding the full application. I reproduced the issue locally by running the exact pytest command from the issue description and confirmed the test fails with an empty `caplog.text`, while the log line is visibly emitted to stdout. Multiple people have commented interest, but no PRs exist yet, so it's still open to attempt. The estimated scope (config-level fix in one file) fits comfortably within the Week 8-9 timeline.

**Branch name:** fix/159-structlog-caplog-config

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger