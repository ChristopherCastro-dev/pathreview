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

## Week 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
Implemented the fix from PLAN.md: added an autouse pytest fixture (`configure_test_logging`) in `tests/conftest.py` that calls `configure_logging()` before each test, so structlog routes through stdlib `logging` and becomes visible to `caplog`. Confirmed the previously-failing test (`test_empty_chunks_list_returns_empty`) now passes.

Ran full verification before finalizing: `make test-unit` shows 52 failed / 376 passed, with zero new failures introduced (the 52 pre-existing failures are identical with or without my change — confirmed via `git stash` comparison). `make check` reports 182 pre-existing lint errors across unrelated files (`safety/`, various test files) — none in `tests/conftest.py`, the only file I touched. Both `make check` and `make test-unit` were re-run after committing to confirm no new issues.

**Next steps:**
Open a draft PR with a full description (What changed / Root cause / How to test / Pre-existing issues), and share it in the peer review Slack channel for feedback.

**Blockers:**
None currently.

### Check-in 2 (end of week)

**PR link:** https://github.com/ChristopherCastro-dev/pathreview/pull/1

**Branch:** fix/159-structlog-caplog-config

**What you built:**
Added an autouse pytest fixture in `tests/conftest.py` that calls the existing `configure_logging()` function before every test, wiring structlog into Python's standard `logging` module so pytest's `caplog` fixture can capture structlog output. This makes the previously-failing `test_empty_chunks_list_returns_empty` assertion pass without modifying the test itself.

**Tests added or updated:**
No new test file was needed — this fix resolves a test-environment configuration gap, not a missing test. The existing test in `tests/unit/test_batch_processor.py` now passes as-is.

**Self-review confirmation:** [x] make check passes  [x] make test-unit passes
(Both confirmed to introduce zero new failures — 52 pre-existing test failures and 182 pre-existing lint errors exist across unrelated files, documented in the PR description.)

**Draft PR feedback received from:** None — peer review Slack channel was not accessible, so this PR was self-reviewed against the course's pre-submission checklist and marked ready for review directly.

## Week 10 — Iteration & reflection

### Reviewer feedback

**Feedback received:** [ ] Yes  [x] No — still awaiting review

**Summary of feedback:**
No feedback received. The peer review Slack channel wasn't accessible (as noted in Week 9), and no reviewer comments have come in on PR #1 itself either - it currently shows 0 reviews.

**How you responded:**
N/A - no feedback arrived, so no further changes were made beyond the self-review already documented in Week 9 (`make check` and `make test-unit` both confirmed zero new failures via `git stash` comparison).

---

### Reflection

**What was harder than you expected?**
Confirming that my fix didn't introduce new problems took more work than expected. With 52 pre-existing test failures and 182 pre-existing lint errors already in the codebase, a normal test run wouldn't tell me anything useful — I had to isolate my change's effect from the existing noise using `git stash` to compare before/after, rather than just checking for a clean pass.

**What did you learn about working in a large codebase?**
The biggest shift was learning to prove that "pre-existing" failures are actually pre-existing, instead of assuming it. In my own projects, a failing test means I broke something. Here, it might have nothing to do with my change, and demonstrating that (not just asserting it) turned out to be real engineering work, not a side task.

**How did AI tools help — and where did they fall short?**
I used AI while debugging why `caplog` wasn't catching structlog's output, but it pointed me toward the wrong cause at first — I ended up figuring out the actual root cause myself: `configure_logging()` in `core/logging.py` was never being called during tests, so structlog fell back to its own renderer instead of routing through stdlib `logging`, which is what `caplog` hooks into. More broadly, I used AI to understand the codebase and minimize how much I had to read directly, so I could work more efficiently — though on this specific bug, it steered me wrong before I found the answer myself.

**What would you do differently if you started over?**
I probably could have pushed Claude harder to get it pointed at the right answer instead of moving on — I got annoyed and tired of going back and forth with it, so I ended up just working it out myself. In hindsight, sticking with it a bit longer or being more precise about what I was asking might have gotten me to the answer faster than abandoning the AI and starting from scratch.

**What are you most proud of from this module?**
Figuring out that Claude's suggestion for the `caplog` issue wasn't actually correct, and working out the real root cause myself. It would've been easy to just run with what the AI suggested, but recognizing it didn't fit and going back into `core/logging.py` and `conftest.py` to trace the actual cause — that `configure_logging()` was never called during tests — felt like the most "real" engineering moment of this module.