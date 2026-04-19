# This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This repository uses `PLANS.md` as the primary execution contract for major work. Any agent implementing this plan must keep this file synchronized with actual code, tests, validation evidence, and design decisions so the work can resume from this file alone. This file is intended to act as both external memory and a control plane for long-running work.

## Purpose / Big Picture

After this change, `gws-cv-mail-harness` will no longer be a generic local Gmail-to-Sheet demo. It will become a local-first replacement for the existing HR Google Apps Script system that processes 104 resume emails for a single job opening, writes business-facing results into Google Sheets, creates interview invitation drafts, and sends both an HR business digest and an agent execution digest. A human should be able to run the local workflow from the repository, inspect the resulting Sheet, review created Gmail drafts, read the daily summary mail, and safely rerun the same workflow without duplicate processing or silent partial state.

The coding-agent goal is equally important: Codex must be able to read this file, inspect the repository, choose the next bounded action, implement it, test it, record what changed, and continue without asking for next steps unless a human gate is reached. This plan therefore defines both the product behavior and the autonomous implementation loop.

## Current Active Action

Action ID: `A1`

Goal:

Replace the generic contract layer with an HR-specific contract set, and update the root orientation docs so a novice agent can understand the real product without reading the old Apps Script source first.

Why this action is active:

- The repository has already proved the generic local loop.
- The next major risk is not implementation mechanics; it is control-plane drift between the real HR workflow and the repo contracts.
- Until the contract layer is rewritten, future agents will keep planning against the wrong abstraction boundary.

Files to inspect before editing:

- `README.md`
- `ARCHITECTURE.md`
- `PLANS.md`
- `docs/contracts/config-model.md`
- `docs/contracts/digest-format.md`
- `docs/contracts/gmail-search.md`
- `docs/contracts/sheet-schema.md`
- `docs/contracts/state-store.md`

Files expected to change in this action:

- `README.md`
- `ARCHITECTURE.md`
- `docs/contracts/config-model.md`
- `docs/contracts/digest-format.md`
- `docs/contracts/sheet-schema.md`
- `docs/contracts/state-store.md`
- new HR-specific contract files under `docs/contracts/`

Commands to run:

    cd /Users/lee/ws/gws-cv-mail-harness
    find docs/contracts -maxdepth 1 -type f | sort
    sed -n '1,220p' README.md
    sed -n '1,220p' ARCHITECTURE.md
    sed -n '1,220p' docs/contracts/config-model.md
    sed -n '1,220p' docs/contracts/digest-format.md
    sed -n '1,220p' docs/contracts/sheet-schema.md
    sed -n '1,220p' docs/contracts/state-store.md

Expected evidence:

- A novice can identify the repository-native profile model, prompt asset model, anomaly policy, business-facing Sheet projection rules, dual digest rules, and checkpoint semantics by reading `docs/contracts/` plus the root docs.
- `README.md` and `ARCHITECTURE.md` no longer describe the repository as if the generic harness were still the main product.
- `PLANS.md` can point to the new contract files without requiring the next agent to reconstruct product meaning from live Apps Script.

Exit condition:

- The generic contract set is either replaced or explicitly subordinated to a new HR contract set.
- The root docs and `PLANS.md` all describe the same product boundary.
- The next action can proceed without first clarifying what the HR workflow is supposed to do.

Safe-stop note:

- This action is document-only. Stopping midway is safe as long as `PLANS.md` is updated to describe which contract files were changed and which remain generic.

## Action Queue

### Ready Actions

#### `A2` Repo-native profile and prompt assets

Goal:

Introduce a repository-native active profile and prompt asset layout so Google Sheet is no longer the settings source of truth.

Depends on:

- `A1`

Inspect:

- `docs/contracts/config-model.md`
- new HR contract files from `A1`
- `apps/cli/__main__.py`
- `runtime/config.local.example.yaml`
- `runtime/config.local.yaml`

Edit:

- `apps/cli/__main__.py`
- `runtime/config.local.example.yaml`
- new profile / prompt asset paths in the repository
- contracts that define profile loading

Evidence:

- A sample active profile exists in repo-native form.
- The CLI can validate the active profile before live processing.
- A future agent can identify which values are committed defaults versus local secrets.

Exit condition:

- The repository contains one active job profile shape and one prompt asset structure that map to the HR workflow.

