# This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This repository uses `PLANS.md` as the primary execution contract for major work. Any agent implementing this plan must keep this file synchronized with actual code, tests, validation evidence, and design decisions so the work can resume from this file alone.

## Purpose / Big Picture

After this change, `gws-cv-mail-harness` will no longer be a generic local Gmail-to-Sheet demo. It will become a local-first replacement for the existing HR Google Apps Script system that processes 104 resume emails for a single job opening, writes business-facing results into Google Sheets, creates interview invitation drafts, and sends both an HR business digest and an agent execution digest. A human should be able to run the local workflow from the repository, inspect the resulting Sheet, review created Gmail drafts, read the daily summary mail, and safely rerun the same workflow without duplicate processing or silent partial state.

The coding-agent goal is equally important: Codex must be able to read this file, inspect the repository, choose the next bounded milestone, implement it, test it, record what changed, and continue without asking for next steps unless a human gate is reached. This plan therefore defines both the product behavior and the autonomous implementation loop.

## Progress

- [x] (2026-04-17 11:20+08:00) Bootstrapped the repository scaffold and pushed the initial commit.
- [x] (2026-04-17 11:35+08:00) Added root execution guidance in `AGENTS.md`, plus first-pass contracts and helper scripts.
- [x] (2026-04-17 14:57+08:00) Implemented the first generic local loop: typed `gws` wrappers, SQLite state, CLI entrypoints, and initial tests.
- [x] (2026-04-17 16:00+08:00) Completed first live smoke validation for the generic harness path and fixed the Gmail API idempotency bug.
- [x] (2026-04-18 10:00+08:00) Reconstructed the legacy HR Apps Script system as the canonical product reference, including `履歷清單` lifecycle, `CONFIG` keys, `PROMPTS` keys, invitation draft behavior, and digest/report flow.
- [x] (2026-04-18 23:50+08:00) Reframed the repository goal: v1 is now the complete HR workflow replacement for one job profile, not a generic Gmail harness.
- [ ] Replace the generic harness-oriented contracts with HR workflow contracts that define repo-native configuration, resume message classes, anomaly policy, business-facing Sheet projection, dual digest behavior, and checkpoint/resume semantics.
- [ ] Implement repo-native operator configuration and prompt assets so Google Sheet is no longer the settings source of truth.
- [ ] Implement HR resume ingestion rules, including three 104 email classes, one-candidate-per-message validation, anomaly logging, and durable raw artifact capture.
- [ ] Implement the full processing chain: HTML to Markdown, contact extraction, CV review, invitation draft creation, Sheet projection, and dual digest generation.
- [ ] Implement checkpoint/resume and partial-failure handling for local runtime limits such as token exhaustion, API errors, and interrupted runs.
- [ ] Validate the complete HR workflow end to end against a constrained live profile with repeatable tests and live evidence.

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

## Outcomes & Retrospective

- Current outcome: The repository already proves the minimum local loop of Gmail search, Gmail read, Sheet append, digest send, SQLite state, and rerun safety.
- Current gap: The repository does not yet implement the HR-specific workflow that justified the migration in the first place. It lacks repo-native profile configuration, raw artifact persistence, HTML-to-Markdown conversion, contact extraction, CV review, invitation draft policy, business-facing Sheet projection, dual digests, and checkpoint/resume.
- Lesson so far: A generic harness was a useful proof of feasibility, but it is now a liability if the plan continues to optimize for genericity instead of the actual recruiting workflow.

## Context and Orientation

This repository contains a local-first replacement for a Google Apps Script recruiting tool. The old system lived inside a Google Sheet and Apps Script project and used Gmail, Google Drive, Gemini, and Sheet tabs named `履歷清單`, `CONFIG`, and `PROMPTS`. The old system processed inbound 104 recruiting emails for HR. It searched Gmail for specific subject patterns and labels, assumed one candidate per email, stored original email content as HTML in Drive, converted that HTML into Markdown, extracted contact details and a 104 candidate code, compared the candidate against a job description and benchmark CV, created interview invitation drafts for strong candidates, and sent a daily summary to HR and related managers.

In this repository, `apps/` contains runnable entrypoints such as the CLI, `packages/` contains reusable code, `docs/contracts/` contains stable behavior definitions, `tests/` contains validation, and `runtime/` contains local state and artifacts. `runtime/` is not the main source of truth. The primary source of truth for implementation direction is this file plus the contracts it points to.

The current generic implementation path is spread across `packages/google_workspace/`, `packages/state_store/`, `packages/runner/`, `apps/cli/`, `runtime/config.local.yaml`, and the existing contract docs in `docs/contracts/`. Those contracts are now too generic for the product goal and must be replaced or expanded.

The phrase “job profile” in this plan means the complete configuration for one recruiting stream: Gmail query rules, prompt assets, business projection rules, invitation draft templates, digest recipients, and validation thresholds for one job opening. v1 supports exactly one job profile at a time.

The phrase “anomaly” means an input or runtime condition that should not be silently processed as normal. Examples include an email that appears to contain more than one candidate, a resume email class that the parser cannot classify, an artifact conversion failure, or a run that stops halfway because the LLM provider or local agent budget was exhausted.

