"""Complete release-name gate adapted from SDD Manager's public contract.

Every actual name is checked, irrespective of suffix or presence in a matching
expected list. Public conformance vectors are retained beside this module.
"""

from __future__ import annotations

import re
import unicodedata

_DOTTED = re.compile(r"\d+\.\d+")
_COMPONENTS = re.compile(r"(?<![a-z0-9])\d+(?:[-_]\d+){2,}(?![a-z0-9])", re.I)
_MARKED = re.compile(
    r"(?<![a-z0-9])(?:v|ver|version|release|rev|r)[-_ ]?\d+(?![a-z0-9])", re.I
)


def _names(values: list[str]) -> None:
    if any(
        not isinstance(x, str)
        or not x
        or x in (".", "..")
        or "/" in x
        or "\\" in x
        or any(ord(c) < 32 or ord(c) == 127 for c in x)
        for x in values
    ):
        raise ValueError("Inventory requires plain artifact names")
    if len({x.casefold() for x in values}) != len(values):
        raise ValueError("Duplicate or colliding artifact names")


def check_names(
    expected: list[str], observed: list[str], version: str, *, complete: bool = True
) -> None:
    """Check every expected/observed name and exact complete membership."""
    _names(expected)
    _names(observed)
    if (
        not expected
        or not version
        or version.strip() != version
        or any(c.isspace() for c in version)
    ):
        raise ValueError("A stable name contract and release version are required")
    version = version.removeprefix("v").removeprefix("V").casefold()
    core = re.split(r"[-+]", version, maxsplit=1)[0]
    forms = {version, core, core.replace(".", "_"), core.replace(".", "-")}
    for name in expected + observed:
        normal = unicodedata.normalize("NFKC", name).casefold()
        if (
            _DOTTED.search(normal)
            or _COMPONENTS.search(normal)
            or _MARKED.search(normal)
            or any(form and form in normal for form in forms)
        ):
            raise ValueError(
                "Version numbers in release artifact names are prohibited: " + name
            )
    if set(observed) - set(expected) or (complete and set(observed) != set(expected)):
        raise ValueError("Release artifact inventory differs from the stable contract")
