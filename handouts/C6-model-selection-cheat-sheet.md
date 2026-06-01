# C6 — Model Selection Cheat Sheet

U.S. Energy Developer AI Training · Session 2 (Hour 3) reference

No prices — they change. Use relative cost and behavior to make the call.
---

## The Three Tiers

| | Haiku | Sonnet | Opus |
|---|---|---|---|
| **Relative cost** | Lowest | Moderate | Highest |
| **Relative speed** | Fastest | Moderate | Slowest |
| **Reasoning depth** | Adequate for simple, well-defined tasks | Strong for most engineering work | Best for complex reasoning, architecture, and ambiguous problems |
| **Context handling** | Handles shorter contexts well | Handles typical project contexts well | Best at maintaining coherence over very long contexts |

---

## When to Use Each

### Haiku — use it for high-volume, fast, mechanical tasks

- Generating boilerplate (test stubs, CRUD routes, docstrings)
- Reformatting or linting fixes
- Simple search-and-replace across many files
- Ad-hoc one-liner scripts with a clear spec
- Quick "explain this function" questions
- Iterating rapidly on a working prompt — get the shape right cheaply, then run the real version

**Course note:** Default to Haiku in all examples where the task involves calling an LLM from code — keeps the demo fast and the cost low.

### Sonnet — your everyday workhorse

- Building a feature from a clear spec and acceptance criteria
- Writing and expanding a test suite
- Navigating a codebase to understand an architecture
- Reviewing AI-generated code for logic errors
- Refactoring with a defined scope (e.g., "extract a service layer from routes")
- Most of the work in Hours 7–9

**Rule of thumb:** If you're not sure, start with Sonnet. It handles the overwhelming majority of professional engineering tasks without stepping up to Opus cost.

### Opus — bring it in when depth matters

- Sharpening vague or contradictory requirements into a coherent design
- Architecture decisions with significant trade-offs
- Complex algorithmic problems where Sonnet gives shallow or incorrect answers
- Writing a SKILL.md or CLAUDE.md that captures subtle domain knowledge
- Debugging a particularly subtle failure where other tiers keep reaching the wrong conclusion
- "Plan" passes — let Opus produce the plan, then switch to Sonnet for execution

**Cost discipline:** Opus costs more per token and runs slower. Reserve it for work that genuinely requires its reasoning depth. Don't use it because "I want the best" — use it because the task warrants it.

---

## Practical Patterns

**The Plan/Execute split:**
Use Opus (or Sonnet) for the planning pass. Once the plan is approved, run execution with Sonnet or Haiku. You get Opus-quality architecture at a fraction of full-Opus cost.

**The iteration pattern:**
Prototype with Haiku. When the shape is right, run the final clean implementation pass with Sonnet.

**Escalate when stuck:**
If Sonnet gives you a repeated wrong answer, switch to Opus for that specific sub-problem, get a solution, then return to Sonnet for the surrounding work.

---

## Signs You're Using the Wrong Tier

| Symptom | Likely problem | Fix |
|---------|---------------|-----|
| Sessions are slow and expensive, but the tasks are routine | Defaulting to Opus unnecessarily | Drop to Sonnet for feature builds |
| Agent generates boilerplate incorrectly or slowly | Asking Haiku for something requiring judgment | Step up to Sonnet |
| Planning pass gives shallow answers | Sonnet struggling with ambiguous requirements | Escalate to Opus for planning |
| Demo or test run is slow | Using Sonnet/Opus in a context where Haiku would do | Switch to Haiku for demos |

---

## One-Line Summary

> **Haiku** = fast and cheap for mechanical tasks. **Sonnet** = most engineering work. **Opus** = complex reasoning and planning.
