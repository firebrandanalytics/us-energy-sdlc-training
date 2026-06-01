# C5 — Approval Mode Decision Matrix

U.S. Energy Developer AI Training · Session 2 (Hour 3) reference card

Scan this card in 30 seconds. Use the middle column as the default.

---

## The Three Modes

| | Manual Approval | Auto Mode | Unsandboxed (VM only) |
|---|---|---|---|
| **What it means** | Agent stops and asks before every file write, shell command, or tool use | Agent self-assesses risk; proceeds on low-risk actions, pauses on high-risk ones | Agent runs freely — no per-action pauses |
| **Best for** | Exploratory sessions in unfamiliar codebases; first time touching production config; any action you want to inspect step by step | Normal development work; building features, running tests, managing dependencies | Long-running automated tasks where you've already validated the plan; running inside a VM where the VM itself is the safety boundary |
| **Throughput** | Slow — you approve every step | Moderate — you pause only on flagged actions | Fast — no interruptions |
| **Safety boundary** | You, reviewing each action | Claude Code's risk assessment + your attention to flagged pauses | The VM or container — not the agent |
| **Appropriate on bare metal?** | Yes | Yes | **No.** Only inside an isolated VM or container |
| **Appropriate for prod systems?** | Yes (maximum control) | Caution — verify Auto Mode's risk assessment matches yours | No |
| **Token / cost impact** | Lowest (you stop often; less re-planning) | Nominal overhead from risk assessment; worth it on enterprise pay-per-use | Runs the longest sessions; highest total token use |

---

## When to Switch Modes

**Start in Manual when:**
- You are opening a codebase for the first time.
- The task touches infrastructure, secrets, or deployment config.
- You are debugging a subtle issue and want to trace every step.
- You're not sure what the agent is about to do.

**Switch to Auto Mode when:**
- You've seen the agent's plan and you trust the direction.
- The task is a well-understood feature build or test-writing session.
- You've written a clear CLAUDE.md and SKILL.md that constrain scope.
- You want to step back and review outputs rather than approve each action.

**Use Unsandboxed (VM) when:**
- You are running a long automated task (e.g., a full build-test-package cycle).
- You have validated the plan and want the agent to run without interruption.
- The machine running Claude Code is a throwaway VM with no access to production systems.
- **Never on your bare-metal workstation for irreversible operations.**

---

## The Auto Mode Pauses to Watch For

Auto Mode still pauses in certain situations. When it does, that is the signal to pay attention.

Common pause triggers (verify with lead instructor):
- Writing or modifying `.env` files
- `git push` to a remote
- Destructive file operations (delete, overwrite outside the working directory)
- Executing scripts with `sudo` or elevated permissions
- Network calls to external services

When Auto Mode pauses and asks, **read the action before approving.** That is still you doing the engineering judgment.

---

## One-Line Summary

> **Manual** = you see everything. **Auto Mode** = you see what matters. **Unsandboxed** = the VM is the guardrail.