#### `A3` Intake, classification, anomaly handling, and raw artifacts

Goal:

Replace the generic message-to-row assumption with HR-specific intake rules and durable anomaly handling.

Depends on:

- `A2`

Inspect:

- `packages/google_workspace/`
- `packages/runner/`
- `packages/state_store/`
- contracts produced by `A1` and `A2`

Edit:

- `packages/runner/`
- `packages/state_store/`
- any helper modules needed for classification and raw artifact capture
- tests for classification and anomaly handling

Evidence:

- A dry run can show accepted messages, anomaly messages, and raw artifact capture intentions.
- The one-candidate-per-message rule is explicit in both code and tests.

Exit condition:

- The runner no longer assumes every matched message should become a normal downstream candidate record.

#### `A4` HTML-to-Markdown, extraction, and candidate review

Goal:

Implement the content-processing chain that produces durable intermediate artifacts and review outputs for one candidate.

Depends on:

- `A3`

Evidence:

- Fixtures or tests show HTML input, Markdown output, extracted contact fields, and candidate review output.

#### `A5` Business projection, invitation drafts, and dual digests

Goal:

Project HR-facing outputs into Sheet, Gmail drafts, and two digest views.

Depends on:

- `A4`

Evidence:

- The repository can preview business projection, draft creation, and both digest types without irreversible actions.

#### `A6` Checkpoint/resume and interruption handling

Goal:

Extend durable state so partial progress and retry state are first-class.

Depends on:

- `A3`
- `A4`
- `A5`

Evidence:

- State can distinguish completed, partial, anomaly, and retry-ready candidate states.

#### `A7` End-to-end validation

Goal:

Validate the full HR workflow for one constrained live profile.

Depends on:

- `A1`
- `A2`
- `A3`
- `A4`
- `A5`
- `A6`

Evidence:

- Unit, integration, and guided live validation all exist and are recorded in `PLANS.md`.

### Blocked Or Deferred Actions

- Multi-profile support is deferred until the single-profile HR replacement path is stable.
- Multi-provider abstraction is deferred until one provider path proves the end-to-end HR workflow.
- Any local web UI beyond CLI and business-facing Sheet is deferred unless the contracts or validation show it is necessary.

## Action Selection Rules

Choose the next action using these rules:

1. If `Current Active Action` is incomplete and unblocked, continue it.
2. If the active action completes, choose the first ready action whose dependencies are all complete.
3. If a blocked action becomes unblocked because a dependency completed, move it into `Ready Actions` and make it active only if it is the earliest eligible action.
4. If implementation reveals that the current action is too large, split it into smaller action IDs in this file before continuing.
5. If the repository and this plan drift apart, repair the plan first unless the drift is trivial and can be fixed in the same bounded edit.

## Progress

- [x] (2026-04-17 11:20+08:00) Bootstrapped the repository scaffold and pushed the initial commit.
- [x] (2026-04-17 11:35+08:00) Added root execution guidance in `AGENTS.md`, plus first-pass contracts and helper scripts.
- [x] (2026-04-17 14:57+08:00) Implemented the first generic local loop: typed `gws` wrappers, SQLite state, CLI entrypoints, and initial tests.
- [x] (2026-04-17 16:00+08:00) Completed first live smoke validation for the generic harness path and fixed the Gmail API idempotency bug.
- [x] (2026-04-18 10:00+08:00) Reconstructed the legacy HR Apps Script system as the canonical product reference, including `履歷清單` lifecycle, `CONFIG` keys, `PROMPTS` keys, invitation draft behavior, and digest/report flow.
- [x] (2026-04-18 23:50+08:00) Reframed the repository goal: v1 is now the complete HR workflow replacement for one job profile, not a generic Gmail harness.
- [x] (2026-04-19 08:00+08:00) Reviewed the repository against the OpenAI ExecPlan article and identified four control-plane gaps: insufficient self-containment, lack of an action queue, insufficient file-level executable specification, and missing plan-authoring rules in `AGENTS.md`.
- [x] (2026-04-19 08:35+08:00) Rewrote `AGENTS.md` and `PLANS.md` so the root control plane now explicitly covers ExecPlan authoring, implementation, revision, active action selection, action queueing, and safe resumption.
- [ ] `A1` Replace the generic contract layer with an HR-specific contract set and align root orientation docs with the real product.
- [ ] `A2` Introduce repo-native profile and prompt asset structure.
- [ ] `A3` Implement intake, classification, anomaly handling, and raw artifact capture.
- [ ] `A4` Implement HTML-to-Markdown, extraction, and candidate review.
- [ ] `A5` Implement business projection, invitation drafts, and dual digests.
- [ ] `A6` Implement checkpoint/resume and interruption handling.
- [ ] `A7` Validate the complete HR workflow end to end against a constrained live profile.

