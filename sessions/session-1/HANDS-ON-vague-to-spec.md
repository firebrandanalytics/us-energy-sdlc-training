# Hands-On: Turn a Vague Data Request into an AI-Ready Spec

U.S. Energy AI Software-Development Training · Session 1 · closing exercise

---

## What you're doing

You have a vague data request — the kind that lands in an email, a ticket, or a
hallway conversation. Your job is to rewrite it as an **AI-ready spec**: precise
enough that an agent could execute it reliably, without a dozen rounds of
"wait, did you mean…?"

You are **not** writing code or querying a database today. (You don't even have
the dataset yet — that arrives in Session 3.) You're practising the *thinking*:
finding the hidden decisions buried in a casual ask and pulling them into the
open. That is the single most valuable habit this course builds, and you'll do
the real, build-it version of this exact request in Session 4.

**Time:** ~15 minutes to draft, then ~5 minutes to share one section with the
group.

---

## The vague ask

Read it the way it would actually arrive — from a desk manager, in passing:

> *"Can you pull together a summary of our fuel volumes by terminal? Monthly is
> fine. Should be quick — just give me the totals so I can see how each terminal
> is doing."*

That's it. That's the whole brief.

It sounds clear. It is not buildable. Every phrase in it hides a decision that
changes the number.

---

## Your task

Open **`handouts/C7-ai-ready-spec-template.md`** (the AI-Ready Spec template) and
work through each section for this request. Don't aim for perfection — aim to
surface the decisions the ask quietly left to you.

Pay special attention to four sections — for a data request, these are where the
correctness lives:

- **Constraints.** "Volumes" — measured how? Most fuel volumes are recorded two
  ways: the raw metered gallons, and a temperature-corrected figure (fuel
  expands and contracts with heat, so a corrected number is what reconciles).
  Which one is the *right* total here? "Monthly" — by which date on the record?
  Where does the data even come from?

- **Anti-Goals.** Resist the urge to build the whole reporting platform. What is
  explicitly *out of scope* for a first, correct summary? (A dashboard? Pricing
  and revenue? Renewable-credit math? Say so.)

- **Acceptance Criteria.** Write at least **three** statements that are checkable
  without a judgment call. "The totals look reasonable" is not one — reasonable
  to whom? Aim for things a second person could verify the same way you would.

- **Glossary.** "Volume" sounds obvious and isn't. So does "terminal." Define
  the terms for the agent the way your desk actually means them.

You do not need to know U.S. Energy's real data model to do this well. In fact,
the most useful thing you can do is **name what you'd need to confirm** — "which
gallons figure is authoritative," "do we count fuel that physically moved but
isn't taxable," "are reversed/voided records already excluded." Writing *"confirm
with the desk"* next to an unknown is a strength, not a gap. It's the whole point:
making implicit knowledge explicit instead of letting the agent guess.

---

## The decisions hiding in "summarize our fuel volumes"

Use these as a nudge if you get stuck — each is a fork the ask silently handed
to you:

- **Which gallons?** Metered (raw) or temperature-corrected? They are different
  numbers. Picking one is a real decision with a real total behind it.
- **What counts as a "volume"?** Does a *reversed* or *voided* record still
  count? Does a *non-physical adjustment* — a paperwork correction that never
  moved a gallon — belong in a physical-volume total?
- **All product, or taxable product?** Some fuel moves physically but is
  tax-exempt (e.g. dyed off-road diesel). Is the manager asking for *everything
  that moved*, or *the taxable subset*? Those are two different reports — and the
  ask doesn't say which, so maybe the answer is both, clearly labelled.
- **"Monthly" by which date?** The date the fuel lifted? When it was billed?
  Where do the month boundaries fall?
- **What's the output?** A printed table? A CSV the manager can open? Something
  that re-runs next month? "So I can see how each terminal is doing" implies
  human-scannable — but the format is still unstated.

You will not resolve all of these with certainty today, and that's fine. The win
is *seeing* them — because the agent won't surface them for you. It will pick a
default for each, silently, and hand you a confident answer that runs and may be
wrong.

---

## Debrief — be ready to share

When the group reconvenes:

1. **Which section was hardest to fill in, and why?**
2. **What did you have to decide that the original ask left completely open?**
3. **If you'd handed the original one-liner to an agent as-is, what do you think
   it would have produced — and would you have trusted it?**

---

## Why this matters for the rest of the course

This is not a warm-up. *"Give me clean monthly volumes by terminal"* is the
actual starting point for **Session 4**, where you'll sharpen it into a real data
spec and direct an agent to build a pipeline against U.S. Energy's dataset. The
gallons-vs-corrected question, the voided records, the tax-exempt fuel — those
turn out to be exactly the things that decide whether the pipeline's numbers are
right.

You're meeting them today as ideas. You'll meet them again as code.

---

> **Takeaway:** a casual data ask is a pile of unmade decisions. The agent will
> make every one of them for you — silently — unless you make them first. The
> spec is where you make them.
