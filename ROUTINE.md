# Week Routine: Productize for Prince & Team

**Anchor (2026-05-14 → 2026-05-20):** Carry the project from "code shipped on main" to "team using it, feedback loop closed, next anchor named."

*Previous routine: 5-day discipline drill (API & Data Operations) — closed 2026-05-13. See git log for that commit history.*

---

## Day 1 — Wed 05-14: Pages Live & Verified

**Move:** Enable GitHub Pages on `caraxesthebloodwyrm02/token-type-calculator` (Settings → Pages → branch `main`, root `/`). Confirm `https://caraxesthebloodwyrm02.github.io/token-type-calculator/` loads and computes a scenario end-to-end in the browser.

**Drill:** Open the deployed URL in an incognito window. Run three scenarios (moony, one GATE_ON path, one no-take boundary). Confirm all three produce expected `TokenType` and zone outputs — no fetch calls, no backend.

**Outcome:** A stable public URL. The team can open a link, not clone a repo.

---

## Day 2 — Thu 05-15: Human-Readable Onboarding

**Move:** Write a `QUICKSTART.md` at the repo root targeting a non-developer reader. Cover: what the calculator does in one paragraph, how to open the dashboard (URL link + local fallback), what the three key controls mean (token list, step count, one worked example).

**Drill:** Read the file aloud end-to-end as if you are the first-time team member. Cut anything that requires prior context to decode.

**Outcome:** A team member with no project history can use the dashboard within two minutes of reading the file.

---

## Day 3 — Fri 05-16: Share & Capture Feedback

**Move:** Send the Pages URL and `QUICKSTART.md` link to at least two people on the team. Attach three questions: (1) Was anything confusing in the first 60 seconds? (2) Which output is most immediately useful to you? (3) What is missing that you expected to find?

**Drill:** Log each response verbatim in a scratch note (`feedback-day3.md`, gitignored). Do not interpret yet — just capture.

**Outcome:** Raw feedback in hand before triage.

---

## Day 4 — Mon 05-19: Triage Feedback

**Move:** Read the captured responses. Classify each item: bug / UX friction / missing feature / out of scope. Rank the top three actionable items by impact-to-effort ratio.

**Drill:** For each top-three item, write one sentence stating the acceptance criterion for "done." If an item cannot be stated that concisely, break it down further.

**Outcome:** A ranked, acceptance-criterioned shortlist. The Day 5 target is the top item.

---

## Day 5 — Tue 05-20 (morning): Ship One Improvement

**Move:** Implement the top-ranked feedback item from Day 4. Branch → change → `uv run pytest` green → PR through the merge gate defined in `.github/pull_request_template.md` → merge to `main`. Pages redeploys automatically.

**Drill:** Verify the deployed URL reflects the change before closing the session.

**Outcome:** One concrete improvement shipped and live — closes the feedback loop.

---

## Day 5 — Tue 05-20 (afternoon): Lineage Architecture Decision

**Move:** Decide whether shared trajectory matters for the team. The trajectory store (`token_calc.db`, `marauders_map.py`) is local-only and does not travel with the static deploy. Three options: (A) keep it local-only — each user's history is private; (B) export a summary view (JSON snapshot) that can be committed and rendered on the dashboard; (C) scope a lightweight shared backend. Read `DESIGN.md` storage section before deciding.

**Drill:** State the decision in one paragraph in `DESIGN.md` under a new "Shared Lineage" heading. Even "stay local for now, revisit if the team grows" is a valid and complete decision.

**Outcome:** Lineage stance is documented and no longer an open architectural question.

---

## Day 6 — Tue 05-20 (close): Reflect & Name Next Anchor

**Move:** Review the week: what shipped, what feedback revealed, what the lineage decision forecloses or opens. Write the next anchor — one sentence — at the top of `.claude-progress.md`.

**Outcome:** The session ends with a named next anchor and a clear handoff state.

---

## Routine status

**Active — week of 2026-05-14.**

---

*Project commands (`uv run pytest`, API server, dashboard sync, batch client) live in [AGENTS.md](AGENTS.md) — canonical reference for all build and run operations.*
