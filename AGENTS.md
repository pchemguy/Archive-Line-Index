# Agent instructions

## Specification-driven development

This project uses the SDD Manager plugin for specification-driven development. If not already in the context, load `PLUGIN.md` from installed location or from `.agents/plugins/sdd-manager/PLUGIN.md` and the coordinator skill entry it references. If neither source is available, report the missing plugin before dependent workflow work.

**Follow the applicable SDD Manager workflows, including human checkpoints, Git publication and integration, and the tracking policy below.**

## Initialization

Execute the [skill and plugin discovery protocol](SKILL_DISCOVERY_PROTOCOL.md).

## Windows shell

On **Windows execution hosts only**, follow [WINDOWS_SHELL_POLICY.md](.agents/plugins/sdd-manager/assets/WINDOWS_SHELL_POLICY.md): CMD syntax, unavailable PowerShell/pwsh, temporary files for script text and shell operations, and the documented tool probe/recovery. This repository policy is independent of the plugin.

## Browser development

When developing or testing browser-based applications or browser extensions, follow [BROWSER_DEV_POLICY.md](.agents/plugins/sdd-manager/assets/BROWSER_DEV_POLICY.md). Prioritize Chromium and include Firefox by default; project documents may specify other choices. Use dedicated, isolated environments.

## Environment diagnostics

When Playwright is selected, follow [Playwright environment guidance](.agents/plugins/sdd-manager/assets/playwright.md) before dependent setup and execution, and when provisioning or browser runtime blocks required checks.

When a Vite-served module worker fails to start, especially from a linked Windows checkout or with an HTML entry response, follow [Vite worker-loading diagnostics](.agents/plugins/sdd-manager/assets/vite-worker-loading.md). Diagnose the loading stage before applying a workaround; this guidance does not apply to every SQLite or worker failure.

## Workflow continuity

For continuation, read `docs/dev/HANDOFF.md` and use `sdd-manage`'s continuity subworkflow to reconstruct later work from current development records and Git. The handoff describes a checkpoint, not necessarily the branch tip. At startup, inspect unfinished workflow branches against their recorded parents and request the continuation branch unless already selected. Preserve the recovered scope, approvals and stopping boundary.

## Human checkpoints

Present each necessary development-document proposal and its selected artifacts with concise substantive analysis and pause for acceptance before dependent work. Model/API-design artifacts share the decomposition checkpoint; contract artifacts share specification, without additional documentation tasks or approval rounds. Honor the user's requested implementation range and stop when it is complete.

The user may explicitly preapprove future checkpoints at any time. Retain the scope and conditions of that decision, including after interruption; do not repeat a covered approval request. Preapproval does not waive QC, resolve blockers or expand the authorized implementation range.

## Commits and publication

Keep each task's verified result, required evidence and completion checkbox in the same commit. Push every owned commit and verify remote containment before further work or another commit, unless the user explicitly directs local-only or deferred publication.

Use SDD Manager's integration procedure at the authorized complete boundary.

## GitHub tracking

Enable and maintain GitHub tracking for documentation preparation and implementation **by default**. The user may disable tracking, select local-only work or choose another supported backend. Preserve an established choice through interruptions and access failures; copying this template does not reset it.

Follow `sdd-manage`'s preparation and phase-activation workflows for required tracking readiness and lifecycle updates. Reconcile uncertain effects before retrying and report unmet prerequisites before dependent work.

## Project guidance

Archive Line Index is a synchronous Python library for sequential archive payload
streaming and byte-line indexing. Read the [project brief](docs/dev/PROJECT.md)
for intended scope; its approval state and subsequent design decisions belong in
`docs/dev/DOCS_PREPARATION.md`. Do not infer accepted behavior from legacy code or
an unapproved proposal.

The supplied legacy repository is
<https://github.com/pchemguy/Archive-Line-Index-Legacy>. Its README,
`docs/architecture.md`, `docs/dev/SPEC.md` and linked specifications are inputs to
new design work. Adapt useful content to the current document owners rather than
copying legacy document structure or completion claims. Public APIs, internal
interfaces and implementation must follow the newly accepted design and SPEC.

### Locations and instruction discovery

`pyproject.toml` declares `src/archive_line_index` as the wheel package, `src` as
the import/type-check root and `tests` as the test root. These source/test paths
are planned and do not yet exist. Main design and preparation records belong in
`docs/dev/`; consult their current owners as they are created. Keep source, test
and documentation ownership distinct when designing physical layout.

Read applicable nested `AGENTS.md` files before working within their paths. Load
this root file explicitly when the host does not discover it. Conversation logs
under `docs/ai-logs/` are historical data, governed by their own `AGENTS.md`, and
are excluded from routine orientation and design authority.

### Python tooling

Use Python 3.11 or later. On Windows, retain the CMD policy above; on other hosts,
use the actual host shell. Commands below run from the repository root with the
selected Python interpreter. Do not install globally or create an environment
without checking the applicable environment constraints.

The build backend is `hatchling.build`. The runtime dependency is `py7zr`;
optional groups are `dev`, `lint`, `tools` and `test`. `dev` contains build,
Ruff, mypy, pytest/plugins and Flowmark; `test` additionally supplies
pytest-benchmark and coverage. Hatch and uv are optional tools, not runtime
requirements. An empty `[project.scripts]` defines no console command.

The following invocations match the declared tools and paths. They are intended
checks after source/tests and dependencies exist, not passing verification
results for the current scaffold:

| Purpose | Command | Configuration |
| --- | --- | --- |
| Lint | `python -m ruff check src tests` | E/F/I/B/UP/ANN; E501 and B008 ignored; per-file exceptions apply |
| Format check | `python -m ruff format --check src tests` | 88 columns, four spaces, double quotes |
| Type check | `python -m mypy` | Strict mode; configured files are `src` |
| Tests | `python -m pytest` | Configured test root `tests`, import root `src`, strict config/markers |
| Branch coverage | `python -m pytest --cov=archive_line_index --cov-report=term-missing` | Source and branch measurement configured in coverage settings |
| Distribution build | `python -m build` | Hatchling; wheel package `src/archive_line_index` |

Pytest markers are `integration`, `slow` and `windows`. Asyncio strict mode and a
60-second timeout are configured; install the selected pytest plugins and confirm
that its version supports the native `[tool.pytest]` TOML table before relying on
these settings. The presence of pytest-asyncio does not require a public async API.

Mypy requires typed definitions. Ruff does not currently select `D` rules, so its
configured Google docstring convention does not itself enforce docstring coverage.
Use professional module/API documentation and Google-style Python docstrings
under the documentation workflow.

Flowmark is configured for width 88, non-semantic wrapping, disabled smart quotes
and ellipses, cleanup enabled and preserved list spacing. Discover its installed
CLI before adding a formatter invocation; preserve Markdown structure and literal
code/data when applying formatting.

### Current verification limits

TOML parsing and configuration/path inspection are established. This scaffold has
no source/tests and declares no static or dynamic project version; the configured
README is supplied with the project-brief proposal. Resolve version metadata and
create the accepted package layout before installation/build verification. The
configured Python development tools are not installed in the inspected execution
interpreter, and no runtime, type, lint, test or distribution check has passed for
the new package. Update this evidence as checks become executable.
