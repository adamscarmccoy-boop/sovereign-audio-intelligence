# Operations and maintenance plan

**Updated:** November 12, 2026  
**Audience:** project maintainer and future collaborators

This document separates repository maintenance from tasks that require the actual music workstation. It describes what may be scheduled, what must remain manual, and what evidence each task should produce.

## Operating principles

1. **No false positives.** Every reported success must correspond to a completed check. Missing dependencies or inaccessible services are not "passes."
2. **Keep original records.** Use existing DuckDB, Lance, Parquet, JSON, model, and runtime registries. Do not silently create replacement databases or assume that similar-shaped vectors are interchangeable.
3. **Keep private work private.** Do not place model weights, unpublished tracks, machine-wide file manifests, secrets, or internal paths in a public CI log or artifact.
4. **Preserve evidence.** Track tool version, model hash, input/output identifiers, operation ID, elapsed time, and actual result wherever execution occurs.
5. **Separate read-only monitoring from audio changes.** Any mastering, file replacement, registry mutation, or deployment needs a deliberate approval and a rollback plan.

## What GitHub can and cannot do

GitHub Actions starts temporary workers for committed code and permitted workflows. It can check documentation, validate files, run small tests, collect logs, and report failures. A scheduled workflow is a useful **maintenance service**, not a persistent agent, music daemon, or Windows workstation.

A hosted GitHub runner does **not** automatically see workstation drives, DuckDB files, native extensions, named pipes, audio devices, or running ONNX sessions. A self-hosted runner would provide access to a designated machine, but that introduces security and operating risks and **has not been configured by this repository update**.

Scheduled jobs run on the repository's default branch. They may start later than the scheduled minute. They cannot guarantee continuous monitoring or an exact-time audio-processing operation.

## Proposed task schedule

| Frequency | Environment | Task | Evidence | Automatic changes? |
|---|---|---|---|---|
| On request, if re-enabled | GitHub-hosted runner | Validate public documentation links and referenced repository files | Action job outcome | No |
| Optional weekly | GitHub-hosted runner | Review committed documentation and data-file integrity, only if a future workflow is deliberately enabled | Action job outcome | No |
| Daily, if workstation is running | Local Windows Task Scheduler or controlled daemon | Check services, model-file availability, DB accessibility, and free storage | Local JSON receipt, no personal paths in public logs | No |
| Weekly, locally | Workstation | Check audio workflow inputs, model hash drift, extraction completeness, and recent failure receipts | Private audit report | No |
| On request | Workstation | Run one known music operation and Big Brain before/after inference with the **correct trained 64-D input** | Private typed receipt and measured audio delta | Only with explicit approval |
| On release | GitHub and approved local environment | Run real tests, review dependencies/licensing, review security and performance claims | Versioned release checklist | Approval required |

**Status as of November 12, 2026:** the GitHub Actions workflow was removed at the maintainer's request. No weekly GitHub job is scheduled in this repository. All time-based jobs in this table are recommendations only; no Windows scheduled task or daemon was installed by this documentation update.

## Local daemon responsibilities

A future workstation supervisor should perform narrowly scoped jobs:

- **Health:** verify the configured model paths, native runtimes, and database connections without writing to them.
- **Ingestion:** detect intentionally submitted audio, record source fingerprints, and prevent duplicate processing.
- **Processing:** resolve a registered operation and its precise input contract; reject ambiguous model mappings.
- **Review:** capture the pre-operation state, execution receipt, and post-operation state. No success verdict without the stored decision contract.
- **Audit:** retain ordered timestamps and segment-level measurements; summarize failures and incomplete work.
- **Recovery:** distinguish an offline service, missing weights, a malformed contract, and a failed mathematical operation; never treat an exception as approval.

Use OS-native task scheduling or an authorized local service for persistent functions. GitHub Actions may receive a **sanitized status summary** through a deliberate, authenticated, outbound push from the workstation, but this is **not configured**.

## Security boundaries for any future workstation connection

Do not expose a Windows named pipe, an unauthenticated DuckDB endpoint, or a general-purpose execution method to a public workflow. Prefer short-lived credentials and a limited function set. Keep tokens in repository secrets or approved local secret storage, avoid printing them, and disable write operations until access controls and auditing are tested.

If a self-hosted GitHub Actions runner is considered later, isolate it from sensitive music archives and production databases, control which branches and workflow authors can invoke it, and avoid accepting arbitrary public pull requests on a privileged runner.

## Definition of a successful model-evaluation task

The receipt must include a source identifier and time interval; the exact model and input preprocessing contract; native executor and operation parameters; before/after tensors; audio or data output; a comparison under a previously verified acceptance rule; and an explicit outcome of **approved**, **rejected**, **failed**, or **unverified**.

**Until those contracts are connected, the proper outcome is _unverified_—not a mastering pass.**

## Public/private project separation

- **Public:** design overview, safe example code, tests, anonymized non-sensitive benchmarks with reproducible methodology, release notes.
- **Private:** unpublished Kimi projects, checkpoints/weights pending licensing review, sample libraries, raw WAVs, complete workstation manifests, secrets, and internal execution logs.
- **Ableton integration:** separate adapters and supported project tooling; the engine remains broader than one DAW.

No persistent local scheduler, self-hosted runner, or remote workstation connection was installed as part of this documentation and repository-check update.
