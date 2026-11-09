# Demo Alphanum revision plan

## Campaign context

| Field | Value |
| --- | --- |
| Campaign | `010_e1d884f` |
| Status | Open |
| Working branch | `revision/010_e1d884f-demo-alphanum` |
| Creation parent and integration target | `main` |
| Baseline and branch-off commit | `e1d884f396e63d972a355423358632d19d34a987` |

## Scope

The user requested a checkout-only command-line demonstration using three alphanumeric lines and the same payload in ZIP, TGZ, TBZ, TAR and 7z archives. The inputs and both demos live under the repository's existing `docs/demo/alphanum/` tree.

| Action | Deliverable | Acceptance |
| --- | --- | --- |
| R-001 | Plain fixture, five single-member archives and CMD launcher under `docs/demo/alphanum/` | Every archive contains exactly `demo.txt` with the plain fixture's bytes. The launcher resolves the checkout from its own location and invokes the CLI from `src` on all six inputs. Each input yields the same SQLite and raw offsets. |
| R-002 | Rename the CLI launcher to `demo_cli.bat` and add `demo_api.py` and `demo_api.bat`. | The API script imports from checkout `src` and uses public indexing and persistence functions with their defaults. On clean inputs, both demos create matching SQLite and raw indexes at the same relative paths. |
| R-003 | Add a concise Alphanum demo section to the README. | Both checkout launchers, the 7z dependency, output paths and rerun behavior match the demo. |

Both demos use the selected Python's existing runtime dependencies, including `py7zr` for 7z. The campaign remains open after publishing this action.

## Evidence

The [revision report](REVISION-REPORT.md) records the opening and will track verification for subsequent actions.
