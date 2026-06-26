# AI Agents Coding Guidelines

Welcome! This document outlines the project structure, design decisions, and coding standards for future AI agents contributing to `gmsad`.

---

## 1. Project Overview

`gmsad` manages Active Directory group Managed Service Account (gMSA) secrets and keytabs on Linux. It retrieves secrets from LDAP, calculates Kerberos keys, and updates local keytab files.

---

## 2. Project Structure

*   **`gmsad/`**: Main Python package containing core components.
    *   **`gmsa.py`**: Manages gMSA account state, password date checking, and rotation workflows.
    *   **`keytab.py`**: Low-level serialization and parsing of the Kerberos keytab binary file format.
    *   **`ldap.py`**: Handles authentication (SASL GSSAPI/Kerberos) and querying attributes from Active Directory domain controllers.
    *   **`salt.py`**: Executes Kerberos pre-authentication AS_REQ handshake to dynamically resolve principal salts.
    *   **`utils.py`**: General helper utilities (DNS query resolutions, background timers).
*   **`scripts/`**: Helper tools for administrators (e.g., dumping keytabs, calculating keys).
*   **`tests/`**: Standard python `unittest` suite.

---

## 3. Development Workflow

### Setup Local Environment
Ensure you create a Python 3.14 virtual environment and install the codebase in editable mode with development dependencies:

#### Windows (PowerShell)
```powershell
# Create environment
py -3.14 -m venv .venv
.venv\Scripts\Activate.ps1

# Install in editable mode with dev tooling
pip install -e .[dev]
```

#### Linux (Bash)
```bash
# Create environment
python3.14 -m venv .venv
source .venv/bin/activate

# Install in editable mode with dev tooling
pip install -e .[dev]
```

### Verification Pipeline
Always verify code changes before finishing:
1.  **Code Style**: Run `ruff check gmsad tests scripts`
2.  **Type Check**: Run `mypy gmsad tests`
3.  **Unit Tests**: Run `python -m unittest discover -s tests`

---

## 4. Coding Standards & Best Practices

Contributors must adhere to the following modern Python standards:

### Target Python Version
*   **Python >= 3.14**. Use modern language constructs.

### Type Annotations
*   **PEP 585 & 604**: Use built-in types for generic parameters (e.g. `list[str]`, `dict[str, int]`) instead of `typing` imports, and `| None` instead of `Optional`.
*   **PEP 673 (`Self`)**: When defining constructors or factory methods (like `from_stream`), define them as class methods (`@classmethod`) returning `Self`, rather than static methods returning string-literal forward references (e.g. `tuple['ClassName', int]`).

### Robust & Cross-Platform Conventions
*   **Explicit File Encoding**: When reading or writing text files, always specify `encoding="utf-8"` in `open()`.
*   **Time Handling**: Do not use `datetime.fromtimestamp(0)` as it raises platform-specific `OSError` on Windows. Use `datetime(1970, 1, 1, tzinfo=datetime.UTC).astimezone()` to represent epoch.
*   **Tests & File Locks**: On Windows, temporary file wrapper locks block concurrent opens. For unit tests handling temporary files, wrap operations inside `tempfile.TemporaryDirectory` blocks and clean them up manually.
