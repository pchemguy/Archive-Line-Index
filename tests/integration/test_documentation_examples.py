"""Run complete README Python examples against each installed artifact."""

import re
from pathlib import Path

import pytest
from tests.helpers.packaging import InstalledPackage

pytestmark = [pytest.mark.integration, pytest.mark.timeout(300)]


def test_readme_examples_are_complete_and_installed(
    installed_package: InstalledPackage,
) -> None:
    readme = Path(__file__).resolve().parents[2] / "README.md"
    examples = re.findall(
        r"^```python\n(.*?)^```", readme.read_text(), flags=re.M | re.S
    )
    assert len(examples) == 3, (
        "stream, direct scanning and source building examples required"
    )
    for example in examples:
        installed_package.run(example)
