# Persona B checkpoint — Affinity Atlas 0.2

**Date:** 2026-10-09. **OWNER:** Persona B. **REVIEWER:** Persona A only after Apertus handoff. This work does not modify Apertus main.

## Goal and decision

Produce a Qloo-essential, curator-facing tool, rather than a generic movie/music recommendation app. Continue Cultural Programming Agent as a **provisional product** based on direct, successful Qloo API evidence. Do not reopen the broader ideation audit without evidence that disproves the product premise.

## Direct evidence (higher priority than older plans)

On Persona B's Ubuntu machine, MVP 0.1:
- Qloo `GET /search`: Nils Frahm resolves as artist (HTTP 200).
- Qloo `GET /v2/insights`: 5 movies, 5 brands, 5 Madrid places from the same canonical artist ID (HTTP 200 each, no warnings).
- Qloo explainability: Qloo input artist was traced for Círculo de Bellas Artes and Goethe-Institut Madrid. `score: 1` should not be presented as predicted event success/compatibility.
- Browser at `127.0.0.1:8765`: end-to-end generation of three proposals and a local evidence ledger.
- MVP 0.2: offline goal-aware planner, reviewer tests; **live 0.2 execution still needs a user-run smoke**.

## Source priority and constraints

1. Current terminal/API/deployment evidence from Persona B.
2. Qloo 2026 rules: https://qloo.devpost.com/rules ; schedule: https://qloo.devpost.com/details/dates ; overview https://qloo.devpost.com/.
3. Official Qloo API docs: https://github.com/qloo/docs-public , specifically `/search`, `/v2/insights`, `feature.explainability`.
4. User migration master: `00_PROMPT_MAESTRO_MIGRACION_AUTO_SUSCRIPCION.md`, cut 2026-10-07; historical prep plan superseded by working live prototype.
5. Rule snapshot `04_REGLAS_2026_VERIFICADAS.md`; Apertus audit is **out of scope for B's Qloo implementation**.

## Real current limitations

- Client-side demo requests still depend on a private Qloo key locally; public hosting needs safe server-side secret + abuse controls.
- Goal routing is deterministic/keyword-based, **not yet a true LLM agent**. No autonomous prompt/tool selection.
- Venue screening is an illustrative policy, not accessibility, licensing, suitability or costs research.
- No published repo, public demo, Devpost description or submission evidenced.

## Done for checkpoint B-02

- [x] Existing 0.1 preserved in published ZIP artifact and user's working folder.
- [x] Goal text changes selection of initial proposition.
- [x] Rejection reasons and an auditable goal policy shown in UI.
- [x] No unsupported compatibility percentage, sponsorship, cost or venue claims.
- [x] Local isolated offline test suite passes.
- [ ] End-to-end *0.2* live call run by Persona B and compared for at least two distinct objectives.
- [ ] Access key rotated before publication.

## Next action (one checkpoint at a time)

**Persona B:** download 0.2 ZIP, stop old 0.1 process with Ctrl+C, back up existing project, extract 0.2, run tests, restart UI, then compare two goal presets. Verify that the top concept changes and the decision audit shows the cause. Do not re-run unrelated hackathon tasks.

**Abort / rollback:** If 0.2 tests fail or local results regress, keep 0.1 working and restore the backed-up version. No edits to Apertus.

**After Apertus submission:** Persona A can join Qloo and own backend / agent reasoning / deployment; Persona B continues product UX, user-facing QA, Devpost copy, evidence comparisons.

**Official deadline:** 2026-10-30, 23:45 EDT. **Internal target:** 2026-10-29 for public repo, demo and Devpost completion.


## 2026-10-09: Live educational comparison and v0.3 correction

Observed v0.2 live: Nils Frahm/Madrid cinema -> Cinema in Resonance first at Círculo de Bellas Artes; education -> Listening Lab first at Museo Nacional del Prado. Both used 5 movies, 5 brands and 5 places. Educational output repeated Phantom Thread and Museo del Prado across two final proposals.

V0.3: choose formats by user goal, then allocate distinct Qloo evidence/venues per proposal where possible and report reuse. Tests are offline; a live Qloo browser test on the user's PC remains mandatory. Model-based curator/critic and public-hosted demo remain future work.


## 2026-10-09: Live 0.3 PASS and v0.4 optional bounded AI

Live browser 0.3 returned 3 educational proposals from Qloo Nils Frahm/Madrid, using separate movie entities and all three institution/cultural-place candidates. Goal `education` was preserved, 17 local tests PASS and no unsupported sponsorships/venue claims were observed. Mark `QLOO_V0_3_LIVE_DIVERSITY = PASS`.

New 0.4: optional server-side OpenAI-compatible format chooser; strict model output schema + source-backed evidence allocation + rule-based fallback. No LLM is configured by default, so this is **not** yet evidence of live model reasoning. The next verification gate is (a) offline critic tests on B, (b) live Qloo v0.4 output on B, and then (c) one actual LLM execution with provider access + visible `bounded_llm` mode. Continue guarding credentials; rotate disclosed Qloo key before public hosting.


## Update 0.5 — 2026-10-09
- Blueprint de Render y guardas básicas para demo pública preparados.
- 32 tests locales PASS (no equivalen a despliegue externo validado).
- `PUBLIC_DEPLOYMENT` sigue PENDING hasta rotar Qloo, disponer de LLM remoto, Git público y ensayo real HTTPS.