The phrase “checkpoint” means durable local state that records enough progress for the next run to continue safely without duplicating completed work or losing the reason for interruption.

## Plan of Work

### Milestone 1: Replace generic contracts with HR workflow contracts

This milestone changes the repository’s definition of “done.” At the end of it, a novice reader should be able to understand the actual product from repo files without reading the old Apps Script code. Add or replace contracts under `docs/contracts/` so they describe the HR product, not the generic harness. Introduce repository-relative files for at least the following concepts:

- one job profile configuration model
- prompt asset structure and loading rules
- resume email classes and classification rules
- anomaly policy and reporting rules
- business-facing Sheet projection rules
- dual digest format
- checkpoint/resume semantics

Update `README.md`, `ARCHITECTURE.md`, and this file only if needed to keep the repository orientation coherent. The expected proof for this milestone is document-level: the contracts should make it obvious what the system must do, which data belongs in repo files, which data belongs in runtime state, and what the user-visible outputs are.

### Milestone 2: Introduce repo-native profile configuration and prompt assets

Create repository-native configuration paths so the system no longer depends on Google Sheet for settings. The agent should be able to clone the repository, inspect a sample profile, and understand what needs to be customized for a real hiring stream. Use human-readable, diff-friendly files. Secrets must remain uncommitted.

This milestone should define and wire one active profile for the target job opening. That profile must include Gmail classification rules, prompt references, invitation draft templates, business digest recipients, and behavior toggles such as whether to create drafts. The CLI must be able to load this profile and validate it before any live processing starts.

### Milestone 3: Implement intake, classification, anomaly handling, and raw artifacts

Replace the generic “message in, row out” assumption with recruiting-specific intake logic. The runner must:

- search Gmail using the active profile
- classify each matching message into one of the supported 104 email classes
- validate that only one candidate is represented
- skip and record anomalies instead of guessing
- persist raw message artifacts and metadata needed for later steps

At the end of this milestone, a dry run should already be able to show which messages were accepted, which were skipped as anomalies, and what raw artifacts would be captured for downstream processing.

### Milestone 4: Implement HTML-to-Markdown, contact extraction, and CV review

Add the content-processing chain that made the old system resilient to layout variation. The plan is not to write brittle string slicing. The plan is to preserve the old design intent while making it testable and resumable locally. The processing chain must:

- convert resume HTML into stable Markdown
- extract contact details and candidate code from the Markdown
- evaluate the candidate against the profile’s job description and benchmark material
- preserve both intermediate artifacts and final review outputs in durable local artifacts

This milestone must produce observable artifacts and tests. A novice must be able to inspect the generated Markdown, extracted contact fields, and review result for a fixture before any live mail or Sheet projection is trusted.

### Milestone 5: Implement business projection, invitation drafts, and dual digests

Project the workflow into the surfaces real users care about. The Sheet should expose business-facing result fields for HR, hiring managers, and executives without overwhelming them with internal execution noise. Use the old `履歷清單` lifecycle as compatibility guidance, but keep the projected columns focused on business review rather than technical internals.

Add Gmail draft creation for invitation emails. v1 should create drafts only, not send them automatically. Record the draft result in a way that HR can inspect.

Add two daily digests:

- an HR business digest summarizing new candidates, recommendations, anomalies, and draft status
- an agent execution digest summarizing counts, checkpoints, failures, retries, and resume state

The business digest may go to HR and related managers. The execution digest may go to the operator list, but the implementation should allow both to be configured from the active profile.

### Milestone 6: Implement checkpoint/resume and local interruption handling

This milestone replaces the old cloud runtime guard with local recovery rules. The system must be able to stop safely and continue later when:

- the LLM provider returns errors
- local agent/model token budgets are exhausted
- Google APIs fail temporarily
- the operator stops the run
- only part of the candidate batch completed

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
    sed -n '1,260p' PLANS.md

Confirm the Google Workspace boundary before touching Gmail, Sheets, or drafts:

    ./scripts/preflight.sh

Expect the command to confirm a valid authenticated `gws` environment. If authentication, scopes, or the account identity are wrong, stop and record the blocker in `Progress`, `Surprises & Discoveries`, and `Decision Log`.

Before changing contracts, inspect the existing generic contract set:

    find docs/contracts -maxdepth 1 -type f | sort
    sed -n '1,220p' docs/contracts/config-model.md
    sed -n '1,220p' docs/contracts/digest-format.md
    sed -n '1,220p' docs/contracts/sheet-schema.md
    sed -n '1,220p' docs/contracts/state-store.md

Before implementing profile-aware behavior, refresh the legacy system facts if needed:

    clasp show-authorized-user
    clasp clone 1e0cZMYPKz2zwHNzvtQFkwSL97U-IlTXcPoSS0SHuY-5GjGmcouuOsgLN --rootDir /tmp/clasp-gws-cv-map
    sed -n '1,260p' /tmp/clasp-gws-cv-map/code.js

During development, keep the test loop narrow and frequent:

    uv sync
    uv run pytest tests/unit
    uv run pytest tests/integration

When adding live-profile behavior, keep a safe preview path:

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

Every milestone in this plan must be safe to repeat. If a command is run twice, it should not corrupt durable state or create duplicate business projection unless the command is explicitly designed to reproject from scratch.

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