## Surprises & Discoveries

- Observation: The initial scaffold alone was not sufficient to make a future agent autonomous.
  Evidence: Before the first implementation pass, the repository had structure but not enough execution rules, human gates, or durable decision records.

- Observation: `gws gmail +read --format json` can return address-shaped fields as either objects or lists.
  Evidence: The first real dry run failed on a list-shaped `from` field until the parser normalized both shapes.

- Observation: Live reruns duplicated work when state used the RFC `Message-ID` header instead of the Gmail API message id.
  Evidence: The first live rerun exposed a mismatch between `gws gmail +read` payloads and Gmail search identities; updating idempotency to use Gmail API ids fixed the drift.

- Observation: The legacy Apps Script system is much more domain-specific than the first local harness.
  Evidence: The live `code.js` depends on HR-specific Gmail queries, `履歷清單`, Drive-stored HTML and Markdown artifacts, Gemini-powered extraction and scoring, interview invitation drafts, and a business digest for HR and managers.

- Observation: The old cloud-runtime safety valve (`MAX_EXECUTION_TIME_MINUTES`) does not map directly to local execution.
  Evidence: The real local risk is not hard platform shutdown but partial completion due to token ceilings, model failures, local interruptions, or operator-aborted runs.

- Observation: The result Sheet serves executives and hiring managers, not just implementers.
  Evidence: The user explicitly clarified that Google Sheet should remain a business-facing review surface for HR, department heads, and the CEO, and should not expose too much internal evaluation-process noise.

- Observation: The repository had already adopted the language of a living plan, but not yet the stronger control-plane structure needed for low-context resumption.
  Evidence: The 2026-04-19 review found that the old `PLANS.md` still behaved like a roadmap rather than a resumable action system.

## Decision Log

- Decision: v1 targets complete replacement of the old HR Google Apps Script workflow for one job profile.
  Rationale: The user explicitly prioritized functional parity with the business workflow over preserving a generic harness abstraction.
  Date/Author: 2026-04-18 / Codex

- Decision: Repository-native configuration replaces the legacy `CONFIG` and `PROMPTS` Google Sheets.
  Rationale: The new system should follow an agent-friendly repository design where repo files are the primary source of truth and Google Sheet is a projection target rather than a control plane.
  Date/Author: 2026-04-18 / Codex

- Decision: Google Sheet remains in the product, but only as a business-facing results surface.
  Rationale: HR, hiring managers, and the CEO need to inspect candidate results, while low-level execution metadata should remain in local state, logs, and digests instead of cluttering the Sheet.
  Date/Author: 2026-04-18 / Codex

- Decision: The first implementation path remains single-profile and provider-agnostic in concept, but provider abstraction is deferred.
  Rationale: Multi-profile and multi-provider flexibility are real future needs, but the first risk to retire is whether the complete HR workflow can be rebuilt in a local repo with autonomous agent execution.
  Date/Author: 2026-04-18 / Codex

- Decision: Messages that appear to contain multiple different candidates are anomalies and must be skipped.
  Rationale: The user wants deterministic handling for this class of ambiguity: do not partially process such emails, do not attempt splitting, and surface them in the daily summary.
  Date/Author: 2026-04-18 / Codex

- Decision: Invitation emails remain draft-first in v1.
  Rationale: Trust in the agent is not yet high enough for autonomous outbound mail. The system should prepare Gmail drafts and make that result observable to HR rather than sending automatically.
  Date/Author: 2026-04-18 / Codex

- Decision: Daily output must include two distinct summary views.
  Rationale: The business audience needs a candidate/recruiting summary, while the operator and agent need an execution summary with anomalies, skips, and recovery state.
  Date/Author: 2026-04-18 / Codex

- Decision: Local recovery is based on checkpoints and resumable state, not a local clone of `MAX_EXECUTION_TIME_MINUTES`.
  Rationale: Local execution should safely stop and resume when tokens, APIs, or the operator interrupt work, rather than simulating Apps Script’s runtime budget directly.
  Date/Author: 2026-04-18 / Codex

