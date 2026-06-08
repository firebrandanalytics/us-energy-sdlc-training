# Homework #1 — Learn a Shell Trick from the Agent

**Assigned after:** Session 2
**Due before:** Session 3
**Time budget:** 30–45 minutes

---

## The Assignment

Today you used Claude Code as a **shell** — it runs commands, and you watched it
tear through an 8,000-line log with a regex. We ran short on that exercise in class,
so this homework has **two parts**:

1. **Finish the log hunt.** Point the agent at the log and get it to pin the one
   real error (the failure with **no "recovered" line after it**), then propose the
   fix. Bring the regex/`grep` that found it.
2. **Turn it around.** Use the agent as a **patient command-line tutor**, and bring
   back one new technique you learned.

Part 2 is the bulk of the assignment — here's how it works.

As you work, **inspect the commands the agent runs and have it teach you the ones
you don't know.** Bring **one new command-line technique** you learned to Session 3
— not just a single flag, but a *technique* (a pipe idiom, a regex construct, a
shell symbol like `${}` or `2>&1`). Many of us are light on the command line; this
is the fastest way to level up, with a tutor who explains on demand.

---

## How it works

The move has two steps, and you'll repeat it whenever something looks unfamiliar:

1. **See the command.** Keep Claude Code in an **approval mode** (the default, or
   Manual) — *not* bypass/auto-everything — so it pauses and shows you each command
   before it runs. Read the command in the prompt. If it's long or collapsed,
   press **Ctrl+E** to expand it.
2. **Ask the agent to explain it.** Before you approve (or right after), ask:
   *"Explain that command — what does each part do?"* or *"what does `uniq -c` do?"*
   or *"walk me through that regex piece by piece."* The agent is a tutor that never
   gets tired of "what does this do?"

> This is the same **inspect-before-approve** habit from today's governance point —
> you review what the agent does before you let it run. Here you also *learn* from
> it. Two wins from one habit.

**Setup notes:**
- **Windows: use Git Bash** (install Git for Windows if you haven't). Claude Code
  runs commands through Bash, so you'll see standard Unix syntax — pipes, `grep`,
  `head`, `${}` — which is what we want.
- **Stay in an approval mode.** In bypass/"don't ask" mode there are no prompts to
  read, so you'd miss the whole point.

---

## What to do

Either bring your own small task, **or** use the starter prompts below (great if
you're newer to the command line — they reliably produce commands worth learning).
Point the agent at any folder with a few files in it — your log-hunt folder from
class works, or any project.

### Starter prompts (each one surfaces a real technique)

1. **A multi-stage pipe** *(tested — this one always produces a rich command):*
   > *"What are the 10 most common words in `README.md` (or any text file here),
   > with their counts?"*

   You'll see something like
   `tr '[:upper:]' '[:lower:]' < file | tr -cs '[:alpha:]' '\n' | sort | uniq -c | sort -rn | head`.
   Ask: *"explain each stage of that pipe."* That one line teaches `tr`, `|`,
   `sort`, `uniq -c`, and `head` — a huge amount of shell in one go.

2. **A regex search.**
   > *"Find every email address (or every URL) in the files here."*

   It'll write a `grep -E`/`grep -P` with a regex. Ask: *"explain that regex,
   piece by piece — what does each symbol match?"*

3. **Sort + top-N.**
   > *"Show me the 5 largest files under this folder."*

   Watch for `sort`, `head`, and flags like `-rh`. Ask what `-r`, `-h`, `-n` do.

4. **A real CLI tool.**
   > *"Fetch just the HTTP status code for https://example.com — nothing else."*

   It'll reach for `curl` with flags like `-s -o /dev/null -w "%{http_code}"`. Ask:
   *"what is each of those curl flags doing?"* (Needs internet — fine from your desk.)

5. **Stretch — shell symbols.**
   > *"Show me the command to rename every `.txt` file here to `.md` — don't run it,
   > just show me and explain it."*

   You'll meet a loop and parameter expansion like `${f%.txt}`. Ask what `${f%.txt}`
   means — that `${...}` syntax is one of the highest-leverage things to know.

---

## What to Bring to Session 3

**From the log hunt:** which regex or `grep` finally pinned the real error, and the
one-line fix you'd make. (One sentence is plenty.)

**One command-line technique you learned from the agent** — be ready to say, in one
sentence each:

1. **The technique** (e.g., *"piping to `sort | uniq -c | sort -rn` to count and
   rank things,"* or *"`grep -P` with a lookahead,"* or *"`${var%.ext}` to strip a
   file extension"*).
2. **What it does**, in your own words.
3. **When you'd use it** on your real work.

We'll open Session 3 with a few of these — a quick round of "here's a trick I picked
up." Bring the one that surprised you most.

---

## Tips

- **Don't just collect flags — look for techniques.** `grep -i` is a flag;
  `grep -oP "...\K..."` to *extract* a value is a technique. The second kind is
  what's worth sharing.
- **Make it explain, don't just accept.** The value is in the question "what does
  this do?", asked the moment something looks unfamiliar — not in approving fast.
- **It's fine to decline and ask.** If a command looks confusing, decline the
  approval and ask the agent to explain (and to propose a simpler version). You're
  the reviewer; understanding before approving is the job.

---

*Reference cards: **CC — Claude Code Commands** (approval keys, including Ctrl+E),
**C5 — Approval Modes**. Questions? Session 3 opens with the share-back.*
