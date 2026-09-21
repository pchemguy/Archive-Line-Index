# Immutable archive fixtures

Tests normally generate small archives under pytest's temporary directory via
`tests/helpers/archive_factory.py`. Generated archives are not repository
content.

This directory is reserved for small malformed samples that cannot be produced
reliably with the declared runtime dependencies. Every such file must be
documented here with its purpose, generating tool and version, exact command or
script, and a checksum. There are currently no immutable binary fixtures.
