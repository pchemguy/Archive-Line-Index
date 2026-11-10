# Documentation revision report

## Opening checkpoint

Campaign `015_132a8e7` opened from clean `main` at `132a8e73fac4a846c03094b34586c55141cbdcfa`, matching the GitHub `main` ref. The [revision plan](REVISION-PLAN.md) records the branch, return target and scope boundary. Pause after verified publication for the documentation brief.

## R-001 compact API reference

Added the [API reference](../../../API_REF.md) and a README link. The reference presents library and CLI invocations, identifies required parameters, and explains defaults including derived output stems and omitted switches. The source distribution includes the reference and its linked contracts.

Checked live Python signatures and executed the library examples and CLI module and callable invocations against temporary fixtures. Fifteen documentation, metadata and installed CLI tests passed. An independent source build confirmed the README link and all reference targets are present. Ruff and changed-document link checks passed.

The stream example now uses a bounded `readinto` loop inside the context manager and consumes only the populated part of the reusable buffer. The parameter table retains `read(-1)` as the default and describes its memory cost. Verified the example against a compressed ZIP with multiple blocks and a short tail by comparing the digest and checking EOF and closure.

Separated the opener parameters from the stream method calls so their arguments and defaults are scoped to the correct callable. Checked the tables against the live signatures.
