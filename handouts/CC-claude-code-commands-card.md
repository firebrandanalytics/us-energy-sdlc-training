# Claude Code Commands — Muscle-Memory Card

U.S. Energy Developer AI Training · Instructor request — highest-frequency commands only

These are the ~20 commands, shortcuts, and features you'll reach for every day.
Not exhaustive — just the ones worth memorising. A few keyboard shortcuts
differ on Windows; those are noted inline. Verify the current Claude Code
version for exact syntax.

---

## Starting a Session

Run these in your terminal (Git Bash on Windows) to start Claude Code.

| What you want | How to do it |
|--------------|-------------|
| Start Claude Code in the current directory | `claude` |
| Start with a specific model | `claude --model claude-haiku-4-5` |
| Start in planning mode (plan before executing) | `claude --permission-mode plan` |
| Resume the previous session | `claude --continue` |
| Pick an earlier session to resume | `claude --resume` |

---

## During a Session — Slash Commands

Type these at the Claude Code prompt (the `>` line).

| Command | What it does |
|---------|-------------|
| `/help` | List available slash commands |
| `/plan` | Ask Claude to write a plan for what it's about to do, and pause for your approval before executing anything |
| `/compact` | Summarise and compress the conversation context. Use before context fills up and quality degrades. Does NOT start a new conversation — history is summarised, not cleared. |
| `/clear` | Clear the conversation entirely and start fresh. Use when you are done with a task and starting something unrelated, or when the context has drifted far from the current task. |
| `/status` | Show current session info — model, context usage, approval mode |
| `/model <name>` | Switch the model mid-session |
| `/doctor` | Diagnose a broken setup — checks your install, config, and environment, and can offer fixes |

---

## Keyboard Shortcuts

These work *inside* a Claude Code session — no slash, just the keys.

**Controlling the session**

| Keys | What it does |
|------|-------------|
| `Ctrl+C` | Interrupt — stop Claude while it is working |
| `Esc` | Cancel / clear the prompt you are typing |
| `Ctrl+D` | Exit Claude Code |
| `↑` / `↓` | Scroll back through your previous prompts |
| `Ctrl+R` | Search your prompt history |

**Writing a prompt**

| Keys | What it does |
|------|-------------|
| `Ctrl+J` | New line *without* submitting — for multi-line prompts |
| `Ctrl+G` | Open your prompt in an external editor (handy for long prompts) |
| `Ctrl+V` | Paste an image — e.g. a screenshot (Windows / Git Bash: `Alt+V`) |

**Seeing what happened**

| Keys | What it does |
|------|-------------|
| `Ctrl+O` | Toggle the full transcript — every tool call and the full output |
| `Ctrl+T` | Toggle the task / to-do list |

> Shortcuts are customisable — run `/keybindings` to see or change them.

---

## Permission & Approval

Two things to know here: which *mode* you are in, and what you press when
Claude *asks*.

**Cycle the approval mode** — press `Shift+Tab` to rotate through three modes:

1. **Manual** — Claude asks before every action (the default)
2. **Auto-accept edits** ("Auto Mode") — file edits apply automatically; shell commands still ask
3. **Plan mode** — Claude only plans; it writes nothing until you approve the plan

The current mode is shown in the input box as you work.

**At a permission prompt** — when Claude stops to ask before running something:

| Keys | What it does |
|------|-------------|
| `Y` or `Enter` | Approve this action |
| `N` or `Esc` | Decline it |
| `Ctrl+E` | **Toggle the explanation** — show exactly what the action will do before you decide |

> **`Ctrl+E` is the one to build muscle memory for.** On anything you are not
> sure about — an unfamiliar command, a multi-file edit — press `Ctrl+E` first,
> read what it actually does, *then* approve or decline. You can also ask Claude
> in plain English before approving (see Useful One-Liners below).

> **Quick discipline:** start a new codebase in Manual mode. Move to
> Auto-accept once you have seen a few actions and trust the direction.

---

## Context Management — When to Use Which

| Situation | Right move |
|-----------|-----------|
| Context is filling up but you're mid-task | `/compact` — preserves the task, compresses history |
| Task is complete; starting something unrelated | `/clear` — start fresh |
| New day, new task, unclear what's in context | Start a new `claude` session entirely |
| Context has drifted (agent is giving stale answers) | `/clear` and re-state the task cleanly |

> **Rule of thumb:** if you feel like you're fighting the context to get a good answer, clear it. The re-statement cost is lower than the compounding cost of a confused agent.

---

## Referencing Files

Claude Code can read files directly — you don't need to paste content.

```
Read main.py and tell me where the delete endpoint should go.
```

```
Before you start, read CLAUDE.md, db.py, and service.py.
```

```
Look at the failing test in tests/test_routes.py and fix what's failing.
```

> **Tip:** Tell the agent which files to read *before* it writes anything. Saves a round-trip of "I assumed the schema was X but it's actually Y."

---

## Useful One-Liners

```bash
# Ask Claude Code to explain a change before you approve it
# (just type this at the > prompt, mid-session)
What exactly will you change, and why? Show me the file paths and the lines affected.

# Planning mode — ask for a plan first
Plan the implementation of [feature] before you write any code.
List the files you'll touch and the order you'll work in.

# Asking for a review pass
Read the diff in [file] and tell me if anything looks wrong before I commit.

# Anchoring scope (mileage-logbook example)
Only modify db.py and tests/test_db.py. Do not touch main.py or service.py yet.
```

---

## Things Worth Knowing

- **Claude Code inherits your shell's environment.** Variables you export in your shell (or load from `.env`) are available to the commands the agent runs.
- **Conversation history is not saved between separate `claude` invocations** (unless you use `--continue`). If you close the terminal, the context is gone.
- **The agent sees your working directory.** It reads files relative to where you started `claude`. Start from the repo root.
- **Long outputs get truncated in display** but the agent received the full content. Press `Ctrl+O` to expand the transcript, or ask the agent to write the full output to a file.
