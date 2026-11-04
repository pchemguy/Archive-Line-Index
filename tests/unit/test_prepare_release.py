"""Release metadata uses UTF-8 independently of the process text locale."""

from pathlib import Path

import pytest
from scripts.prepare_release import _version


def test_project_metadata_read_is_independent_of_locale(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "pyproject.toml"
    project.write_text(
        '[project]\nversion = "0.4.0"\n# Unicode project comment: \u0141\n',
        encoding="utf-8",
    )
    read_text = Path.read_text

    def locale_read_text(
        path: Path, encoding: str | None = None, errors: str | None = None
    ) -> str:
        return read_text(path, encoding=encoding or "cp1252", errors=errors)

    monkeypatch.setattr(Path, "read_text", locale_read_text)
    assert _version(project, "v0.4.0") == "0.4.0"
