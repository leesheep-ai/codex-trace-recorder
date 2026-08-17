# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Tighten archive directory permissions across the archive root, session, and
  subagent hierarchy on a best-effort basis.
- Align installation instructions with marketplace registration followed by
  installation from the Codex desktop Plugins directory.
- Describe checkpoints as content-addressed rather than tamper-resistant.

### Tests

- Add POSIX regression coverage for correcting permissive archive and session
  directory modes to `0700`.

## [0.1.0] - 2026-08-17

### Added

- Byte-preserving main-thread transcript archival on `Stop`, `PreCompact`, and
  `SessionEnd`.
- Separate subagent transcript archival on `SubagentStop`.
- Content-addressed SHA-256 checkpoints and a stable latest-transcript path.
- Cross-platform Windows and POSIX hook commands.
- Tests for byte identity, checkpoint retention, subagent routing, and failure
  behavior.

[Unreleased]: https://github.com/leesheep-ai/codex-trace-recorder/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/leesheep-ai/codex-trace-recorder/releases/tag/v0.1.0
