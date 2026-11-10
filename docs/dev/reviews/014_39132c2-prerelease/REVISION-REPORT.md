# Archive Stream v0.5.3 revision report

R-001 resolves F-001, F-003 and F-004. The README prioritizes CLI interpretation and shows the three records observed in a deterministic real run. Its logging scope distinguishes the scanner from the 7z worker. The component and line-index summaries now describe both completion records. The native and bundle validators require the equals delimiter for wheel entry-point metadata. The new malformed-wheel test failed before the repair and passed afterward.

The prepared v0.5.3 candidate passed 774 tests with 95% coverage, including both installed variants and all README examples. Ruff lint and format, strict mypy, active links, and native and stable-bundle validation passed. The logging baseline and checkout demo checks apply to the unchanged indexing and archive paths. Native Windows CMD and macOS execution remain unverified.

F-002 local preparation passed. Metadata is 0.5.3, the development commands use the new tag, and the root release notes cover the reviewed changes. The exact default-branch release commit will set the README download links and verify their hosted bytes.

Close by returning to the suspended CLI logging branch at `39132c2089c63808a2df5c914554b27d504b5f94`. The child opening is `ce3b466da3667d62b0dbf7d80b375d58a5dc019e`. After verified child integration, the requested release continues through the logging campaign's integration into `main`.
