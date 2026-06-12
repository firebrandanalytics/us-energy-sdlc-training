# Lab Guide: Close Your Loop — Session 5

U.S. Energy AI Software-Development Training · Session 5 (hour 1; the second hour
is a separate presentation)

Session 4 ran the loop; today **everyone finishes their own**. The room is at
different steps — that's expected, and this guide is built for it: find your rung
on the ladder below and climb from wherever you are. Steps 1–8 still live in the
**Session 4 lab guide** (`../session-4/LAB-GUIDE.md`); this guide adds the two
that close the loop — **Step 9, the clean-context review and merge**, and
**Step 10, closing the tickets** — which you'll watch demonstrated before the
work block.

---

## How the hour runs

| Elapsed | What's happening |
|---:|---|
| 0–10 | Share-back: finishing the steps solo — what held, what fought you |
| 10–15 | **Demo: the loop closes** (Steps 9–10, live on the instructor repo) + where it was all headed |
| **15–45** | **Work block (30 min)** — the ladder below; continue from wherever you are |
| 45–60 | The series, tied together — then the handoff |

---

## Before you climb (everyone, ~3 min)

```bash
# 1) Fresh course materials (run inside the course repo):
cd us-energy-sdlc-training && git pull

# 2) Back to YOUR repo — the sibling you created in Session 4:
cd ../<initials>-volume-service

# 3) Start Claude Code here:
claude
```

Then paste the **re-entry prompt** — a fresh session has no memory of Thursday,
so make it rebuild the picture from the artifacts (this is the same move as
Step 9's review, in miniature):

```
Read whatever exists of: SPEC.md, stories.md, PLAN.md, test_service.py,
service.py, ARCHITECTURE.md, PR.md — plus git log --oneline and git status.
Against this checklist — (1) spec, (2) skill, (3) stories on the board +
foundation commit + story branch, (4) tests-first build to green, (5) validation
evidence (pytest + reconcile + run log ↔ database), (6) the lift_count change
absorbed with a before/after log diff, (7) ARCHITECTURE.md, (8) approved commit,
push, PR — tell me exactly what's DONE, what's HALF-DONE, and the single next
action. Don't do anything yet.
```

Read its answer, check it against what you remember, and start there.

---

## The ladder — find your rung

| Where you actually are | Start here |
|---|---|
| Mid-Steps 1–8 (most of the room) | Resume at your step in `../session-4/LAB-GUIDE.md`. **Today's target: through Step 5, the done-gate** — a validated service beats a rushed PR. |
| Steps 1–8 done; PR open (or PR.md ready) | **Step 9 below** — the clean-context review, then the merge. |
| Merged | **Step 10 below** — close the tickets. ~5 minutes, very satisfying. |
| Loop closed | **Homework 3** (`../../homework/homework-3-brief.md`) — the dashboard skeleton on your service. |
| Dashboard running too | **`EXTRA-CREDIT.md`** (this folder) — extend it with parallel subagents — and handout **C11** for the power tools. |

Never started, or Session 4 went sideways? The Environment section of the
Session 4 guide gets you a repo in ~5 minutes — wave the instructor over and
start at Step 1. (No Homework 2 dossier to paste? Ask — we'll hand you one.)

---

## Step 9 — The clean-context review, then the merge (~10 min)

You wrote this code (well — you directed it). You've been staring at it since
Thursday. You are exactly the wrong person to review it, and so is the session
that built it: it *wants* to have been right. The fix is the same one a real team
uses — **fresh eyes**. Open a **new terminal**, and start a **brand-new Claude
Code session** in your repo (a new `claude` — not the session that did the work;
context is the whole point):

```
You have no prior context on this work — that's deliberate. You are the
REVIEWER, not the author. Review the story branch as a senior engineer would:

1. Read SPEC.md and the acceptance criteria in stories.md — that's the standard.
2. Read the actual diff: git diff main...HEAD.
3. Interrogate the tests: do they encode the contract fields, the invariants,
   and the exact reconciliation anchors? Could they pass while the spec is
   violated?
4. Don't take the PR description's word for anything: run pytest yourself, and
   re-run the reconcile against ../us-energy-sdlc-training/data/vol_report.py.
5. Verdict: APPROVE or REQUEST CHANGES, with at most three findings, each with
   file:line evidence. Nitpicks last, clearly labeled.
```

**Read the verdict the way you'd read a colleague's review.** If it found
something real, fix it in your original session (or this one) and re-run the
tests. If it only found nitpicks — congratulations, that's what shipping feels
like.

**Log the review where the work lives, then merge:**

```
Post the review verdict to my service story's work item:
az boards work-item update --id <service-story-id> --discussion "<one-paragraph
verdict + findings>". Then list my open PRs (az repos pr list -o table), and
complete my PR: az repos pr update --id <PR-id> --status completed. If DevOps
says the merge is queued or still analyzing, wait a few seconds and run the
update again.
```

> **Fallback (no DevOps):** the review above works identically — it's reading
> your local branch. Merge locally instead: `git switch main && git merge
> story/<id>-volume-service`, and note the verdict at the top of `stories.md`.

---

## Step 10 — Close the tickets (~5 min)

Close **what merged, not what you hope**: the merge delivered your service story
and (if you built the CLI with it) the reconcile-CLI story. The dashboard
stories stay open — they're Homework 3 / extra credit.

```
Close the stories the merge delivered:
az boards work-item update --id <service-story-id> --state Closed
az boards work-item update --id <cli-story-id> --state Closed
Then show me the board state: az boards work-item list (or query) — I want to
see Closed next to the right items and nothing else touched.
```

That's the loop: an ask became a spec, a spec became stories, stories became a
branch, a branch became reviewed, merged code — and the board says so. *(No
DevOps: mark them closed in `stories.md` with the date. Same loop, smaller
board.)*

---

## If the 30 minutes runs out mid-step

Stop where you are and note your next action at the top of `stories.md` — the
re-entry prompt above will pick it up whenever you come back. Everything on this
ladder works exactly the same at your desk tomorrow: nothing here needed the
classroom except the company.

---

## While the agent works — still true today

`/btw <question>` answers side questions in an overlay without disturbing the
build. The stall-nudge from Session 4 still applies if a resumed build stops
mid-flight: *"Continue from the approved plan. Run the failing tests if they
haven't run, then implement, run pytest, and iterate until green."* And the
ground rule stands: the course repo is read-only reference — `data/` only.
