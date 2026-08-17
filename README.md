# Codex Trace Recorder

[![CI](https://github.com/leesheep-ai/codex-trace-recorder/actions/workflows/ci.yml/badge.svg)](https://github.com/leesheep-ai/codex-trace-recorder/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

[简体中文](README.zh-CN.md)

Codex Trace Recorder is a local Codex plugin that archives complete transcript
files without format conversion. It preserves the raw file exposed by Codex
lifecycle hooks and keeps content-addressed checkpoints for the main thread and
subagents.

## Design guarantees

- **Byte-preserving:** transcript content is copied as bytes and never decoded
  or re-serialized.
- **No schema dependency:** the recorder does not depend on the internal JSONL
  event schema.
- **Checkpointed:** every distinct transcript version is stored under its
  SHA-256 digest.
- **Main thread and subagents:** `Stop`, `PreCompact`, `SessionEnd`, and
  `SubagentStop` are covered.
- **Local only:** the recorder performs no network requests.

> [!IMPORTANT]
> “Complete” means every byte in the transcript file Codex exposes to the hook.
> The plugin cannot capture server-side data or hidden model state that Codex
> did not write to that file.

## Repository layout

```text
.agents/plugins/marketplace.json
plugins/codex-trace-recorder/
  .codex-plugin/plugin.json
  hooks/hooks.json
  scripts/trace_recorder.py
  skills/trace-recorder/SKILL.md
  tests/test_trace_recorder.py
```

## Install

### From this GitHub marketplace

Register this repository as a Codex plugin marketplace:

```powershell
codex plugin marketplace add leesheep-ai/codex-trace-recorder
```

Restart the Codex desktop app, open the Plugins directory, install and enable
**Codex Trace Recorder** from the `codex-trace-recorder` marketplace, then open
`/hooks` to review and trust the plugin hooks. Start a new task after enabling
the plugin.

### From a local clone

```powershell
git clone https://github.com/leesheep-ai/codex-trace-recorder.git
cd codex-trace-recorder
codex plugin marketplace add .
```

Then install and enable **Codex Trace Recorder** from the local marketplace in
the Codex desktop app's Plugins directory and review `/hooks` before use.

Plugin command hooks are intentionally subject to Codex's hook trust review.
Do not bypass that review for an uninspected checkout.

## Usage

No prompt is required. Once enabled and trusted, the plugin records
automatically:

| Event | Archive action |
| --- | --- |
| `Stop` | Updates the main transcript after a completed turn |
| `PreCompact` | Saves the raw transcript before compaction |
| `SessionEnd` | Performs the final main-thread save |
| `SubagentStop` | Saves the subagent transcript separately |

The default archive root is:

```text
~/.codex/trace-archive
```

Set `CODEX_TRACE_DIR` in the environment that launches Codex to override it.

```text
<archive-root>/<session-id>/
  main/
    transcript.jsonl
    checkpoints/<sha256>.jsonl
  subagents/<agent-id>/
    transcript.jsonl
    checkpoints/<sha256>.jsonl
```

Inspect saved files in PowerShell:

```powershell
Get-ChildItem "$HOME\.codex\trace-archive" -Recurse -File
```

## Development

Requirements:

- Python 3.10+
- No third-party runtime dependencies

Run the tests:

```powershell
python -m unittest discover -s plugins/codex-trace-recorder/tests -v
```

The tests verify byte identity, content-addressed checkpoint retention,
subagent routing, archive directory permissions on POSIX, and failure behavior.

See [CONTRIBUTING.md](CONTRIBUTING.md) before submitting changes. Security
issues should follow [SECURITY.md](SECURITY.md).

## Privacy and security

Raw transcripts may contain prompts, responses, reasoning summaries, tool
arguments and results, source excerpts, local paths, and secrets. The plugin
does not redact anything because its purpose is exact preservation.

The recorder best-effort applies private POSIX-style permissions to archive
directories and saved files. These modes do not replace Windows ACL policy or
other operating-system access controls.

Use a private archive location, restrict filesystem access, and define an
appropriate retention policy. Do not publish trace archives without reviewing
their contents.

## License

Copyright (c) 2026 leesheep-ai.

Licensed under the [MIT License](LICENSE). Contributions are accepted under
the same license unless explicitly stated otherwise.
