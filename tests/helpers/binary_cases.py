"""Canonical byte corpora shared by scanner and backend integration tests."""

from dataclasses import dataclass


UTF8_BOM = b"\xef\xbb\xbf"


@dataclass(frozen=True, slots=True)
class BinaryCase:
    name: str
    content: bytes
    skip_bom: bool
    offsets: tuple[int, ...]


BINARY_CASES = (
    BinaryCase("empty", b"", True, (0,)),
    BinaryCase("empty-no-skip", b"", False, (0,)),
    BinaryCase("bom-only", UTF8_BOM, True, (3,)),
    BinaryCase("bom-only-no-skip", UTF8_BOM, False, (0, 3)),
    BinaryCase("unterminated", b"abc", True, (0, 3)),
    BinaryCase("terminated", b"abc\n", True, (0, 4)),
    BinaryCase("crlf", b"abc\r\n", True, (0, 5)),
    BinaryCase("lone-cr", b"abc\rdef", True, (0, 7)),
    BinaryCase("empty-line", b"\n", True, (0, 1)),
    BinaryCase("two-empty-lines", b"\n\n", True, (0, 1, 2)),
    BinaryCase("mixed-empty", b"a\n\nb", True, (0, 2, 3, 4)),
    BinaryCase("bom-terminated", UTF8_BOM + b"abc\n", True, (3, 7)),
    BinaryCase("bom-empty-line", UTF8_BOM + b"\n", True, (3, 4)),
    BinaryCase("later-bom", b"a\n" + UTF8_BOM, True, (0, 2, 5)),
    BinaryCase("incomplete-bom-1", b"\xef", True, (0, 1)),
    BinaryCase("incomplete-bom-2", b"\xef\xbb", True, (0, 2)),
)
