# Acceptance evidence

## Purpose

[SPEC.md](SPEC.md) and its child specifications remain normative. This file
maps each numbered acceptance condition to durable executable or manual
evidence; it does not add requirements. The identifiers below are local labels
formed from the owning specification and its condition number. Actual command
results belong in the append-only implementation journal.

Automated selectors name focused evidence, not necessarily every test that
also exercises a condition. Manual evidence is used only where the condition
depends on the execution environment or artifact inspection. The final
campaign ran on Linux; Windows and macOS behavior remains covered by portable
and host-conditional tests but requires those hosts for direct confirmation.
The slow generated input cases sample incremental memory and establish a
bounded-buffer scaling argument; this host did not stream a source larger than
its physical memory. Their process RSS measurement is not an absolute memory
ceiling or a cross-platform peak measurement.

## System conditions

| ID | Condition | Evidence |
| --- | --- | --- |
| SYS-1 | Equivalent formats yield identical bytes and indexes. | `tests/integration/test_content_stream.py::test_zip_and_plain_streams_are_byte_identical`<br>`tests/integration/test_content_stream.py::test_tar_variants_and_plain_are_byte_identical`<br>`tests/integration/test_content_stream.py::test_sevenzip_and_plain_streams_are_byte_identical`<br>`tests/integration/test_index_building.py::test_zip_build_matches_plain_and_expected_offsets`<br>`tests/integration/test_index_building.py::test_tar_variants_match_expected_offsets`<br>`tests/integration/test_index_building.py::test_sevenzip_build_matches_expected_offsets` |
| SYS-2 | Bounded streaming and no extraction support inputs larger than available memory. | `tests/integration/test_large_inputs.py::test_rss_sampler_tracks_this_process`<br>`tests/integration/test_large_inputs.py::test_large_plain_payload_streams_with_bounded_process_memory`<br>`tests/integration/test_large_inputs.py::test_highly_compressible_7z_expands_through_bounded_reads`<br>`tests/integration/test_resource_lifecycle.py::test_backend_creates_no_decompressed_member_artifact`<br>Manual: structural bounded-buffer review plus sampled RSS support the scaling inference; a greater-than-RAM execution was unavailable. |
| SYS-3 | Canonical byte-line cases produce exact offsets and EOF. | `tests/unit/test_scanner.py::test_canonical_binary_cases` |
| SYS-4 | Newlines and BOMs split across boundaries remain correct. | `tests/unit/test_scanner.py::test_results_are_invariant_across_scan_block_boundaries`<br>`tests/unit/test_scanner.py::test_split_bom_and_arbitrary_short_reads` |
| SYS-5 | Invalid structure and corrupt archives use the public error model. | `tests/unit/backends/test_zip.py::test_zero_multiple_and_metadata_files_are_rejected`<br>`tests/unit/backends/test_tar.py::test_truncated_compressed_archive_is_rejected`<br>`tests/unit/backends/test_sevenzip.py::test_invalid_and_truncated_archives_are_open_failures` |
| SYS-6 | Terminal EOF validates; early close is explicitly non-validating. | `tests/integration/test_content_stream.py::test_zip_crc_failure_is_raised_through_public_stream`<br>`tests/integration/test_resource_lifecycle.py::test_early_and_repeated_close_release_resources` |
| SYS-7 | Every package-owned resource is deterministically released. | `tests/integration/test_resource_lifecycle.py::test_normal_exhaustion_closes_package_resources`<br>`tests/integration/test_filesystem_portability.py::test_zip_processing_failure_closes_backend_handles_before_caller_cleanup` |
| SYS-8 | SQLite and raw persistence reproduce the source offsets. | `tests/integration/test_persistence_equivalence.py::test_source_index_round_trips_identically_through_both_formats` |
| SYS-9 | Existing destinations require explicit replacement. | `tests/unit/persistence/test_sqlite.py::test_existing_destination_is_protected_without_temporary_file`<br>`tests/unit/persistence/test_raw.py::test_existing_destination_is_protected_without_temporary_file`<br>`tests/integration/test_persistence_equivalence.py::test_repeated_authorized_replacement_is_whole_file` |
| SYS-10 | Failed replacement preserves the previous destination. | `tests/integration/test_persistence_equivalence.py::test_prepublication_failure_preserves_prior_bytes_and_cleans_artifacts` |
| SYS-11 | Unit, integration, lifecycle, persistence, and installed tests pass on available supported hosts. | `tests/integration/test_installed_package_workflow.py::test_complete_public_workflow`<br>Manual: final journal records the complete Linux campaign; Windows and macOS require host runs. |
| SYS-12 | The installed package works outside the repository. | `tests/integration/test_installed_package_workflow.py::test_complete_public_workflow`<br>Manual: final campaign installs both sdist and wheel into clean external environments. |

## Archive-handling conditions

| ID | Required case | Evidence |
| --- | --- | --- |
| ARCH-1 | Empty member. | `tests/unit/backends/test_zip.py::test_empty_member_is_valid`<br>`tests/unit/backends/test_tar.py::test_empty_member_is_valid`<br>`tests/unit/backends/test_sevenzip.py::test_empty_member_is_valid` |
| ARCH-2 | One regular member with and without directories. | `tests/unit/backends/test_zip.py::test_empty_member_is_valid`<br>`tests/unit/backends/test_tar.py::test_empty_member_is_valid`<br>`tests/unit/backends/test_sevenzip.py::test_empty_member_is_valid`<br>`tests/unit/backends/test_zip.py::test_path_streams_nested_member_with_directories`<br>`tests/unit/backends/test_tar.py::test_tar_variants_stream_nested_member`<br>`tests/unit/backends/test_sevenzip.py::test_path_streams_nested_member_with_directory` |
| ARCH-3 | Nested member path. | `tests/unit/backends/test_zip.py::test_path_streams_nested_member_with_directories`<br>`tests/unit/backends/test_sevenzip.py::test_path_streams_nested_member_with_directory` |
| ARCH-4 | Zero and multiple regular members. | `tests/unit/backends/test_zip.py::test_zero_multiple_and_metadata_files_are_rejected`<br>`tests/unit/backends/test_tar.py::test_zero_regular_files_are_rejected_before_delivery`<br>`tests/unit/backends/test_tar.py::test_reports_late_additional_member`<br>`tests/unit/backends/test_sevenzip.py::test_zero_multiple_and_metadata_files_are_rejected` |
| ARCH-5 | Regular member plus special entry. | `tests/unit/backends/test_zip.py::test_symlink_entry_is_rejected_even_with_one_file`<br>`tests/unit/backends/test_tar.py::test_reports_late_special_member` |
| ARCH-6 | Metadata file plus intended file. | `tests/unit/backends/test_zip.py::test_zero_multiple_and_metadata_files_are_rejected`<br>`tests/unit/backends/test_tar.py::test_reports_late_additional_member`<br>`tests/unit/backends/test_sevenzip.py::test_zero_multiple_and_metadata_files_are_rejected` |
| ARCH-7 | Corrupt and truncated archives. | `tests/unit/backends/test_zip.py::test_invalid_and_truncated_archives_are_open_failures`<br>`tests/unit/backends/test_tar.py::test_truncated_compressed_archive_is_rejected` |
| ARCH-8 | Misleading recognized suffixes. | `tests/integration/test_content_stream.py::test_misleading_tar_suffix_is_never_plain_fallback`<br>`tests/integration/test_content_stream.py::test_misleading_sevenzip_suffix_is_never_plain_fallback` |
| ARCH-9 | Signature recognition with unconventional names. | `tests/integration/test_content_stream.py::test_valid_signature_archive_with_unconventional_name_is_streamed`<br>`tests/integration/test_content_stream.py::test_signature_claimed_invalid_archives_never_fall_back_to_plain` |
| ARCH-10 | String and path-like filesystem sources. | `tests/integration/test_filesystem_portability.py::test_unicode_path_like_values_round_trip` |
| ARCH-11 | Declared-size and actual-size limits. | `tests/unit/test_stream.py::test_declared_size_limit_rejects_before_read_and_closes`<br>`tests/unit/test_stream.py::test_actual_size_limit_rejects_first_excess_without_delivery` |
| ARCH-12 | Early close during extraction. | `tests/unit/backends/test_sevenzip.py::test_early_close_joins_worker`<br>`tests/integration/test_resource_lifecycle.py::test_early_and_repeated_close_release_resources` |
| ARCH-13 | Terminal failure after earlier payload delivery. | `tests/unit/backends/test_sevenzip.py::test_failure_after_prefix_is_raised_on_next_progress_read`<br>`tests/unit/backends/test_zip.py::test_crc_failure_is_translated_during_read` |

## Content-stream conditions

| ID | Condition | Evidence |
| --- | --- | --- |
| STREAM-1 | Bounded reads are byte-identical across formats. | `tests/integration/test_content_stream.py::test_zip_and_plain_streams_are_byte_identical`<br>`tests/integration/test_content_stream.py::test_tar_variants_and_plain_are_byte_identical`<br>`tests/integration/test_content_stream.py::test_sevenzip_and_plain_streams_are_byte_identical` |
| STREAM-2 | Read size does not change the byte sequence. | `tests/unit/test_stream.py::test_read_sizes_follow_binary_io_behavior`<br>`tests/unit/backends/test_sevenzip.py::test_arbitrary_reads_split_and_coalesce_producer_blocks` |
| STREAM-3 | Short, zero-size, readinto, and unbounded reads follow binary I/O semantics. | `tests/unit/test_stream.py::test_read_sizes_follow_binary_io_behavior`<br>`tests/unit/test_stream.py::test_readinto_writes_only_returned_bytes`<br>`tests/unit/test_stream.py::test_repeated_bounded_reads_and_eof` |
| STREAM-4 | The first actual byte beyond the inclusive limit is rejected. | `tests/unit/test_stream.py::test_actual_size_limit_rejects_first_excess_without_delivery` |
| STREAM-5 | Terminal backend failures are not converted to EOF. | `tests/unit/test_stream.py::test_backend_failure_closes_stream_and_propagates`<br>`tests/unit/test_stream.py::test_false_eof_is_extraction_error` |
| STREAM-6 | Close and exceptional paths release owned resources. | `tests/integration/test_resource_lifecycle.py::test_context_exit_after_consumer_exception_releases_resources`<br>`tests/integration/test_resource_lifecycle.py::test_declared_size_failure_releases_resources_and_joins_worker` |
| STREAM-7 | Deterministic close leaves no 7z worker alive. | `tests/unit/backends/test_sevenzip.py::test_close_unblocks_blocked_producer_and_joins_worker` |
| STREAM-8 | A slow consumer cannot create unbounded lookahead. | `tests/unit/backends/test_sevenzip.py::test_one_slot_queue_applies_slow_consumer_backpressure` |
| STREAM-9 | Bounded large streaming does not retain the full payload. | `tests/integration/test_large_inputs.py::test_highly_compressible_7z_expands_through_bounded_reads` |

## Line-index conditions

| ID | Condition | Evidence |
| --- | --- | --- |
| INDEX-1 | Required examples yield exact arrays. | `tests/unit/test_scanner.py::test_canonical_binary_cases` |
| INDEX-2 | Block boundaries and legal short reads do not change results. | `tests/unit/test_scanner.py::test_results_are_invariant_across_scan_block_boundaries`<br>`tests/unit/test_scanner.py::test_split_bom_and_arbitrary_short_reads` |
| INDEX-3 | Scanning uses native block search. | `tests/unit/test_scanner.py::test_scanner_uses_native_find_not_python_byte_iteration` |
| INDEX-4 | Long lines are not accumulated. | `tests/unit/test_scanner.py::test_line_larger_than_buffer_is_not_accumulated`<br>`tests/integration/test_large_inputs.py::test_line_far_larger_than_scan_buffer_is_not_retained` |
| INDEX-5 | Direct scanning leaves caller streams open. | `tests/unit/test_scanner.py::test_scanner_does_not_close_caller_stream` |
| INDEX-6 | Archive scanning completes terminal validation before return. | `tests/integration/test_index_building.py::test_zip_build_matches_plain_and_expected_offsets`<br>`tests/integration/test_index_building.py::test_composed_zip_build_rejects_terminal_crc_failure` |
| INDEX-7 | Invalid buffer sizes and unrepresentable offsets are rejected. | `tests/unit/test_scanner.py::test_nonpositive_buffer_size_is_rejected_before_read`<br>`tests/unit/test_scanner.py::test_noninteger_buffer_size_is_rejected_before_read`<br>`tests/unit/test_offsets.py::test_constructor_rejects_unrepresentable_or_noninteger_values`<br>`tests/unit/test_offsets.py::test_offset_above_shared_signed_range_is_rejected` |
| INDEX-8 | Structural validation accepts canonical arrays and rejects invalid shapes. | `tests/unit/test_offsets.py::test_valid_zero_one_and_multi_line_shapes`<br>`tests/unit/test_offsets.py::test_non_array_inputs_are_rejected`<br>`tests/unit/test_offsets.py::test_wrong_array_type_code_is_rejected`<br>`tests/unit/test_offsets.py::test_empty_array_is_rejected`<br>`tests/unit/test_offsets.py::test_invalid_first_offset_is_rejected`<br>`tests/unit/test_offsets.py::test_duplicate_and_descending_offsets_are_rejected`<br>`tests/unit/test_offsets.py::test_offset_above_shared_signed_range_is_rejected` |

## Persistence conditions

| ID | Condition | Evidence |
| --- | --- | --- |
| PERSIST-1 | Representative and generated indexes round trip through both formats. | `tests/integration/test_persistence_equivalence.py::test_source_index_round_trips_identically_through_both_formats`<br>`tests/integration/test_persistence_equivalence.py::test_generated_large_index_round_trips_through_both_readers` |
| PERSIST-2 | SQLite uses the exact canonical table and rows. | `tests/unit/persistence/test_sqlite.py::test_write_creates_exact_schema_and_rows` |
| PERSIST-3 | Raw bytes are portable little-endian uint64 values. | `tests/unit/persistence/test_raw.py::test_write_produces_exact_little_endian_bytes`<br>`tests/unit/persistence/test_raw.py::test_big_endian_encoding_uses_swapped_copy_without_mutating_input` |
| PERSIST-4 | Both loaded arrays equal each other and the source. | `tests/integration/test_persistence_equivalence.py::test_source_index_round_trips_identically_through_both_formats` |
| PERSIST-5 | Existing destinations are protected by default. | `tests/unit/persistence/test_sqlite.py::test_existing_destination_is_protected_without_temporary_file`<br>`tests/unit/persistence/test_raw.py::test_existing_destination_is_protected_without_temporary_file` |
| PERSIST-6 | Pre-publication failures preserve prior bytes and clean temporary files. | `tests/integration/test_persistence_equivalence.py::test_prepublication_failure_preserves_prior_bytes_and_cleans_artifacts` |
| PERSIST-7 | Invalid schemas, lengths, and offset content are rejected. | `tests/unit/persistence/test_sqlite.py::test_read_rejects_noncanonical_schema`<br>`tests/unit/persistence/test_raw.py::test_read_rejects_empty_or_misaligned_file`<br>`tests/unit/persistence/test_raw.py::test_read_rejects_invalid_decoded_offsets` |
| PERSIST-8 | Raw loading does not use mmap. | `tests/unit/persistence/test_raw.py::test_raw_reader_does_not_use_or_expose_mmap` |
| PERSIST-9 | Persistence formats contain no source identity or metadata. | `tests/unit/persistence/test_sqlite.py::test_write_creates_exact_schema_and_rows`<br>`tests/unit/persistence/test_raw.py::test_write_produces_exact_little_endian_bytes` |

## Public API conditions

| ID | Condition | Evidence |
| --- | --- | --- |
| API-1 | Every documented export imports from an installed wheel. | `tests/integration/test_import_surface.py::test_package_exports_exact_documented_public_surface`<br>`tests/integration/test_installed_package_workflow.py::test_complete_public_workflow` |
| API-2 | Internal backend and persistence names are not re-exported. | `tests/integration/test_import_surface.py::test_package_exports_exact_documented_public_surface` |
| API-3 | Invalid arguments fail before resource acquisition or mutation. | `tests/integration/test_index_building.py::test_invalid_options_fail_before_path_open`<br>`tests/integration/test_persistence_api.py::test_public_validation_precedes_temporary_creation` |
| API-4 | Package-owned paths close; direct scanner inputs remain caller-owned. | `tests/integration/test_resource_lifecycle.py::test_path_owned_source_file_is_closed_after_exhaustion`<br>`tests/unit/test_scanner.py::test_scanner_does_not_close_caller_stream` |
| API-5 | Direct scanning and source composition produce equal offsets. | `tests/integration/test_index_building.py::test_path_build_matches_direct_stream_scan` |
| API-6 | Public persistence protects destinations and preserves failed replacements. | `tests/unit/persistence/test_sqlite.py::test_existing_destination_is_protected_without_temporary_file`<br>`tests/unit/persistence/test_raw.py::test_existing_destination_is_protected_without_temporary_file`<br>`tests/integration/test_persistence_equivalence.py::test_repeated_authorized_replacement_is_whole_file`<br>`tests/integration/test_persistence_equivalence.py::test_prepublication_failure_preserves_prior_bytes_and_cleans_artifacts` |
| API-7 | Public errors are stable and translated causes are retained. | `tests/integration/test_persistence_api.py::test_public_sqlite_translation_retains_engine_cause`<br>`tests/integration/test_content_stream.py::test_signature_claimed_invalid_archives_never_fall_back_to_plain` |
