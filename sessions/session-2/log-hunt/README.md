# Log hunt — find the needle in 8,000 lines

A tiny exercise for the "Claude Code as a shell" part of Session 2. It shows three
things at once: the **`!` shell notation**, why the **agent beats you at searching
logs**, and the **find → fix** loop.

## Run it

From this folder, run the job **with the `!` notation** at your Claude Code prompt
(this runs it in your shell and lets Claude see the output):

```
! python noisy_job.py
```

You'll see something like *"ingested 7994/8000; 6 permanently failed. wrote job.log
(8134 lines)."* So 6 records didn't make it — but the log is 8,000+ lines and most
of it is noise. Scrolling it by hand is exactly the kind of thing you shouldn't do.

## Find the failures — without reading the script

Don't open `noisy_job.py` yet (that's cheating — the point is to work from the log).
Ask the agent:

```
A batch job logged 6 permanent record failures in job.log, among thousands of
normal lines and many errors that recovered on retry. The log is far too large to
read — do NOT read the file into context; search it with grep, using an approach
that would still work if the log were a thousand times bigger. Without reading the
source code either: (1) find the 6 real permanent failures and the exact bad value
each carried, distinguishing them from the recovered errors yourself; and (2) give
me one grep-compatible regex I could drop into a log monitor that matches a
permanent failure but not a recovered one.
```

Watch what it does: it **searches** (it won't read the whole file), it figures out
that the real failures are the ones *without* "recovered," and it writes a regex to
isolate them — the kind of pattern that takes a non-expert ten minutes and the agent
ten seconds. Notice you never told it the regex; you told it the *goal*.

## Now fix it

```
Now read noisy_job.py and fix the cause so those records ingest. Then re-run it and
confirm zero permanent failures.
```

The feed sends values like `4,210.5`, `3180.0 gal`, and blanks; the parser assumes a
clean number. After the fix, re-running shows **0 permanent failures**.

## The point

You just used the shell three ways: ran a command yourself (`!`), had the agent
search a big log far faster than you could, and had it fix the cause — all by
describing outcomes, not typing commands or writing regex by hand.
