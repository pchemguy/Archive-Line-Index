# Critical composition review

## Scope and evidence

Campaign 008_af8ae75-readme-docs; reviewed source af226cae5896df44054c60c313f6d85cd64ced0c on revision/008_af8ae75-readme-docs. The user requested critical composition review after the backend grouping and consumer-contract amendments. The audience is humans and agents implementing software that consumes archive-line-index. This is a findings-only review of the complete root README, with selected linked contracts considered for navigation and responsibility; it is not a project-wide documentation, implementation or security audit.

Evidence mode: non-research, repository material only; no independent web research. Applied composition analysis and software-documentation criteria from Technical Writing Assistant, within the active SDD campaign. Assessed document trajectory, section hierarchy and contribution, paragraph scope, sentence/table density, repetition and level of detail. Runtime/interface facts use the public exports/facade/detection/registry and consumer contracts inspected during V-002/V-003. No examples, builds or tests were executed for this editorial review. Locations below refer to the pinned README, not subsequent revisions.

## Overall assessment

The README accurately introduces its basic input/output model and now supplies a useful consumer-contract map. Its composition still combines an API inventory, advanced streaming examples, scanner explanation, archive fixture creation, operational caveats and contributor instructions without a clear main consumer journey. Adding Consumer contract helped local lookup but did not reconcile the surrounding structure. The document is not ready to call compositionally finished for the selected audience.

The approximately 3,094 whitespace-separated words are not inherently excessive. Most technical details have a legitimate reference, example or diagnostic role. The problem is their placement and repetition: the complete CLI workflow arrives after advanced streaming/scanning and all archive examples, while shared source rules sit inside a backend subsection. Retain precision, independent-file publication warnings, original-byte/BOM/EOF semantics, a concise scanner implementation explanation explicitly requested by the user, and examples that serve independent use. Do not shorten by discarding these guarantees or invent a new specification suite; the existing linked contracts already provide suitable detailed authorities.

## Reverse outline

| Current unit | Actual contribution | Compositional effect |
| --- | --- | --- |
| Opening, lines 3–20 | Purpose, offset example, complete interface/ownership inventory, formats and byte semantics | Good orientation, but substantially overlaps Consumer contract. |
| Installation, lines 22–33 | Install procedure, release naming/metadata explanation, dependency/build facts | Necessary setup mixed with packaging rationale and contributor detail. |
| Consumer contract, lines 35–54 | Automatic selection, interface/result summary, integration-specification map | Strong reference entry point; surrounding examples do not yet follow its priority. |
| Streaming, borrowed reader and scanner loop, lines 56–114 | Independently useful advanced API examples and implementation rationale | Interrupt the primary source-path-to-output path. |
| Source backends, lines 116–202 | Plain example, common source rules, three archive-creation examples, validation/worker details | Backend grouping is useful; shared versus format-specific responsibilities remain blurred. |
| Persistence and CLI, lines 204–268 | File representations, writers/readers, complete CLI and imported execution | Central consumer workflows arrive late. |
| Progress and memory/failure, lines 270–282 | Operational behavior and limits | Useful integration information, with logging setup separated from its explanation. |
| Development, lines 284–303 | Contributor checks, package verification and project navigation | Appropriate end placement; some earlier packaging detail could be consolidated here. |

## Findings index

| Finding | Priority | Status | Concern |
| --- | --- | --- | --- |
| R-001 | Moderate | Verified | Main task sequence prioritizes advanced APIs and implementation over source-to-output use. |
| R-002 | Moderate | Verified | Two overlapping interface summaries lack a clear division of responsibility. |
| R-003 | Moderate | Verified | Common source behavior is nested under Plain files. |
| R-004 | Moderate | Verified | Archive examples emphasize creating sources rather than consuming existing ones. |
| R-005 | Minor | Verified | Consumer table cells mix interface identification with operational detail. |
| R-006 | Minor | Verified | Logging setup is developed in an unrelated borrowed-reader example. |

Priorities describe editorial impact, not production severity. No Critical composition finding is identified; this review does not establish absence of runtime defects.

## Findings

### R-001 — Organize the main path around consumer tasks

Location: README lines 56–114, 116–202 and 204–268. After presenting the consumer reference, the document moves to ContentStream/readinto, reader borrowing and the LF-search implementation. The complete source-based library example is at lines 122–135; persistence follows all backend examples, and the CLI workflow begins at line 231. Readers who only need to provide a source and receive output must traverse material they explicitly need not understand. The early contract table makes the interfaces discoverable, so this is a sequencing defect rather than an absence of public-interface information. Confidence: high.

Proposed remedy: place source-based library use and CLI use directly after installation/consumer orientation, with persistence adjacent to the library path. Follow with input/backend details, then independently usable streaming/borrowed-reader APIs and implementation explanation. Add a small task-oriented navigation list if the retained sections remain substantial. Preserve the requested scanner excerpt and its justification; move it rather than treating implementation explanation as forbidden. This changes organization, not supported scope.

### R-002 — Give interface information a single main home

Location: README lines 3–20 and 35–54, with further repetition at lines 120, 204–206 and 231–245. The opening table already inventories functions, inputs, results and ownership; Consumer contract then introduces another interface/result table covering much of the same material. Short repeated orientation about formats or byte coordinates is justified, but the two tables currently compete as the main integration summary and create parallel maintenance surfaces. Confidence: high.

Proposed remedy: retain a clear opening overview of purpose, input/output and a small offset example, as the user requested. Make Consumer contract the main public integration map; either move the comprehensive inventory there or reduce the opening table to a non-overlapping overview. Keep task sections for examples and their local prerequisites, not another retelling of all contract facts. Do not remove the consumer contract or its core specification links to eliminate duplication. No requirement or interface change is needed.

### R-003 — Lift shared source rules above backend subsections

Location: README Source backends → Plain files, lines 118–137. Its first paragraph describes build_line_index ownership, EOF validation and array-only results for all source formats. Its closing paragraph describes text paths, URL exclusion, automatic archive detection, archive-claim failure and source stability, also shared by archives. The heading makes these common rules appear plain-file-specific, and archive consumers can reasonably skip this subsection. This is an information-scope mismatch introduced by the otherwise useful backend grouping. Confidence: high.

Proposed remedy: put common source acceptance, automatic selection and facade behavior in a short parent-level introduction. Keep Plain files focused on plain payload behavior and its example. Distinguish any common archive member policy from format-specific ZIP/TAR/7z qualifications without duplicating it in every subsection. Preserve all existing behavioral qualifications; this is a placement correction.

### R-004 — Separate example fixture creation from consumer requirements

Location: README archive examples, lines 143–154, 163–178 and 187–199. Each example creates a new archive with zipfile, tarfile or py7zr before calling the same build_line_index interface. This is valid self-contained example setup and does not actually require consumers to import package-internal backends. However, repeated archive construction occupies most of the demonstration and visually associates format-specific imports with the consumption path, weakening the newly stated automatic-selection message. Confidence: high.

Proposed remedy: demonstrate the common call on an existing source once near the consumer entry point. If complete runnable archive examples remain, label archive creation explicitly as fixture/setup work, separate it visually from the library call, or place the longer setup in an examples guide. Retain legitimate format-specific acceptance and failure differences. Do not claim archive creation code is a production defect or remove it solely to satisfy a line/word quota.

### R-005 — Reduce conceptual load in the consumer interface table

Location: README lines 39–43, especially the CLI row. A single cell combines console invocation, module invocation and the imported callable; the result cell combines scan count, two formats, naming defaults, an option and both process/callable status semantics. The table is factually useful, but its sentences carry several independently consulted dimensions. Library persistence is an operation within the library interface, while CLI is an alternate interface, so the rows also operate at different conceptual levels. Confidence: medium-high.

Proposed remedy: organize around the two consumer interfaces (Python library and CLI), grouping construction/persistence together under the library and the three CLI invocation forms together under CLI. Keep the overview cells to entry point and principal result; put naming/error/publication details in a short adjacent paragraph and use the existing contract map for precision. This is a presentation preference with a concrete readability benefit, not evidence of an invalid API model.

### R-006 — Put logging configuration with its explanation

Location: README borrowed-reader example lines 84–98 and Progress logging lines 270–276. logging.basicConfig is introduced inside an example whose stated purpose is reader borrowing and offset semantics. The later progress section sends source-path consumers back to that unrelated example for configuration. This mixes teaching goals and makes logging setup look associated with direct reader scanning rather than all library indexing. Confidence: high.

Proposed remedy: put the application-owned logging setup example or direct guidance in Progress logging, and let the borrowed-reader example focus on its contract. Keep the application-owned configuration policy, five-second cadence and scan-versus-publication distinction. Example reorganization may require adjusting the installed-example inventory coherently; the existing count of eight is test coverage of current examples, not a product requirement that forbids a sound reorganization.

## Recommended revision order

Resolve R-001 and R-002 together by choosing the document's main task sequence and main interface-information owner. Then repair R-003/R-004 within Source backends. Finish R-005/R-006 against that structure, validating contract links, retained technical qualifications and all affected executable examples. A suitable proposed outline is Overview → Installation → Consumer contract → Library/CLI workflows and outputs → Source backends → Streaming/borrowed readers → Progress and operational limits → Line-boundary implementation → Development. This is a proposal, not an accepted rewrite or a new requirement.

## Retention, limits and stopping

Retain the useful early purpose/input/output explanation, automatic backend selection, source-versus-payload byte coordinates, the separation of array construction and file persistence, the core contract map, independent publication caveats, and the explicitly requested scanner implementation snippet. The public API design and operational contract are separate useful targets; there is no finding that they should be merged merely because both filenames are public-api.md.

At the original review checkpoint, all six findings remained Open pending revision authorization; current dispositions and subsequent recheck evidence are recorded below. No README, source, tests or governing contracts are changed by this review. Closed campaign/feature records are excluded from loading and current-validity checks. No external-source verification, render/screen-size assessment, link-target content audit beyond the selected consumer contracts, full specification composition review or software execution is claimed. The containing report checkpoint must be published/read back; stop before repairs, campaign closure, integration or release.

## Authorized revision recheck — V-008

The user authorized execution of V-004–V-008, including the recommended Integration contract title for D-001. Rechecked the revised README at published source 39c032ac75361b79fa5ee7214b852322ac034d54 against the pinned original review source and requested audience. Original observations and their locations above describe the baseline; the findings index now reflects the verified after-state.

| Finding | After-state evidence | Current disposition |
| --- | --- | --- |
| R-001 | Integration contract is followed directly by Index a source through the library (construction, paired persistence and readback), then CLI use. Source backends, independent streaming/borrowing and the scanner explanation follow these workflows. | Verified by full-document sequence inspection and actual installed examples/CLI checks. |
| R-002 | Removed the competing opening function inventory; the opening retains purpose/input/output and the small byte-range example. Integration contract is the main interface/specification map. Task sections carry examples with local warnings rather than a second inventory. | Verified; limited repetition of byte coordinates and independent publication serves orientation and safe local reading. |
| R-003 | Shared path types, URL exclusion, automatic format selection, source stability and archive member policy are parent-level Source backends content. Its four subsections retain their actual format differences. | Verified by heading/topic-scope comparison and retained contract mapping. |
| R-004 | One common source-based call and complete persistence workflow precede backend details. Archive examples explicitly identify imports/construction as fixture setup and label the common consuming call; their executable behavior is unchanged. | Verified; complete examples remain independently runnable and backend selection is explicitly automatic. |
| R-005 | The integration table has two interface rows, Python library and CLI. Library persistence is within the library interface, and alternate CLI invocation forms are adjacent prose. Naming/error/publication details remain in relevant workflows/contracts. | Verified by table and paragraph inspection; no interface/guarantee change. |
| R-006 | Progress logging contains its own complete source-based application-configuration example. Borrowed-reader scanning no longer imports/configures logging; progress guidance no longer depends on that unrelated example. | Verified by example inspection and execution of all nine examples in both installed variants. |

The after-state retains all seven core contract links, public identifiers, original payload-byte coordinates, BOM/LF/EOF and bounds, supported formats/sole-member constraints, input stability/ownership, file encodings/schema, protected/independent publication, cleanup notes and CLI outcomes. ZIP CRC/declared-size checks, TAR trailing-entry/footer validation and 7z bounded-worker/cancellation limitations retain their scope and qualifications. The explicitly requested scanner excerpt and alternatives/rationale/link are unchanged. Packaging rationale moved to Development without losing pinned-release guidance beside installation.

Example fidelity: six original Python example ASTs are unchanged, two are intentionally revised (complete source-to-storage workflow; borrowed-reader logging removed), and one new source-based logging example is added. The example test explicitly requires and runs all nine, rather than skipping new material or weakening coverage. The scanner excerpt is byte-for-byte unchanged. Runtime source, APIs, normative contracts, version, release notes and frozen records are unchanged.

Actual verification: 27 focused integration cases passed in 11.99 seconds, comprising tests/integration/test_documentation_examples.py, test_installed_cli.py and test_progress_logging.py. The documentation cases execute all nine Python examples in clean installed wheel and source-rebuilt runtimes; the CLI cases exercise console/module/imported routes and progress cases cover configuration behavior. Ruff lint and formatting pass across src/tests/scripts (77 files). Current README/active-record paths and heading links, Markdown whitespace and scoped/protected-path checks pass. Earlier action-specific example results remain in REVISION-REPORT. No full runtime-suite rerun, live release/download check or native Windows/macOS execution is claimed for this documentation change; no visual browser-render assessment was performed.

All six selected findings are Verified with no remaining revision decision. The campaign remains Open at the human-selected execution boundary; verification does not authorize closure, main integration, version bump or release.
