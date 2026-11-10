"""Execute the shared CLI only when invoked as a module, never on import."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
