# Pull Request Operations Playbook

A lightweight, repeatable workflow for opening, reviewing, merging, and closing PRs with clean branch hygiene and contract fidelity.

---

## 1) Branching and scope rules

- Create a feature branch from the latest default branch (`main`).
- Never push contract-changing commits directly to `main`.
- Keep each PR scoped to **one** problem statement.
- Avoid unrelated refactors in the same PR.

**Branch naming suggestion**

- `feat/<topic>`
- `fix/<topic>`
- `chore/<topic>`
- `docs/<topic>`

(The `cursor/<topic>` prefix is also fine for agent-driven work when that matches team convention.)

---

## 2) Pre-PR local quality gate

Run these before opening or updating a PR:

```bash
uv sync
uv run pytest
uv run python scripts/sync_dashboard_constants.py
git diff --exit-code dashboard_constants.generated.js
```

**Optional stricter gate (recommended):**

```bash
uv run ruff check .
```

If any check fails, fix before the PR update.

---

## 3) Commit quality standards

- Use clear, imperative commit messages.
- Keep commits logically grouped.
- Prefer small, reviewable diffs.
- If generated files are required by project policy, include them in the same PR.

---

## 4) PR creation template (minimum required sections)

Include these sections in every PR description:

- **TL;DR**
- **Problem statement**
- **Contract decisions** (authority rules, validation, error semantics)
- **What changed** (by module/file)
- **Test and CI evidence** (exact commands + results)
- **Risk / backward compatibility**
- **Reviewer focus**
- **Author checklist**

---

## 5) Merge gate rubric (must pass before merge)

Use the same bar as [`.github/pull_request_template.md`](.github/pull_request_template.md). In short:

1. **Branch discipline** — Feature branch used; no direct contract changes on the default branch.
2. **Scope control** — Diff matches stated problem; no unrelated refactors.
3. **CI health** — Required checks green.
4. **Generated artifacts** — Sync/regen run; expected generated diffs are clean.
5. **Behavioral tests** — Test suite passes; new behavior has contract-locking tests.
6. **Static quality gates** — Lint/type checks pass where configured or expected.
7. **Documentation parity** — Caller-relevant docs are up to date.
8. **Review completeness** — No unresolved threads; required approvals present.
9. **Contract fidelity** — PR contract wording matches code exactly.
10. **Merge hygiene** — Agreed merge strategy used; post-merge cleanup done.

---

## 6) Ready-for-review transition checklist

Before flipping draft → ready:

- [ ] PR description complete and current
- [ ] CI green on latest commit
- [ ] Local tests pass
- [ ] Generated artifact checks clean
- [ ] Reviewer asks are explicit (what to validate)

**Suggested ready-for-review comment**

> CI green, tests passing, generated artifacts clean. Requesting focused review on contract fidelity and caller-facing docs.

---

## 7) Reviewer handling protocol

When reviews arrive:

- Address comments in focused commits.
- Resolve each thread only after code or doc update is in place.
- Re-run relevant tests and checks after changes.
- Post a short “addressed” summary if multiple threads were updated.

---

## 8) Merge execution protocol

**Preferred default:** Squash and merge (unless team policy says otherwise).

**Before clicking merge:**

- Required approvals present
- Zero unresolved threads
- Required CI checks green on latest SHA
- No base drift requiring update or rebase

Use a squash commit title that captures **outcome**, not implementation noise.

---

## 9) Post-merge cleanup protocol

Immediately after merge:

1. Delete remote feature branch.
2. Delete local feature branch (after squash, `git branch -D <branch>` may be required if Git reports “not fully merged”).
3. Update local default branch:

   ```bash
   git checkout main
   git pull --ff-only
   ```

4. Run quick health check:

   ```bash
   uv run pytest
   ```

5. (Optional) Watch default-branch CI for org-level confirmation.

---

## 10) Incident handling / exceptions

If a required gate fails but an urgent merge is needed:

- Document the exception in PR comments.
- Tag owner(s) explicitly.
- Open an immediate follow-up issue or PR with a clear due date.

Do **not** silently bypass contract or CI requirements.

---

## 11) Fast command reference

| Action | Command |
|--------|---------|
| Check PR checks | `gh pr checks <PR_NUMBER>` |
| Mark ready for review | `gh pr ready <PR_NUMBER>` |
| View PR in browser | `gh pr view <PR_NUMBER> --web` |

---

## 12) Definition of done (PR lifecycle)

A PR is **done** when:

- It is **merged**,
- Branch is deleted (**local + remote**),
- Default branch is **synced locally**,
- Post-merge **health check** passed,
- No **unresolved follow-up** obligations remain.
