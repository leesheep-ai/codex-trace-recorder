# Codex Trace Recorder

Codex Trace Recorder archives the transcript files exposed by Codex lifecycle
hooks without changing their contents.

The recorder copies each source as bytes. It does not parse JSONL, normalize
messages, redact fields, construct training rows, or convert to another format.

## Captured lifecycle events

- `Stop`: update the main-thread archive after each completed turn.
- `PreCompact`: preserve a checkpoint before context compaction.
- `SessionEnd`: perform the final main-thread save.
- `SubagentStop`: archive each subagent transcript separately.

## Storage

The default archive root is `~/.codex/trace-archive`. Set `CODEX_TRACE_DIR` in
the environment that launches Codex to use another directory.

```text
<archive-root>/<session-id>/
  main/
    transcript.jsonl
    checkpoints/<sha256>.jsonl
  subagents/<agent-id>/
    transcript.jsonl
    checkpoints/<sha256>.jsonl
```

`transcript.jsonl` is the latest byte-identical copy. Each distinct version is
also retained under `checkpoints/` using its SHA-256 digest as the filename.
The extension follows the source transcript.

“Complete” means every byte in the transcript file Codex exposes to the hook.
The plugin cannot capture server-side data or hidden model state absent from
that file.

## Requirements

- Codex with lifecycle-hook support
- Python 3.10 or later available as `python` on Windows or `python3` on macOS
  and Linux

## Security

Raw transcripts can contain prompts, model responses, tool inputs and outputs,
source excerpts, local paths, and secrets. This plugin deliberately performs no
redaction because redaction would change the trace. Protect the archive with
appropriate filesystem permissions and retention controls.

The plugin makes no network requests.

## License

Released under the [MIT License](LICENSE).

The source repository is
[leesheep-ai/codex-trace-recorder](https://github.com/leesheep-ai/codex-trace-recorder).
