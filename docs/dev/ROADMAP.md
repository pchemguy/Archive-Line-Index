# Archive Line Index roadmap

## Authority

This roadmap is the compact progress projection of [PLAN.md](PLAN.md). PLAN owns phase, milestone, task, dependency, order, verification, and completion definitions. Checkboxes record durable completion only; the append-only implementation journal and recovery state provide the execution evidence.

## Progress summary

| Boundary   | Complete | Total |
| ---------- | -------: | ----: |
| Phases     |        3 |     4 |
| Milestones |       10 |    11 |
| Tasks      |       34 |    35 |

## [x] [Phase 1: Plain stream and index MVP](PLAN.md#plain-stream-and-index-mvp)

- [x] [Milestone: plain stream foundation](plan/plain-stream-index-mvp.md#milestone-plain-stream-foundation)
    - [x] [Task: establish the package and test baseline](plan/plain-stream-index-mvp.md#task-establish-the-package-and-test-baseline)
    - [x] [Task: implement public errors](plan/plain-stream-index-mvp.md#task-implement-public-errors)
    - [x] [Task: implement source path normalization](plan/plain-stream-index-mvp.md#task-implement-source-path-normalization)
    - [x] [Task: implement format classification](plan/plain-stream-index-mvp.md#task-implement-format-classification)
    - [x] [Task: define the backend reader contract](plan/plain-stream-index-mvp.md#task-define-the-backend-reader-contract)
    - [x] [Task: implement the plain backend](plan/plain-stream-index-mvp.md#task-implement-the-plain-backend)
    - [x] [Task: implement backend dispatch for the MVP](plan/plain-stream-index-mvp.md#task-implement-backend-dispatch-for-the-mvp)
    - [x] [Task: implement the common content stream](plan/plain-stream-index-mvp.md#task-implement-the-common-content-stream)
- [x] [Milestone: line indexing and public MVP](plan/plain-stream-index-mvp.md#milestone-line-indexing-and-public-mvp)
    - [x] [Task: implement the offset representation](plan/plain-stream-index-mvp.md#task-implement-the-offset-representation)
    - [x] [Task: implement the byte-line scanner](plan/plain-stream-index-mvp.md#task-implement-the-byte-line-scanner)
    - [x] [Task: compose the MVP public API](plan/plain-stream-index-mvp.md#task-compose-the-mvp-public-api)

## [x] [Phase 2: Archive streams](PLAN.md#archive-streams)

- [x] [Milestone: ZIP streaming](plan/archive-streams.md#milestone-zip-streaming)
    - [x] [Task: establish shared archive test factories](plan/archive-streams.md#task-establish-shared-archive-test-factories)
    - [x] [Task: implement ZIP archive streaming](plan/archive-streams.md#task-implement-zip-archive-streaming)
    - [x] [Task: register and integrate ZIP](plan/archive-streams.md#task-register-and-integrate-zip)
- [x] [Milestone: TAR streaming](plan/archive-streams.md#milestone-tar-streaming)
    - [x] [Task: implement streaming TAR](plan/archive-streams.md#task-implement-streaming-tar)
    - [x] [Task: register and integrate TAR](plan/archive-streams.md#task-register-and-integrate-tar)
- [x] [Milestone: 7z streaming](plan/archive-streams.md#milestone-7z-streaming)
    - [x] [Task: implement the 7z queue protocol](plan/archive-streams.md#task-implement-the-7z-queue-protocol)
    - [x] [Task: implement the py7zr extraction destination](plan/archive-streams.md#task-implement-the-py7zr-extraction-destination)
    - [x] [Task: implement 7z inspection and public error translation](plan/archive-streams.md#task-implement-7z-inspection-and-public-error-translation)
    - [x] [Task: register and integrate 7z](plan/archive-streams.md#task-register-and-integrate-7z)
- [x] [Milestone: archive lifecycle certification](plan/archive-streams.md#milestone-archive-lifecycle-certification)
    - [x] [Task: complete resource-lifecycle integration tests](plan/archive-streams.md#task-complete-resource-lifecycle-integration-tests)

## [x] [Phase 3: Index persistence](PLAN.md#index-persistence)

- [x] [Milestone: persistence adapters](plan/index-persistence.md#milestone-persistence-adapters)
    - [x] [Task: finalize persistence-facing offset validation](plan/index-persistence.md#task-finalize-persistence-facing-offset-validation)
    - [x] [Task: implement SQLite writing](plan/index-persistence.md#task-implement-sqlite-writing)
    - [x] [Task: implement SQLite reading](plan/index-persistence.md#task-implement-sqlite-reading)
    - [x] [Task: implement raw writing](plan/index-persistence.md#task-implement-raw-writing)
    - [x] [Task: implement raw reading](plan/index-persistence.md#task-implement-raw-reading)
- [x] [Milestone: public persistence integration](plan/index-persistence.md#milestone-public-persistence-integration)
    - [x] [Task: expose persistence through the public API](plan/index-persistence.md#task-expose-persistence-through-the-public-api)
    - [x] [Task: verify cross-format persistence equivalence](plan/index-persistence.md#task-verify-cross-format-persistence-equivalence)

## [ ] [Phase 4: Package integration](PLAN.md#package-integration)

- [x] [Milestone: distribution surface](plan/package-integration.md#milestone-distribution-surface)
    - [x] [Task: finalize package exports](plan/package-integration.md#task-finalize-package-exports)
    - [x] [Task: finalize dependency and build metadata](plan/package-integration.md#task-finalize-dependency-and-build-metadata)
    - [x] [Task: write the user README](plan/package-integration.md#task-write-the-user-readme)
- [x] [Milestone: operational verification](plan/package-integration.md#milestone-operational-verification)
    - [x] [Task: complete large-input and backpressure verification](plan/package-integration.md#task-complete-large-input-and-backpressure-verification)
    - [x] [Task: complete cross-platform filesystem verification](plan/package-integration.md#task-complete-cross-platform-filesystem-verification)
    - [x] [Task: run installed-package end-to-end workflows](plan/package-integration.md#task-run-installed-package-end-to-end-workflows)
- [ ] [Milestone: documentation and acceptance](plan/package-integration.md#milestone-documentation-and-acceptance)
    - [ ] [Task: reconcile documentation and acceptance coverage](plan/package-integration.md#task-reconcile-documentation-and-acceptance-coverage)
