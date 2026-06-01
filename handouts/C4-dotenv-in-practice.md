# C4 — .env in Practice

U.S. Energy Developer AI Training · Session 3 (Hour 5) reference card

---

## Why .env Matters for AI-Assisted Work

The "Make Correctness Easy" principle says: take work away from the AI that you don't need it to manage. Putting database paths, API keys, and environment names into `.env` means the agent never has to guess, hard-code, or ask. It reads the variable; it gets the right value.

Security is a second benefit, not the first one. The first one is removing working-memory load from the agent.

---

## What Goes in .env

| Put it in .env | Don't put it in .env |
|----------------|----------------------|
| Database connection strings and paths | Passwords typed in plaintext in source code (already a bug) |
| API keys and tokens | Constants that are the same in every environment (put in `config.py` or a constant) |
| Environment name (`development`, `staging`, `production`) | Logic — `.env` is data, not code |
| External service URLs that differ per environment | Secrets that need rotation policies (use a vault or secrets manager instead) |
| Port numbers and hostnames that differ per environment | Values that belong in a database or config table |
| Feature flags that vary by environment | |

---

## How to Keep .env Out of Git

**Step 1 — Add to `.gitignore`:**

```
# .gitignore
.env
.env.local
.env.*.local
```

**Step 2 — Commit a `.env.example` instead:**

```bash
# .env.example  ← committed to the repo
DB_PATH=./data/logbook.db
APP_ENV=development
AZURE_CLIENT_ID=
AZURE_TENANT_ID=
```

`.env.example` has all the variable *names* and safe placeholder *values*. Developers copy it: `cp .env.example .env` and fill in real values locally. The real `.env` is never committed.

**Step 3 — Audit before committing:**

```bash
git diff --staged | grep -i "secret\|password\|key\|token"
```

---

## Loading .env in Python

Install `python-dotenv`:

```bash
pip install python-dotenv
```

Load at the top of your entry point (`main.py` or `app/__init__.py`):

```python
from dotenv import load_dotenv
import os

load_dotenv()          # reads .env from the current working directory

DB_PATH = os.environ["DB_PATH"]      # raises KeyError if missing — intentional
APP_ENV = os.getenv("APP_ENV", "development")  # optional with a default
```

> **Prefer `os.environ["KEY"]` over `os.getenv("KEY")` for required variables.** A
> missing required variable should fail loudly at startup, not silently produce
> wrong behaviour deep in a session.

---

## How to Reference .env Variables in Claude Code Sessions

Claude Code inherits your shell's environment. If you have sourced or loaded `.env` in your shell before starting Claude Code, the agent can reference those variables in the commands it runs.

**Option A — let the app load it (recommended):**
Wire `load_dotenv()` into your application; Claude Code runs your app and the variables are loaded automatically.

**Option B — export in your shell before starting Claude Code:**

```bash
# Git Bash / macOS / Linux
export $(grep -v '^#' .env | xargs)
```

**Option C — reference in CLAUDE.md:**
Tell Claude Code where to look:

```markdown
## Secrets & Environment Variables
Expected in `.env` (repo root, not committed).
Load with `python-dotenv`; already wired in `app/main.py`.
Variables: DB_PATH, APP_ENV, AZURE_CLIENT_ID, AZURE_TENANT_ID.
```

The agent now knows the variable names and where they come from, without ever seeing the values.

---

## Security Gotchas

- **Never paste a real API key into a Claude Code prompt.** It lands in conversation history, which is visible in logs. Put it in `.env` and reference it by name.
- **`.env` in a shared folder is not secure.** If multiple people can read the folder (e.g., a network drive), treat it like any other plain-text credential store and use a proper secrets manager.
- **Rotation:** if a key in `.env` is compromised, rotate the key at the source first, then update `.env`. Don't just update `.env` — the old key may still be active.
- **CI/CD:** `.env` files don't exist in CI pipelines. Use your CI system's secret variables (Azure DevOps pipeline variables, GitHub Actions secrets) and inject them as environment variables at runtime.

---

## Quick Checklist

- [ ] `.env` is in `.gitignore`
- [ ] `.env.example` is committed with all variable names and no real values
- [ ] `load_dotenv()` is called at application startup
- [ ] Required variables use `os.environ["KEY"]` (fail loudly if missing)
- [ ] No real secrets appear in CLAUDE.md, prompt history, or source files
- [ ] CI pipeline injects secrets via pipeline variables, not a committed file
