# Security Policy

## Supported versions

Security fixes are applied to the latest release on the `main` branch.

| Version | Supported |
| --- | --- |
| 0.1.x | Yes |
| Earlier versions | No |

## Reporting a vulnerability

Use GitHub's private vulnerability reporting feature from the repository's
**Security** tab. Do not include sensitive trace data in a public issue.

If private reporting is unavailable, open a minimal issue requesting a private
contact channel without including exploit details, credentials, transcripts,
or personal data.

Useful reports include:

- affected version and platform;
- impact and prerequisites;
- minimal reproduction steps using synthetic data;
- suggested remediation, if known.

## Sensitive-data model

The recorder intentionally preserves raw transcript bytes. It does not redact
secrets, paths, prompts, source excerpts, or tool output. Users are responsible
for archive permissions, retention, backup, and disclosure controls.
