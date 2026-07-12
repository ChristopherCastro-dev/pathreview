## Week 7 — Issue selection

**Issue link:** https://github.com/jamjamgobambam/pathreview/issues/42

**Issue title:** `tech_detector.py` misclassifies Jupyter notebooks as JSON files

**Tier:** Tier 1 [x] Tier 2 [ ] Tier 3 [ ]

**Problem summary:**
The tech detector in `agent/tools/tech_detector.py` identifies a file's type based on its extension. Since `.ipynb` (Jupyter notebook) files are actually JSON under the hood, the detector currently misclassifies them as generic JSON instead of recognizing them as Python/Jupyter data science work. This means notebook-based contributions aren't being properly credited or categorized by the tool. A successful fix would add a special case so `.ipynb` files are detected and counted separately from plain JSON files.

**Branch name:** fix/42-tech-detector-ipynb-json

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger