# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

##  [Unreleased]

##  [0.3.0] - 2026-06-26

### Added
- `pyproject.toml` configuration to manage packaging, dependencies, and settings for static analysis and linting.
- `.github/dependabot.yml` to run weekly security and version update checks on pip and GitHub Actions dependencies.

### Changed
- Bumped target Python environment to `3.14` (Ruff and `pyproject.toml`).
- Replaced legacy `setup.py` and `mypy.ini` configurations.
- Converted alternative constructors (`from_stream`) in `Keyblock` and `KeytabEntry` to class methods (`@classmethod`) with PEP 673 `Self` return types.
- Modernized codebase style: replaced older formatting patterns with f-strings, cleaned up backslash line continuations, and adopted the `datetime.UTC` alias.
- Modernized GitHub Actions test workflow (`python-test.yml`) and publish workflow (`python-publish.yml`) to use pip caching, install dependencies in virtual environments (via `.[dev]`), lint with `ruff`, and publish distribution assets directly to GitHub Releases.

### Fixed
- Fixed Windows-specific datetime epoch constructor bugs (`OSError`).
- Fixed concurrent file-locking permission issues in keytab unit tests on Windows using `tempfile.TemporaryDirectory`.

##  [0.2.0] - 2024-12-19

### Added

- Support for storing multiple GMSAs secrets in a single keytab file (#5)
- Print Kerberos error names (#7)
- Fix salt retrieval with aes128-cts-hmac-sha1-96 (#8)
- Handle server without WhoAmI and allow to specify ldap auto_bind parameter (#9)

## [0.1.0] - 2023-06-05

Initial commit
