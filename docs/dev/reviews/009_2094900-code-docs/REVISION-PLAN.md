# Revision and patch-release plan

## Authority and baseline

Campaign 009_2094900-code-docs; original reviewed/branch-off source 209490063eb2e299243fc7ad99e63a08305e0f3e, creation parent/return target main; working branch revision/009_2094900-code-docs. [Review report](REVIEW-REPORT.md) records three confirmed findings. The user authorized preparing this plan, fixing all findings, preparing a patch release, closing the campaign and publishing the release. Selected version: 0.5.1, because the only runtime change corrects resource lifetime without changing public interfaces or formats.

## Ordered actions

| Action | Findings | Changes | Acceptance |
| --- | --- | --- | --- |
| V-001 | R-001 | Add observable failing read-frame reclamation and cleanup-retry/exception-preservation regressions; release the stream's failure reference only after successful explicit resource closure. | Observe RED before source edit; GREEN proves retained failure before close, retry after failed cleanup, reclaimable frames while closed stream remains alive and unmodified externally held exception evidence. Rerun stream/API/lifecycle cases and memory probe. |
| V-002 | R-002 | Reconcile current test layout ownership with actual delivered test files, including principal archive/lifecycle/installed owners. | All concrete test references resolve and covered responsibility descriptions match existing tests; no invented empty files or closed-record changes. |
| V-003 | R-003 | Set project Flowmark width to 0, retaining semantic=false and existing cleanup settings. | Default formatter preserves single-line paragraphs/list items in nonmutating probes; no whole-tree reformat. |
| V-004 | All / release | Recheck coupled source/doc scope; bump static version and current install examples to 0.5.1; collect complete changes since v0.5.0 and prepare exact release notes, run full tests/tools and package gates. | All findings Verified with evidence, full configured suite/tool checks pass, safe stable source/wheel bundles/checksum candidates, accurate notes and native limits. |

## Completion and publication

Each action commits its change and observed evidence together and is published/read back before dependent work. Finalize campaign records before explicit two-parent main integration and closure. Verify/publish the target, then create the exact default-branch release commit with root RELEASE-NOTES.md as its literal body, rebuild final native packages and stable bundles from that commit, verify source identity and installed/rebuilt consumers, publish/read back the v0.5.1 tag, and use one GitHub draft/upload/verify/publish route. Verify exact release body and all tag-specific/latest downloaded bytes. Stable outer names remain archive-line-index-wheel.zip, archive-line-index-source.zip and SHA256SUMS. Preserve existing tags/releases and all prior closed records.

No new feature/API/format or project requirement is selected. The accepted current layout amendment is limited to R-002, and config amendment to R-003. Release notes include the already integrated README/test-hardening changes since v0.5.0 without presenting their earlier work as new runtime behavior. Native Windows/macOS/other Python/big-endian execution remains unverified. Stop after verified release publication and clean published main outcome checkpoint.
