# Changelog

All notable changes to Spectra AI will be documented in this file.

The format loosely follows Keep a Changelog and adheres to Semantic Versioning where practical.

## [Unreleased]

### Added
- (none yet)

### Changed
- (none yet)

### Fixed
- (none yet)

## [2.0.1] - 2025-08-09

### Added

- `model_used` field for backward-compatible chat responses.
- UTC timezone-aware timestamps across all API responses.
- README refactor with professional sections & schema documentation.
- CHANGELOG, CONTRIBUTING, CODE_OF_CONDUCT for project professionalism.

### Changed

- Structured logging standardized (JSON / console selectable).
- Metrics endpoint now returns UTC timestamps.

### Fixed

- Pytest import path stabilization via `conftest.py`.

## [2.0.0] - 2025-08-02

### Added

- FastAPI primary backend initialization.
- Dynamic model selection (context aware: creative / technical / concise).
- Personality hot-reload with hashing.
- Metrics: request counts, avg processing time, failed models tracking.

---

Links:
- 2.0.1: internal (not yet tagged)
- 2.0.0: initial professional baseline snapshot
