# README and documentation revision report

## Opening checkpoint

Campaign 008_af8ae75-readme-docs is Open on revision/008_af8ae75-readme-docs, created from main at af8ae75219275e0142f4abdcb09bb10443f1fda6. [Revision plan](REVISION-PLAN.md) records scope and stopping boundary. The user authorized opening the campaign; no review, documentation amendment or execution was requested at this checkpoint.

Before opening, the main worktree was clean, remote main was refreshed and matched the baseline, and repository-wide campaign path/ref discovery found 007 as the highest allocated sequence. Previous revision 007 was already integrated and published. This checkpoint adds only the new campaign records and the active HANDOFF; README, product documentation, source/tests, versions and releases remain unchanged.

Verification is limited to opening-record links, whitespace, branch/baseline association and changed-path ownership. No test run or documentation-quality assessment is claimed. The containing opening commit requires publication/readback; subsequent review or concrete revisions await user direction.

## V-001 — Group source backends

Implemented the user-selected heading reorganization: Source backends now contains Plain files, ZIP, TAR and 7z subsections. All prose, examples and code blocks are unchanged. The parent section ends before independent persistence, keeping the four source backends together.

Verification: exact comparison confirms non-heading content and all fenced code blocks are unchanged; the four backend headings are level three under one level-two parent; local README links resolve and git diff --check passes. No maintained reference to the replaced backend heading anchors was found. Tests were not rerun for this heading-only change. This containing action/evidence commit requires publication/readback. Campaign remains Open; no review, closure, merge, version bump or release is claimed.
