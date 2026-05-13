## Merge Gate (Every PR)

Before marking a PR ready or merging, all of the following must be true:

- [ ] **Branch discipline:** Use a feature branch; do not push contract-changing work directly to the default branch.
- [ ] **Scope control:** Keep the diff tightly aligned to the stated problem; exclude unrelated refactors.
- [ ] **CI health:** All required checks must be green (`gh pr checks <n>` or GitHub Checks tab). Do not merge red builds.
- [ ] **Generated files:** Run required sync/regen steps locally and ensure generated artifacts match expected state.
- [ ] **Behavioral tests:** Test suite passes, and any changed behavior is covered by tests that encode the contract.
- [ ] **Static quality gates:** Run/verify lint and type checks for touched areas when configured by CI or project settings.
- [ ] **Documentation parity:** Update README/design notes for externally relied-on behavior (inputs, defaults, validation, errors).
- [ ] **Review completeness:** Resolve all review threads and obtain explicit approval from owners of touched surfaces.
- [ ] **Contract fidelity:** PR contract language must match implemented behavior exactly (authority rules, validation, error semantics).
- [ ] **Merge hygiene:** Use the team-agreed merge strategy; after merge, delete the remote branch and verify default branch build health.