- Decision: Before implementing more HR-specific code, the repository should first be upgraded so `AGENTS.md` and `PLANS.md` act as a stronger external memory and control plane.
  Rationale: The 2026-04-19 review concluded that future implementation work would otherwise continue to rely too heavily on hidden agent reasoning and repo-context reconstruction.
  Date/Author: 2026-04-19 / Codex

## Outcomes & Retrospective

- Current outcome: The repository already proves the minimum local loop of Gmail search, Gmail read, Sheet append, digest send, SQLite state, and rerun safety.
- Current outcome: The root control plane now more explicitly separates authoring rules, implementation rules, revision rules, and queued actions for future agents.
- Current gap: The repository still does not implement the HR-specific workflow that justified the migration in the first place. It lacks repo-native profile configuration, raw artifact persistence, HTML-to-Markdown conversion, contact extraction, CV review, invitation draft policy, business-facing Sheet projection, dual digests, and checkpoint/resume.
- Lesson so far: A generic harness was a useful proof of feasibility, but it became a liability once the real product boundary was clearer. The repository now needs contract-layer clarity before more code.

## Context and Orientation

This repository contains a local-first replacement for a Google Apps Script recruiting tool. The old system lived inside a Google Sheet and Apps Script project and used Gmail, Google Drive, Gemini, and Sheet tabs named `履歷清單`, `CONFIG`, and `PROMPTS`. The old system processed inbound 104 recruiting emails for HR. It searched Gmail for specific subject patterns and labels, assumed one candidate per email, stored original email content as HTML in Drive, converted that HTML into Markdown, extracted contact details and a 104 candidate code, compared the candidate against a job description and benchmark CV, created interview invitation drafts for strong candidates, and sent a daily summary to HR and related managers.

In this repository, `apps/` contains runnable entrypoints such as the CLI, `packages/` contains reusable code, `docs/contracts/` contains stable behavior definitions, `tests/` contains validation, and `runtime/` contains local state and artifacts. `runtime/` is not the main source of truth. The primary source of truth for implementation direction is this file plus the contracts it points to.

The current generic implementation path is spread across `packages/google_workspace/`, `packages/state_store/`, `packages/runner/`, `apps/cli/`, `runtime/config.local.yaml`, and the existing contract docs in `docs/contracts/`. Those contracts are now too generic for the product goal and must be replaced or expanded.

The phrase “job profile” in this plan means the complete configuration for one recruiting stream: Gmail query rules, prompt assets, business projection rules, invitation draft templates, digest recipients, and validation thresholds for one job opening. v1 supports exactly one job profile at a time.

The phrase “anomaly” means an input or runtime condition that should not be silently processed as normal. Examples include an email that appears to contain more than one candidate, a resume email class that the parser cannot classify, an artifact conversion failure, or a run that stops halfway because the LLM provider or local agent budget was exhausted.

The phrase “checkpoint” means durable local state that records enough progress for the next run to continue safely without duplicating completed work or losing the reason for interruption.

The canonical legacy facts required for the next implementation stages are already known and should be treated as part of this plan, not as hidden context:

- legacy Sheet tabs: `履歷清單`, `CONFIG`, `PROMPTS`
- legacy property family: processed ids, Drive destination id, LLM provider key, digest recipients, storage bucket id
- supported message classes: 104 matching recommendation, 104 self-recommendation, 104 manual forward
- anomaly policy: messages that appear to contain more than one candidate are skipped and reported
- invitation policy: invitation emails remain draft-first
- digest policy: the local system must support both a business summary and an execution summary

Refreshing the live Apps Script source can still be useful, but it is a refresh path, not the primary way a future agent should learn these facts.

## Plan of Work

### Milestone 1: Replace generic contracts with HR workflow contracts

This milestone changes the repository’s definition of “done.” At the end of it, a novice reader should be able to understand the actual product from repo files without reading the old Apps Script code. Add or replace contracts under `docs/contracts/` so they describe the HR product, not the generic harness.

The minimum contract set at the end of this milestone should make the following concepts explicit:

- repository-native job profile configuration
- prompt asset structure and loading rules
- resume email classes and classification rules
- anomaly policy and reporting rules
- business-facing Sheet projection rules
- dual digest format
- checkpoint/resume semantics

