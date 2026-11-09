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

## R-003 README demo

Added a concise [Alphanum demo section](../../../../README.md#alphanum-demo) after the CLI workflow. It gives the checkout commands, the 7z dependency, the output locations and the rerun requirement. Verified the documented launchers, fixture paths and dependency against the checkout. All nine existing README Python snippets were preserved, and both installed-artifact documentation tests passed.

## Final campaign verification

R-001 through R-003 are verified at the final implementation tip `4ed9a2c04de6715bf02d31fb403f11fcb78f2092`. All five archives contain only `demo.txt` with bytes identical to the plain fixture. From checkout sources on Linux, the API script and the six CLI commands produced identical SQLite and raw offsets for every fixture. Checked the final CMD path assignment, launchers' CRLF checkout and README commands. Both installed-artifact README example tests passed, and Ruff lint and format checks passed for the API demo. Native Windows CMD execution remains unverified.

The user requested closure. The recorded creation parent and integration target are `main`, confirmed at `e1d884f396e63d972a355423358632d19d34a987` before this checkpoint. The opening commit is `5985aec9abed6bf74261d7a21fa88ae2b0b37e79`. Closure takes effect when the verified two-parent integration commit is published on `main`.
