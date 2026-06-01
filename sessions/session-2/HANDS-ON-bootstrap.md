# Hands-On: Bootstrap a Small Project Through Claude Code

U.S. Energy Developer AI Training · Session 2

**Time:** 20–25 minutes · **Goal:** one full end-to-end rep where you *direct*
the agent instead of typing the commands yourself.

---

## What you're doing

You're going to stand up a small, working Python project — from an empty
directory — entirely by directing Claude Code. You won't type the `mkdir`
commands. You won't write the files by hand. You give an instruction, review what
the agent produces, correct it if it's off, and move to the next step.

The domain is your choice. Use a scaffold for the **real task you brought** (the
one you'll run for Homework #1) — a data pull, a small loader, a transform, a
helper script. Or, if you'd rather keep today's rep clean and separate from your
real work, make something up; the domain genuinely doesn't matter. The point is
the *operating practice*: clear instructions, review before accept, steering when
it drifts.

> **Why bootstrap and not just "do the task"?** A fresh project is the cleanest
> possible practice ground for the levers from this session — there's no existing
> code to get tangled in, so every approval prompt, plan, and correction is easy
> to see. You'll point the agent at real, messy code starting in Session 3.

---

## The goal (pass/fail checklist)

By the end, your project directory should contain all of the following. This is
binary — either it's all there and the project runs, or it isn't.

| Item | What it looks like |
|------|--------------------|
| Virtual environment | A `venv/` folder at the project root, created and activated |
| Project structure | At minimum: a package directory (your choice of name) with `__init__.py`, and a `tests/` directory |
| `.gitignore` | Covers at least `venv/`, `__pycache__/`, and `*.pyc` |
| `README.md` | Project name, a one-sentence description, how to create the venv, how to run the tests |
| `requirements.txt` | Exists; includes `pytest`; plus anything your stub needs |
| Git repo | `git init` has been run; at least one commit exists |
| One stub module | A Python file in your package with at least one function (it can just `return None`) |
| One stub test | A test in `tests/` that imports and calls your stub function; the test passes |

**Grading:** from the project root, run `python -m pytest tests/ -v`. If it passes
with no errors, you're done.

> A concrete shape, if you want one. A function `def monthly_volume(rows): ...`
> that returns `None` for now, and a test that imports it and asserts it can be
> called. That stub is a fine seed for the real volume work you'll build later in
> the course — but anything that satisfies the checklist counts.

---

## How to approach it

The one constraint: **direct Claude Code to do the work.** Don't type the
commands yourself; describe the outcome and let the agent execute. Each step is
an instruction, a review, and a correction if needed.

### Suggested sequence

1. **Plan first.** Cycle into plan mode (`Shift+Tab`) or just ask:
   *"Before you write anything, give me a plan to bootstrap a new Python project
   called `<name>` — one sentence on what it does, the directory structure, a
   venv, pytest installed, a stub module with one function, a stub test, a
   `.gitignore`, a README, and an initial git commit. List the files you'll
   create and the order. Don't write anything until I say proceed."*
   Read the plan. Does it match what you intended? Correct the scope, then say
   `proceed`.
2. Let it **create the structure, the venv, and install pytest.**
3. Have it **write the stub module** with one function.
4. Have it **write a stub test** that imports and calls that function.
5. Have it **write the `.gitignore`** for a Python project.
6. Have it **write the README** with setup and test instructions.
7. Have it **`git init` and make the first commit.**
8. Run `python -m pytest tests/ -v`. If it fails, tell the agent exactly what
   failed and have it fix it — don't fix it by hand.

### Practice the levers from this session while you work

This rep is where today's controls become muscle memory. Deliberately use each:

- **Approval modes.** Start in **Manual** — approve each action so you see what
  the agent is doing. Once you trust the direction (usually after a couple of
  steps), `Shift+Tab` to **Auto Mode** and let the routine file edits flow. Notice
  it still pauses before shell commands.
- **`Ctrl+E` at a prompt.** On at least one approval prompt — the venv creation or
  the `git init` is a good one — press `Ctrl+E` to see the exact command before you
  approve it. Build this habit now; you'll use it on every risky prompt for the
  rest of the course.
- **Review before you accept.** Before each file is written, glance at it. If
  something's wrong, say so *before* approving. This is the same review discipline
  you'll apply to every task — including the homework.
- **Watch what ambiguity does.** If the agent does something you didn't expect,
  look back at what you asked. Can you see why it made that choice? That gap —
  between what you meant and what you said — is the thing Session 1 was about, and
  it shows up immediately here.

---

## Quick troubleshooting

- **`python` not found:** try `python3`. If neither works, flag it — your
  environment setup may need attention.
- **venv activation (Windows / Git Bash):** `source venv/Scripts/activate`
- **venv activation (macOS / Linux):** `source venv/bin/activate`
- **`pytest` not found after installing:** make sure the venv is activated before
  you run pytest.
- **Import error in the test:** the test's import path has to match the package
  layout. Ask the agent to check the import — don't patch it by hand.

---

## After the exercise

Keep this project. If your stub seeds the real task you brought, it's a head
start on Homework #1. If you made something up today, that's fine too — the rep
was the point, and you'll bring your own real task to the homework.