The expected file-level shape is:

- add a contract that defines the job profile model
- add a contract that defines supported resume message classes and how they are recognized
- add a contract that defines anomaly recording and reporting semantics
- replace or rewrite `docs/contracts/config-model.md` so it describes repo-native profile configuration rather than generic YAML alone
- replace or rewrite `docs/contracts/digest-format.md` so it distinguishes the HR business digest from the execution digest
- replace or rewrite `docs/contracts/sheet-schema.md` so it describes the business-facing projection instead of a generic append payload
- replace or rewrite `docs/contracts/state-store.md` so it names candidate state, anomaly state, digest state, and checkpoint state
- update `README.md` and `ARCHITECTURE.md` only as needed to keep the repository orientation coherent

The expected proof for this milestone is document-level but concrete: a novice should be able to identify which data belongs in repo files, which data belongs in runtime state, what the business-facing outputs are, and what the next implementation step must preserve.

### Milestone 2: Introduce repo-native profile configuration and prompt assets

Create repository-native configuration paths so the system no longer depends on Google Sheet for settings. The agent should be able to clone the repository, inspect a sample profile, and understand what needs to be customized for a real hiring stream. Use human-readable, diff-friendly files. Secrets must remain uncommitted.

This milestone should define and wire one active profile for the target job opening. That profile must include Gmail classification rules, prompt references, invitation draft templates, business digest recipients, and behavior toggles such as whether to create drafts. The CLI must be able to load this profile and validate it before any live processing starts.

### Milestone 3: Implement intake, classification, anomaly handling, and raw artifacts

Replace the generic “message in, row out” assumption with recruiting-specific intake logic. The runner must search Gmail using the active profile, classify each matching message into one of the supported 104 email classes, validate that only one candidate is represented, skip and record anomalies instead of guessing, and persist raw message artifacts and metadata needed for later steps.

At the end of this milestone, a dry run should already be able to show which messages were accepted, which were skipped as anomalies, and what raw artifacts would be captured for downstream processing.

### Milestone 4: Implement HTML-to-Markdown, contact extraction, and CV review

Add the content-processing chain that made the old system resilient to layout variation. The plan is not to write brittle string slicing. The plan is to preserve the old design intent while making it testable and resumable locally. The processing chain must convert resume HTML into stable Markdown, extract contact details and candidate code from the Markdown, evaluate the candidate against the profile’s job description and benchmark material, and preserve both intermediate artifacts and final review outputs in durable local artifacts.

This milestone must produce observable artifacts and tests. A novice must be able to inspect the generated Markdown, extracted contact fields, and review result for a fixture before any live mail or Sheet projection is trusted.

### Milestone 5: Implement business projection, invitation drafts, and dual digests

Project the workflow into the surfaces real users care about. The Sheet should expose business-facing result fields for HR, hiring managers, and executives without overwhelming them with internal execution noise. Use the old `履歷清單` lifecycle as compatibility guidance, but keep the projected columns focused on business review rather than technical internals.

Add Gmail draft creation for invitation emails. v1 should create drafts only, not send them automatically. Record the draft result in a way that HR can inspect.

Add two daily digests:

- an HR business digest summarizing new candidates, recommendations, anomalies, and draft status
- an agent execution digest summarizing counts, checkpoints, failures, retries, and resume state

The business digest may go to HR and related managers. The execution digest may go to the operator list, but the implementation should allow both to be configured from the active profile.

### Milestone 6: Implement checkpoint/resume and local interruption handling

This milestone replaces the old cloud runtime guard with local recovery rules. The system must be able to stop safely and continue later when the LLM provider returns errors, local agent or model token budgets are exhausted, Google APIs fail temporarily, the operator stops the run, or only part of the candidate batch completed.

The state model must make the stop reason visible and allow a future run to continue from the next safe boundary. Safe boundary means a point where no already-projected candidate is projected again and no half-written business output is mistaken for success.

### Milestone 7: End-to-end validation of the complete HR workflow

After the prior milestones, validate the workflow with a constrained live profile. The acceptance target is not “the code compiles.” The acceptance target is that the local repository can replace the old HR Apps Script workflow for one job profile with observable behavior, safe reruns, readable artifacts, and human-reviewable outputs.

This milestone must leave behind:

