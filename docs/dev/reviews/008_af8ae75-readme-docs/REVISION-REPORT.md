# README and documentation revision report

## Opening checkpoint

Campaign 008_af8ae75-readme-docs is Open on revision/008_af8ae75-readme-docs, created from main at af8ae75219275e0142f4abdcb09bb10443f1fda6. [Revision plan](REVISION-PLAN.md) records scope and stopping boundary. The user authorized opening the campaign; no review, documentation amendment or execution was requested at this checkpoint.

Before opening, the main worktree was clean, remote main was refreshed and matched the baseline, and repository-wide campaign path/ref discovery found 007 as the highest allocated sequence. Previous revision 007 was already integrated and published. This checkpoint adds only the new campaign records and the active HANDOFF; README, product documentation, source/tests, versions and releases remain unchanged.

Verification is limited to opening-record links, whitespace, branch/baseline association and changed-path ownership. No test run or documentation-quality assessment is claimed. The containing opening commit requires publication/readback; subsequent review or concrete revisions await user direction.

## V-001 — Group source backends

Implemented the user-selected heading reorganization: Source backends now contains Plain files, ZIP, TAR and 7z subsections. All prose, examples and code blocks are unchanged. The parent section ends before independent persistence, keeping the four source backends together.

Verification: exact comparison confirms non-heading content and all fenced code blocks are unchanged; the four backend headings are level three under one level-two parent; local README links resolve and git diff --check passes. No maintained reference to the replaced backend heading anchors was found. Tests were not rerun for this heading-only change. This containing action/evidence commit requires publication/readback. Campaign remains Open; no review, closure, merge, version bump or release is claimed.

## V-002 — Consumer contract and automatic backend selection

Confirmed from package exports, api.py, formats.py and backends/registry.py that build_line_index(source) normalizes a path, detects its format, opens the selected backend internally, completes scanning and closes its owned stream. Backend classes and format enums need not be imported by consumers. Both this library facade and CLI already satisfy automatic selection; library building returns an array and does not implicitly persist, whereas CLI main owns the paired file workflow.

Added a Consumer contract section to README with separate Library and CLI subsections, explicit input/output and failure boundaries, and a question-to-contract table. Distinguishes API signatures in decomposition/public-api.md from operational/error semantics in spec/public-api.md; links CLI, line-index, persistence and archive acceptance/detection contracts. Clarifies single-payload archives, explicit library destinations, independent publication and informational progress versus completed output.

Verification: inspected actual public implementation and linked authoritative contracts; all local README links resolve; existing fenced code blocks/examples are byte-for-byte unchanged, and git diff --check passes. No runtime, contract, version or test change is made; no test execution is claimed for this documentation-only amendment. The containing commit requires publication/readback. Campaign stays Open for further instructions.

## V-003 — Consumer integration reference

Applied the user's clarification: the section is now a compact entry-point/input-output table plus a core contract map for implementing consumers. It identifies automatic format selection, in-memory library results, explicit public persistence and CLI paired-output execution, then links signatures/exports, API outcomes/errors, CLI, index model, persistence, source acceptance and logging. It summarizes original uncompressed byte coordinates and independent publication without repeating backend implementation details or a usage tutorial.

Verification: existing fenced examples are unchanged, all local README links resolve and git diff --check passes. The section is explanatory navigation to existing contracts; no normative requirement, public interface, production code or tests changed. No test rerun is needed for this prose/table amendment. Commit publication/readback remains required; campaign stays Open.
