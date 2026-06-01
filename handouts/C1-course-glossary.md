# C1 — Course Glossary

U.S. Energy Developer AI Training · Quick reference for terms used across all five sessions.
Two sentences per term. Scan when a word comes up in session and you want a fast definition.

---

## A

**Agent**
A language model that can plan, use tools, and iterate on its own output — not just generate a single response. In Claude Code, the agent reads files, runs shell commands, edits code, and loops until the task is done.

**Approval mode**
The setting that controls how much the agent can do without stopping to ask you. Ranges from manual (approve every action) to Auto Mode (agent self-assesses risk) to fully unsandboxed inside an isolated VM.

**Auto Mode**
An approval-mode level in Claude Code where the agent decides for itself whether an action is safe enough to proceed without a human pause. It still logs every action; you trade approval friction for throughput.

---

## C

**Claude Code**
Anthropic's terminal-based AI coding agent. It is the exclusive tool for this course; it operates in your shell, reads your project files, and executes commands on your behalf.

**CLAUDE.md**
A markdown file, committed to a repo, that tells Claude Code how to operate in that project. Covers stack details, conventions, commands, anti-goals, and anything else the agent needs that it cannot infer from source files.

**Compact (`/compact`)**
A Claude Code slash command that summarises and compresses the current conversation context, preserving essential information but discarding verbatim detail. Use it before context fills up and degrades quality.

**Context compaction**
What happens when a conversation grows large enough that earlier content is summarised or truncated to fit the model's context window. Good CLAUDE.md and on-demand skill loading reduce how often this matters.

**Context window**
The total amount of text — conversation history, files, tool output, and the response — a model can hold at once. Larger windows are more expensive; context discipline keeps costs reasonable.

---

## F

**FastAPI**
A Python web framework used for all web-app examples in this course. It provides fast request routing and automatic OpenAPI documentation generation.

---

## I

**IFTA** *(International Fuel Tax Agreement)*
A multi-jurisdiction agreement that requires commercial carriers to report and apportion fuel tax owed to each US state and Canadian province based on miles driven there. It is the domain of the Hour 7 CLI example.

---

## J

**Jinja2**
A Python templating engine used to render HTML pages in the course's mileage-logbook web app. Templates live in a `templates/` folder and receive data from FastAPI route handlers.

---

## M

**MCP** *(Model Context Protocol)*
A protocol for extending Claude Code with additional tools and data sources (e.g., databases, APIs). *Not covered in this course* — mentioned here because you may encounter the acronym in the Claude Code documentation.

---

## P

**Planning mode**
A Claude Code behaviour (triggered with `--plan` or the `/plan` flow) where the agent drafts a written plan before executing any changes. The human reviews and approves the plan; implementation follows only after approval.

**Prompt**
The instruction you give the agent. In this course, "writing a good prompt" means making implicit requirements explicit — not typing magic words.

---

## S

**Sandbox**
The set of constraints on what the agent can do without approval. A sandboxed session requires human sign-off before destructive or irreversible actions; an unsandboxed session (inside a VM) removes that friction.

**SKILL.md**
A markdown file that documents a recurring procedure in enough detail that Claude Code can execute it without further explanation. It can be a single file or a folder with referenced sub-files when the procedure is complex.

**Slash command**
A `/keyword` typed at the Claude Code prompt that triggers a built-in behaviour — e.g., `/compact`, `/clear`, `/plan`. See the Claude Code Commands card for the highest-frequency ones.

**SQLite**
A file-based SQL database used in all persistence examples in this course. No server required; the database is a single `.db` file in the project directory.

**Subagent**
A subordinate Claude Code session spawned by a parent session to handle a scoped piece of work in parallel. Subagents make agent teams possible.

---

## V

**Validate-and-correct loop**
The pattern where the agent runs tests (or linters, or type-checkers) after every change, reads the output, and fixes failures before declaring the task done. It is the agentic equivalent of "run the tests."

---

> **Footnote — AGENTS.md:** Some tools (e.g., Cursor, GitHub Copilot) look for `AGENTS.md` rather than `CLAUDE.md`. It is the cross-tool portable equivalent. This course teaches `CLAUDE.md` exclusively.