- passing unit tests
- passing integration tests for profile loading, classification, anomaly handling, and recovery state
- at least one guided live validation path
- updated contracts and progress notes

## Concrete Steps

Run all commands from the repository root:

    cd /Users/lee/ws/gws-cv-mail-harness

Before implementation or live validation, inspect the repository control plane:

    sed -n '1,220p' AGENTS.md
    sed -n '1,260p' README.md
    sed -n '1,260p' ARCHITECTURE.md
    sed -n '1,320p' PLANS.md

For `A1`, inspect the current generic contract set before editing:

    find docs/contracts -maxdepth 1 -type f | sort
    sed -n '1,220p' docs/contracts/config-model.md
    sed -n '1,220p' docs/contracts/digest-format.md
    sed -n '1,220p' docs/contracts/sheet-schema.md
    sed -n '1,220p' docs/contracts/state-store.md

When `A1` is complete, the next agent should be able to identify the HR product contract without cloning the old Apps Script. Refreshing legacy source is optional and only for verification:

    clasp show-authorized-user
    clasp clone 1e0cZMYPKz2zwHNzvtQFkwSL97U-IlTXcPoSS0SHuY-5GjGmcouuOsgLN --rootDir /tmp/clasp-gws-cv-map
    sed -n '1,260p' /tmp/clasp-gws-cv-map/code.js

During development, keep the validation loop narrow and frequent:

    uv sync
    uv run pytest tests/unit
    uv run pytest tests/integration

When adding live-profile behavior, keep a safe preview path:

    ./scripts/preflight.sh
    uv run python -m apps.cli preflight --config runtime/config.local.yaml
    uv run python -m apps.cli run-once --config runtime/config.local.yaml --dry-run

The dry run must show accepted candidates, anomalies, intended Sheet projection, intended draft creation, and intended digest outputs without performing irreversible actions.

Only after the relevant human gate is cleared, run the live path:

    ./scripts/run-smoke.sh

As this plan evolves, replace or expand the exact commands above so they reflect the actual profile-aware CLI surface instead of placeholder behavior.

## Validation and Acceptance

The work is accepted only when a human can verify all of the following for one real job profile:

1. The repository contains a repo-native job profile and prompt asset set that fully replaces legacy `CONFIG` and `PROMPTS` sheets as the operational source of truth.
2. Running the dry-run workflow classifies the three supported 104 email classes correctly and visibly flags anomalies such as multi-candidate emails.
3. The workflow captures raw message artifacts and produces Markdown and structured extraction outputs that can be inspected locally.
4. The workflow generates a candidate review result tied to the configured job description and benchmark material.
5. The workflow projects business-facing results into Google Sheet without exposing excessive internal evaluation noise.
6. The workflow creates invitation drafts for qualified candidates but does not auto-send them.
7. The workflow sends or previews both the HR business digest and the agent execution digest.
8. Rerunning the same workflow does not duplicate already-processed candidates in the Sheet or lose anomaly visibility.
9. If the run is interrupted midway, the next run resumes safely from checkpointed state instead of silently starting over or corrupting output.

Tests must prove the building blocks, not just the happy path. At minimum, this repository should end up with automated tests for:

- profile loading and validation
- email class classification
- one-candidate-per-message validation
- anomaly recording
- HTML-to-Markdown transformation handling
- contact extraction parsing
- review pipeline orchestration
- invitation draft gating
- business Sheet projection shape
- checkpoint/resume semantics

## Human Validation Gates

The agent may proceed autonomously until one of these gates is reached:

1. the first live Google Drive artifact write for the HR workflow
2. the first live Google Sheet write that targets the business-facing projection instead of the old generic test tab
3. the first live Gmail draft creation for real candidate invitations
4. the first live daily digest sent to real HR or manager recipients
5. a contract ambiguity where multiple product behaviors are plausible and the repository files do not resolve the choice
6. an authentication, permission, provider, or environment failure that the repository cannot self-correct safely

At every gate, the agent must record exactly what is ready, what evidence exists, what would happen next, and the safest resumption point after human approval.

## Idempotence and Recovery

Every action and milestone in this plan must be safe to repeat. If a command is run twice, it should not corrupt durable state or create duplicate business projection unless the command is explicitly designed to reproject from scratch.

Processed-candidate state must be durable and consultable before projecting business outputs. Anomalies must also be durable. A future run must be able to distinguish among:

