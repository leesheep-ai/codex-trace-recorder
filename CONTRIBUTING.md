# Contributing

Thank you for helping improve Codex Trace Recorder.

## Scope

Changes should preserve the project's central contract: transcript content is
copied byte-for-byte without parsing, normalization, redaction, or format
conversion.

## Development setup

1. Install Python 3.10 or later.
2. Fork and clone the repository.
3. Create a focused branch from `main`.
4. Run the test suite before and after your change:

   ```powershell
   python -m unittest discover -s plugins/codex-trace-recorder/tests -v
   ```

The runtime intentionally uses only the Python standard library.

## Pull requests

- Keep each pull request focused on one coherent change.
- Explain the motivation, behavior change, and verification performed.
- Add or update tests for observable behavior changes.
- Update `CHANGELOG.md` for user-visible changes.
- Do not commit trace archives, credentials, tokens, personal paths, or other
  sensitive data.
- Use clear commit subjects in the imperative mood, for example:
  `Preserve source suffixes in checkpoints`.

## Compatibility

Keep Windows, macOS, and Linux hook commands working. New Python syntax must
remain compatible with Python 3.10 or later.

## Licensing

By submitting a contribution, you agree that it may be distributed under the
repository's [MIT License](LICENSE).

## Security reports

Do not report vulnerabilities in a public issue. Follow
[SECURITY.md](SECURITY.md).
