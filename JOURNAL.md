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

## Week 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/ChristopherCastro-dev/pathreview/commit/2f92a1d

**Reproduction summary:**
Ran the failing test directly and confirmed `caplog.text` stays empty even though structlog visibly prints the expected warning to stdout. Root cause: `configure_logging()` in `core/logging.py` is never called during tests, so structlog isn't wired into stdlib `logging`, which is what `caplog` hooks into.

**PLAN.md link:** https://github.com/ChristopherCastro-dev/pathreview/blob/fix/159-structlog-caplog-config/PLAN.md

**Walkthrough video (recommended):** Not recorded this week.

**Blockers or open questions:**
None currently — root cause is confirmed and the fix approach (adding an autouse fixture in `tests/conftest.py` that calls `configure_logging()`) is scoped. Will confirm during implementation whether `cache_logger_on_first_use` needs to be `False` for tests.

---

**Detailed reproduction (issue #159):**

**Reproduction steps:**
1. Ran the failing test directly:
```
pytest tests/unit/test_batch_processor.py::TestBatchEmbeddingProcessor::test_empty_chunks_list_returns_empty -s
```
2. Confirmed the test fails: `caplog.text` is empty even though structlog visibly
   printed the expected warning to stdout during the test run.

**Observed output:**
```
tests/unit/test_batch_processor.py 2026-07-19 19:52:12 [warning  ] Empty chunks list provided to BatchEmbeddingProcessor
F
=================================== FAILURES ====================================
_______ TestBatchEmbeddingProcessor.test_empty_chunks_list_returns_empty ________

    def test_empty_chunks_list_returns_empty(self, processor, caplog):
        """Test that empty chunks list logs warning and returns empty list."""
        result = processor.process([])

        assert result == []
        # Should log a warning
>       assert "Empty chunks list" in caplog.text or any(
            "empty" in record.message.lower() for record in caplog.records
        )
E       AssertionError: assert ('Empty chunks list' in '' or False)
E        +  where '' = <_pytest.logging.LogCaptureFixture object at 0x1052ef4d0>.text
E        +  and   False = any(<generator object ...>)

tests/unit/test_batch_processor.py:42: AssertionError
FAILED tests/unit/test_batch_processor.py::TestBatchEmbeddingProcessor::test_empty_chunks_list_returns_empty - AssertionError: assert ('Empty chunks list' in '' or False)
1 failed in 0.39s
```

**Root cause:**
`structlog` emits the warning ("Empty chunks list provided to BatchEmbeddingProcessor")
and it clearly prints to stdout. But it's not routed through Python's standard `logging`
module, which is what pytest's `caplog` fixture hooks into. As a result, `caplog.text`
and `caplog.records` both stay empty even though the log event genuinely fired. The fix
needs to configure structlog (likely in `tests/conftest.py`) to route through stdlib
`logging`, e.g. via `structlog.stdlib.LoggerFactory` and a `ProcessorFormatter`.

**Status:** Reproduced locally with real output. Root cause confirmed. Proceeding to PLAN.md.