- not yet seen
- accepted and fully processed
- accepted but partially processed
- skipped as anomaly
- failed and ready to retry

When local execution stops due to token ceilings, LLM failures, API rate limits, operator interruption, or unexpected exceptions, the run must persist enough information for the next run to continue safely. The recovery model must prefer safe stop-and-resume over partial hidden progress.

If a milestone introduces a destructive or hard-to-reverse operation, add a safe preview mode before enabling the live path. This is especially important for Google Sheet writes, Gmail drafts, and multi-recipient digests.

## Artifacts and Notes

Important current files:

    AGENTS.md
    README.md
    ARCHITECTURE.md
    PLANS.md
    docs/contracts/config-model.md
    docs/contracts/digest-format.md
    docs/contracts/gmail-search.md
    docs/contracts/sheet-schema.md
    docs/contracts/state-store.md
    docs/workflows/live-smoke-validation.md
    apps/cli/__main__.py
    packages/google_workspace/
    packages/runner/
    packages/state_store/
    tests/
    runtime/

Important legacy reference facts:

    legacy Sheet tabs: 履歷清單, CONFIG, PROMPTS
    legacy properties: processedIds, folderId, geminiApiKey, cvReportReceiversEmail, gcpBucketId
    supported message classes: 104 matching recommendation, 104 self-recommendation, 104 manual forward
    anomaly rule: multi-candidate messages are skipped and reported
    output rule: invitation remains draft-first
    digest rule: both business summary and execution summary are required in the new system

Change note: 2026-04-18 / Rewrote this plan from a generic harness implementation path into an HR workflow replacement ExecPlan. The reason for this revision is that the product goal was clarified: complete local replacement of the recruiting workflow for one job profile, with repo-native configuration and an autonomous agent coding loop.

Change note: 2026-04-19 / Reworked the root control plane after an ExecPlan architecture review. The reason for this revision is that the previous plan behaved more like a roadmap than a resumable external memory plus action system, so this file now explicitly records the active action, queued actions, action-selection rules, and the canonical legacy facts needed for the next implementation stages.

## Interfaces and Dependencies

The implementation should continue to use the existing repository boundaries rather than inventing new ones casually.

`packages/google_workspace/` remains the only module family allowed to call `gws`. Extend it to support the Gmail, Drive, and Sheet operations needed by the HR workflow. If the current wrappers are too generic or too narrow, evolve them there rather than bypassing the boundary.

`packages/state_store/` remains the home of durable run, candidate, anomaly, digest, and checkpoint state. Expand the schema rather than introducing hidden state elsewhere.

`packages/runner/` should become the workflow orchestrator for the HR pipeline. It should own the ordered execution of intake, classification, anomaly handling, artifact capture, conversion, extraction, review, projection, draft creation, digesting, and checkpoint management.

The repository should end this plan with explicit interfaces equivalent to the following responsibilities, even if the exact Python names vary:

    load_active_profile(profile_path: str) -> JobProfile
    classify_resume_message(message: MessagePacket, profile: JobProfile) -> MessageClassification
    validate_single_candidate(message: MessagePacket, classification: MessageClassification) -> CandidateValidationResult
    capture_raw_artifacts(message: MessagePacket, profile: JobProfile) -> RawArtifactSet
    convert_html_to_markdown(raw_html: str, prompt_asset: PromptAsset) -> MarkdownArtifact
    extract_contact_info(markdown: str, prompt_asset: PromptAsset) -> ContactInfo
    review_candidate(markdown: str, profile: JobProfile) -> CandidateReview
    project_candidate_to_sheet(review: CandidateReview, sheet_target: SheetTarget) -> SheetWriteResult
    create_invitation_draft(candidate: CandidateReview, profile: JobProfile) -> DraftResult
    build_business_digest(summary: BusinessSummary, recipients: list[str]) -> DigestMessage
    build_execution_digest(run: ExecutionSummary, recipients: list[str]) -> DigestMessage
    record_checkpoint(run_id: str, state: CheckpointState) -> None
    resume_from_checkpoint(run_id: str) -> ResumeState

Use one provider path first. If the repository still uses Gemini for legacy parity or switches to another provider for the local implementation, record that decision here and in the relevant contract docs. The key rule is that provider choice must not displace the higher-priority work of building a resumable, observable, agent-operable HR workflow.
