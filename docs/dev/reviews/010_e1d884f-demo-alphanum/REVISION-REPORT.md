# Demo Alphanum revision report

## Opening checkpoint

Campaign `010_e1d884f` opened on `revision/010_e1d884f-demo-alphanum` from `main` at `e1d884f396e63d972a355423358632d19d34a987`. The starting worktree was clean and the remote `main` ref matched the baseline. The [revision plan](REVISION-PLAN.md) records the campaign scope and target.

Opening verification covers changed paths, record links, whitespace and branch ancestry. After publication is verified, the campaign pauses for the Demo Alphanum brief.

## R-001 checkout demo

Created the [CMD launcher](../../../demo/alphanum/demo.bat), the plain fixture and five archives in the existing `docs/demo/alphanum/` tree. The launcher resolves the repository from its own path, prepends `src` to the Python import path and returns a failure status if indexing fails. Directory-scoped Git attributes preserve LF bytes in the plain payload and CRLF lines in the CMD launcher.

Verified that ZIP, TGZ, TBZ, TAR and 7z each contain exactly one `demo.txt` matching the 65-byte plain fixture. In a temporary checkout path containing spaces with Git's CRLF conversion enabled, the plain fixture retained LF and the CMD launcher retained CRLF. In Linux, CPython 3.12 with py7zr 1.1.4 ran the six CLI commands from `src` with Archive Line Index absent from the interpreter's default import path. Both SQLite and little-endian raw output contained offsets 0, 11, 38 and 65 for every input. Native Windows CMD execution remains unverified.
