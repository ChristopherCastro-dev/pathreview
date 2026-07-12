## Week 7 — Issue selection

**Issue link:** https://github.com/jamjamgobambam/pathreview/issues/42

**Issue title:** `tech_detector.py` misclassifies Jupyter notebooks as JSON files

**Tier:** Tier 1 [x] Tier 2 [ ] Tier 3 [ ]

**Problem summary:**
The tech detector in `agent/tools/tech_detector.py` identifies a file's type based on its extension. Since `.ipynb` (Jupyter notebook) files are actually JSON under the hood, the detector currently misclassifies them as generic JSON instead of recognizing them as Python/Jupyter data science work. This means notebook-based contributions aren't being properly credited or categorized by the tool. A successful fix would add a special case so `.ipynb` files are detected and counted separately from plain JSON files.

**Is this right for me? — checklist reasoning:**
I can explain this issue without re-reading it: the tech detector is supposed to misclassify `.ipynb` files as JSON because it detects file type by extension, and `.ipynb` files are JSON under the hood. This is a Tier 1 issue, which fits since this is my first open-source contribution — the fix is localized to a single file (`agent/tools/tech_detector.py`) and doesn't require understanding how the rest of the system works. It's unclaimed (no assignee, no other comments) and the estimated 2-3 hour effort fits comfortably within the Week 8-9 timeline. When I opened `tech_detector.py`, `.ipynb` was already mapped to `"Python"` in `EXT_TO_LANG`, so I'll need to investigate further at the start of Week 8 to confirm whether the bug still reproduces or lives elsewhere in the codebase.

**Branch name:** fix/42-tech-detector-ipynb-json

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger