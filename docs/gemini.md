# Zero-Compromise Quality Mandate & Implementation Plan

## Mantra
**TDD → Build Feature → Regression Suite → TDD (Next Feature) → Build Feature → Regression Suite → ...**

## Objective
Execute comprehensive test suite remediation and feature implementation with **NO shortcuts**. Fix code to pass tests, not skip tests to pass builds.

## Current Status
- **Phase 1 (Performance Suite):** ✅ Completed. All performance tests restored and passing.
- **Phase 2 (Feature Implementation):** ✅ Completed.
    - **Auth:** JWT implemented and tested.
    - **Search:** Semantic search with Vector Store implemented and tested.
    - **Telemetry:** Telemetry service and endpoint implemented and tested.
- **Phase 3 (Data Integrity):** 🚧 In Progress. Purging mocks and loading real data.

## Phase 3: Data Integrity - No Mock Policy
- **Goal:** Use real production data for all tests.
- **Actions:**
    - [ ] Purge `dummy_tweets` fixtures.
    - [ ] Purge `mock_geo` fixtures.
    - [ ] Remove placeholder data (e.g., "Lorem Ipsum").
    - [ ] Load `parsed_tweets_gemini_parser_v2.jsonl`.
    - [ ] Load `chhattisgarh_urban.ndjson`.
    - [ ] Validate against `gold_standard_tweets.csv`.

## Phase 4: Authorized Skips
- Only 26 files (library internals/aspirational) allowed to be skipped.

## Success Criteria
- ✅ 0 Failed Tests
- ✅ 26 Authorized Skips
- ✅ ~350+ Passing Tests (Current: 353)
- ✅ Performance >50fps
- ✅ Real data only
