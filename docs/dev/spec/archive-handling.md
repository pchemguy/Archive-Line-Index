# Archive-handling contract

## Formats and source domain

The detector, selector and adapters in [DECOMPOSITION](../DECOMPOSITION.md) implement this contract through the accepted [internal reader interface](../decomposition/internal-api.md). Sources are stable filesystem files; detection owns a short-lived inspection handle and adapter opening uses a separate handle from the beginning. ZIP and 7z may seek their underlying archive files while public payload access remains sequential.

Required archive support is unencrypted ZIP, uncompressed TAR, gzip/bzip2/xz-compressed TAR and 7z through the declared libraries. A missing codec required for a recognized source is `UnsupportedFormatError`, with its cause retained. Further compression variants are not implicitly required merely because a later Python build can open them. Standalone gzip, bzip2 and xz content that is not TAR is not a supported compressed plain file.

## Detection

Detection reads at most 512 source bytes and records signature and suffix evidence in `FormatCandidate`. It recognizes the 7z magic; ZIP local-file, empty-archive and descriptor signatures; gzip, bzip2 and xz signatures as TAR candidates; and a nonzero complete TAR header with a valid conventional checksum. Backend parsing remains authoritative for full validity.

Recognized suffixes are `.zip`, `.7z`, `.tar`, `.tar.gz`, `.tgz`, `.tar.bz2`, `.tbz`, `.tbz2`, `.tar.xz` and `.txz`, compared case-insensitively and with compound suffixes evaluated together. A recognized signature takes precedence even if a suffix claims another format. With no recognized signature, a recognized suffix selects its archive candidate. If that candidate is invalid, opening raises `InvalidArchiveError` rather than falling back to plain bytes. With neither form of evidence, input is plain regardless of an unknown suffix.

A zero-filled prefix is not by itself a TAR signature. An empty TAR with a recognized suffix still selects TAR and fails the member-count rule. Gzip/bzip2/xz signatures require a valid TAR payload even without a TAR suffix. Detection does not promise identification of every unsupported archive format whose bytes lack supported signatures or suffix claims; unknown bytes remain eligible plain payloads.

## Member structure

An accepted archive contains exactly one exposed regular-file member. An empty regular file or a member nested under directories is valid. Directory entries do not count, and names/suffixes do not restrict payload content. Additional metadata files count as ordinary files, including `__MACOSX` entries. Zero regular members, multiple regular members, links, devices, FIFOs, sockets or other exposed special entries raise `ArchiveStructureError`.

Library-consumed TAR extension headers that are not exposed as payload members are not additional regular files. Directory versus special-entry classification uses each format's metadata, including ZIP external attributes where supplied; entries reported as links or special types are not reinterpreted as ordinary bytes. The package never joins a member name to an extraction directory or materializes a member path.

Detected encryption is rejected as specified by the [public error contract](public-api.md). No password, prompt or credential lookup is attempted. A backend must not silently select one file from a structurally invalid multi-file archive.

## Adapter completion

Plain delivery exposes the file's bytes. ZIP validates the complete member list before payload delivery when available and includes member integrity checks when the member is exhausted. TAR uses sequential iteration and validates exposed trailing entries before terminal completion; an invalid later member may therefore fail after payload bytes were returned. TAR header parsing and gzip/bzip2/xz trailer checks available through the selected standard-library path must complete before validated EOF.

The 7z adapter inspects available member metadata before extraction, extracts only the accepted member through its custom callback writer and verifies dependency completion. It starts one outer package-owned non-daemon extraction thread per active stream, uses bounded transport and joins it under the [stream lifecycle](content-stream.md). Callback synchronization must be correct under the actual supported dependency behavior; dependency-created internals are not misreported as package-owned workers.

A corrupt footer, CRC mismatch, truncated compressed payload or decompression error discovered during delivery/terminal work is `ExtractionError`; malformed candidate opening is `InvalidArchiveError`; invalid member structure remains `ArchiveStructureError`. Source filesystem errors retain their ordinary types. A backend returns empty bytes with `completed=True` only after all checks available through its supported library path succeed. This does not claim cryptographic authenticity or detection of corruption the backend cannot observe.

## Dependency suitability

The selected `py7zr` version and codec support must be recorded with integration evidence for valid large inputs, empty content, callback forwarding, CRC/truncation failures and active early close. Configure supported dependency limits where necessary so valid documented large payloads are not rejected by an unrelated default cap. The implementation must either meet the required contract on its chosen dependency version or report a blocker; silently using complete extraction/materialization is not an alternative implementation.

## Acceptance

- ARC-01: Every required archive family, plain file, recognized suffix variant and signature-recognized unconventional filename selects and streams the expected payload.
- ARC-02: Signature/suffix conflicts use signature precedence; malformed suffix-claimed archives and non-TAR compressed streams fail without plain fallback; unknown suffixes remain legal for plain bytes.
- ARC-03: Empty regular members and nested members are accepted; zero/multiple files, additional metadata files and representable special entries are rejected without filesystem extraction.
- ARC-04: Malformed opening, truncated delivery, terminal CRC/footer failure and detected encryption follow the documented classification and never become successful terminal EOF.
- ARC-05: TAR trailing-member validation and 7z producer completion are required for a completed index even when the selected payload bytes were already delivered.
- ARC-06: Actual dependency integration exercises callback chunking, bounded backpressure, empty payload, early close and failure cleanup; tested versions/capabilities are recorded rather than inferred from installation alone.
