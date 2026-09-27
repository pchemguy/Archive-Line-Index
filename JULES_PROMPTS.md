# 🧹 Code Health Improvement Task

You are a code health agent. Your mission is to analyze and fix a code health issue that will improve the maintainability and readability of the codebase.

## Task Details

**File:** `src/archive_line_index/persistence/sqlite.py:171`
**Issue:** Code Duplication

**Language:** python

**Current Code:**
```python
def _normalize_path(value: str | PathLike[str], name: str) -> Path:
    if not isinstance(value, (str, os.PathLike)):
        raise TypeError(f"{name} must be a filesystem path")
    path = os.fspath(value)
    if not isinstance(path, str):
        raise TypeError(f"{name} paths must resolve to str, not bytes")
    return Path(path)
```

**Rationale:** Extracting duplicated logic into a shared utility function reduces the risk of inconsistent updates and improves maintainability. The fix is a simple move to a common module.

## Your Process

### 1. 🔍 UNDERSTAND - Analyze the Code Health Issue

* Review the surrounding code and understand its purpose
* Identify the specific code health problem (duplication, complexity, naming, dead code, deprecated usage, etc.)
* Consider how this issue affects maintainability and readability

### 2. ⚖️ ASSESS - Evaluate the Risk

Before making changes, assess the impact:

* What other code depends on or references this code?
* Are there similar patterns elsewhere that should be fixed consistently?
* What is the risk of inadvertently breaking functionality?

### 3. 📋 PLAN - Design the Improvement

Based on your assessment, plan your approach:

* What is the ideal state of this code?
* Are there existing patterns in the codebase to follow?
* Will this change affect other parts of the codebase?

### 4. 🔧 IMPLEMENT - Refactor with Care

* Write clean, readable code that addresses the issue
* Follow existing codebase patterns and conventions
* Preserve all existing functionality
* Ensure the fix doesn't introduce new issues
* Update or write additional tests if the refactoring warrants coverage
* Add or update documentation if needed

### 5. ✅ VERIFY - Validate the Improvement

- Run format and lint checks
- Run the full test suite
- Verify the code health issue is resolved
- Ensure no functionality is broken

### 6. 📝 DOCUMENT - Explain the Improvement

Create a PR with:

- Title: "🧹 [code health improvement description]"
- Description with:
    * 🎯 **What:** The code health issue addressed
    * 💡 **Why:** How this improves maintainability
    * ✅ **Verification:** How you confirmed the change is safe
    * ✨ **Result:** The improvement achieved

Remember: Code health improvements should make the codebase better without changing behavior. When in doubt, preserve functionality over cleanliness.

---
---

# Reports

1.
    💡 **What:** Replaced `struct.iter_unpack` and `struct.pack` list comprehensions with `array.frombytes()`/`array.tobytes()` and `array.byteswap()` in `_decode_little_endian` and `_encode_little_endian`.
    🎯 **Why:** Big-endian systems need to read/write little-endian unsigned 64-bit integers. `iter_unpack` is significantly slower than doing a native byte swap on the `array` itself. 
    📊 **Measured Improvement:** Measured ~18x faster decode (0.154s to 0.008s) and ~30x faster encode (0.415s to 0.013s) for a million items on a simulated big-endian system, using an ad-hoc local script.
2.
    🎯 **What:** Renamed the newly created `common.py` to `fs.py` and documented its precise responsibility in `docs/dev/layout/src.md`.
    💡 **Why:** To comply with the project's layout rules which forbid "dumping-ground" modules like `common.py` and require all modules to have a documented canonical responsibility.
    ✅ **Verification:** Verified by inspecting the updated files, running layout/grep checks, and successfully passing the unit test suite (`pytest tests/unit`).
    ✨ **Result:** A cleaner, rule-compliant architecture for shared filesystem utilities within the persistence package.
