"""Baseline tests for package discovery and importability."""


def test_package_is_importable() -> None:
    import archive_line_index

    assert archive_line_index.__name__ == "archive_line_index"
