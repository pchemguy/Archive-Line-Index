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

# ⚡ Performance Optimization Task

You are a performance-focused agent. Your mission is to analyze and implement a performance improvement that should make the codebase measurably faster or more efficient.

## Task Details

**File:** `src/archive_line_index/persistence/sqlite.py:69`
**Issue:** Suboptimal SQLite Offset Loading via Iterator

**Language:** python

**Current Code:**
```python
        _validate_read_schema(connection)
        values = []
        for (value,) in connection.execute(
            "SELECT offset FROM line_index ORDER BY offset"
        ):
            if not isinstance(value, int) or isinstance(value, bool):
```

**Rationale:** Using `.fetchall()` and extracting values from the tuples is consistently faster than iterating over the cursor explicitly due to reduced Python overhead. Easy to fix with a list comprehension.

## Your Process

### 1. 🔍 UNDERSTAND - Analyze the Optimization Opportunity

* Review the surrounding code and understand the data flow
* Identify the specific inefficiency (CPU, memory, I/O, allocations, etc.)

### 2. 📊 MEASURE - Establish a Baseline
Before making any changes, you must attempt to establish a performance baseline for the affected code you can use to demonstrate your improvement later.

Find or create a benchmark/profiling method:

* Look for existing benchmark tests or profiling infrastructure
* If none exist, create a focused benchmark or performance measurement for this code path

⚠️ If you cannot measure the performance impact (or it is impractical to do so), document why and your rationale for why this change is a net performance improvement.

### 3. 🔧 IMPLEMENT - Optimize with Precision

* Write clean, understandable optimized code
* Preserve existing functionality exactly
* Consider edge cases that may apply (nil pointers, concurrent access)
* Ensure the optimization is safe

### 4. ✅ VERIFY - Measure the Impact

- Run format and lint checks
- Run the full test suite
- Verify the optimization by measuring the performance impact after your changes
- Ensure no functionality is broken

### 5. 🎁 PRESENT - Share Your Speed Boost

Create a PR with:

- Title: "⚡ [performance improvement description]"
- Description with:
    * 💡 **What:** The optimization implemented
    * 🎯 **Why:** The performance problem it solves
    * 📊 **Measured Improvement:** Discuss your measured performance improvement details, if any. Include key benchmark results (baseline, improvement, and change over baseline), if any.
        * If you were unable to show a meaningful performance improvement, you must mention that clearly upfront and discuss the rationale.

Remember: You're an amazing performance engineer, making things lightning fast. But speed without correctness is useless. Measure, optimize, verify.

---
---

# 🔒 Security Vulnerability Fix Task

You are a security-focused agent. Your mission is to analyze and fix a security vulnerability that could put the codebase or its users at risk.

## Task Details

**File:** `src/archive_line_index/persistence/raw.py:34`
**Issue:** TOCTOU Vulnerability in Temporary File Usage

**Language:** python

**Vulnerable Code:**
```python
    data = _encode_little_endian(validated)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        _write_temporary(temporary, data)

```

**Rationale:** The fix is clear and self-contained (< 20 lines): modify `_write_temporary` to accept and write to the open file descriptor instead of closing it and reopening by path.

## Your Process

### 1. 🔍 UNDERSTAND - Analyze the Security Issue

* Review the surrounding code and understand the data flow
* Identify the specific vulnerability type and its potential impact
* Consider attack vectors and exploitation scenarios

### 2. 🛡️ ASSESS - Evaluate the Risk

Before making changes, assess the security risk:

* What data or functionality could be compromised?
* Who could exploit this vulnerability?
* What is the blast radius if exploited?
* **If possible**, search for known CVEs, advisories, or recommended fixes for this vulnerability type
    - This may reveal simpler solutions (e.g., dependency updates) or important context

### 3. 🔧 IMPLEMENT - Fix with Security in Mind

* Write a secure fix that eliminates the vulnerability
* Follow security best practices for this type of issue
* Ensure the fix doesn't introduce new vulnerabilities
* Preserve existing functionality

### 4. ✅ VERIFY - Validate the Fix

- Run format and lint checks
- Run the full test suite
- Verify the vulnerability is no longer exploitable
- Ensure no functionality is broken
- For non-trivial fixes (more than just a dependency bump), write simple tests that validate your fix
    - If testing is too complex, document detailed rationale for the fix in the PR description instead

### 5. 📝 DOCUMENT - Explain the Security Fix

Create a PR with:

- Title: "🔒 [security fix description]"
- Description with:
    * 🎯 **What:** The vulnerability fixed
    * ⚠️ **Risk:** The potential impact if left unfixed
    * 🛡️ **Solution:** How the fix addresses the vulnerability

Remember: Security is paramount. A fix that introduces new vulnerabilities is worse than no fix at all. Be thorough and careful.

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
