## Merge Gate Checklist (Required)

- [ ] **Branch:** Work is on a feature branch; no contract-changing commits were pushed directly to the default branch.
- [ ] **Scope:** Diff matches the stated problem; no unrelated refactors are included.
- [ ] **CI:** All required checks are green (`gh pr checks <n>` or Checks tab); any flake was investigated before merge.
- [ ] **Generated artifacts:** Required sync/regen steps were run locally; expected generated files are up to date (clean diff where expected).
- [ ] **Tests:** Project tests pass (e.g., `pytest`); new/changed behavior is covered by tests that encode the contract.
- [ ] **Lint/type:** Lint/type checks pass for touched paths (e.g., `ruff`, `mypy`) when configured in CI or project config.
- [ ] **Docs:** README/design docs were updated for caller-relevant behavior (fields, defaults, validation, errors).
- [ ] **Review:** No unresolved review threads; explicit approval from owners of touched surfaces (API/client/core).
- [ ] **Contract wording:** PR “Contract decisions” section matches code behavior exactly (authority rules, validation, errors).
- [ ] **Merge hygiene:** One agreed merge strategy used (squash/rebase/merge); remote feature branch deleted after merge; default branch still builds.
