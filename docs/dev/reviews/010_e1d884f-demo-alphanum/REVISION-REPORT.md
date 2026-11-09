# Demo Alphanum revision report

## Opening checkpoint

Campaign `010_e1d884f` opened on `revision/010_e1d884f-demo-alphanum` from `main` at `e1d884f396e63d972a355423358632d19d34a987`. The starting worktree was clean and the remote `main` ref matched the baseline. The [revision plan](REVISION-PLAN.md) records the campaign scope and target.

Opening verification covers changed paths, record links, whitespace and branch ancestry. After publication is verified, the campaign pauses for the Demo Alphanum brief.

## R-001 checkout demo

Created the [CMD launcher](../../../demo/alphanum/demo_cli.bat), the plain fixture and five archives in the existing `docs/demo/alphanum/` tree. The launcher resolves the repository from its own path, prepends `src` to the Python import path and returns a failure status if indexing fails. Directory-scoped Git attributes preserve LF bytes in the plain payload and CRLF lines in the CMD launcher.

Verified that ZIP, TGZ, TBZ, TAR and 7z each contain exactly one `demo.txt` matching the 65-byte plain fixture. In a temporary checkout path containing spaces with Git's CRLF conversion enabled, the plain fixture retained LF and the CMD launcher retained CRLF. In Linux, CPython 3.12 with py7zr 1.1.4 ran the six CLI commands from `src` with Archive Line Index absent from the interpreter's default import path. Both SQLite and little-endian raw output contained offsets 0, 11, 38 and 65 for every input. Native Windows CMD execution remains unverified.

## R-002 API demo

Renamed the CLI launcher to [demo_cli.bat](../../../demo/alphanum/demo_cli.bat) and added [demo_api.py](../../../demo/alphanum/demo_api.py) with a [CMD wrapper](../../../demo/alphanum/demo_api.bat). The API script prepends checkout `src` to `sys.path` before importing Archive Line Index and calls the public index builder and writers with their defaults.

On Linux, launched the API script from outside two temporary checkout copies with spaces in their paths and no `PYTHONPATH` or installed Archive Line Index on the import path. Compared its outputs with the six CLI commands run on separate clean fixtures. All relative output names and SQLite and raw offsets matched. A repeat API run preserved the existing SQLite output and returned a failure status. Ruff lint and format checks passed, and Git checkout preserved CRLF in both CMD launchers. Native Windows CMD execution remains unverified.
