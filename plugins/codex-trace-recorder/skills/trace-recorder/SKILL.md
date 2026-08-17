---
name: trace-recorder
description: Explain, locate, configure, or verify raw Codex trace archives produced by Codex Trace Recorder. Use when the user asks where traces are saved, whether traces are transformed, how main and subagent traces are organized, or how to change the archive directory.
---

# Codex Trace Recorder

This plugin records automatically through lifecycle hooks. Do not reconstruct a trace from chat text and do not convert the trace to another schema.

## Storage

The default archive root is `~/.codex/trace-archive`. If the `CODEX_TRACE_DIR` environment variable is set for the Codex process, use that directory instead.

Each session is stored under `<archive-root>/<session-id>/`:

- `main/transcript.jsonl` is the latest byte-for-byte main-thread transcript.
- `main/checkpoints/<sha256>.jsonl` contains a content-addressed main-thread checkpoint.
- `subagents/<agent-id>/transcript.jsonl` is the latest raw subagent transcript.
- `subagents/<agent-id>/checkpoints/<sha256>.jsonl` contains a content-addressed subagent checkpoint.

The extension follows the source transcript. The recorder never parses, normalizes, redacts, reshapes, or re-serializes transcript contents.

“Complete” refers to the full transcript file exposed by Codex. Do not claim that the archive includes private server-side data or hidden model state that Codex did not write to that file.

## Verification

When asked to verify a saved trace, compare the source and archived file as bytes or compare their SHA-256 digests. Do not load and rewrite JSONL just to validate it.

Checkpoints are content-addressed and the recorder does not modify an existing checkpoint. The local archive is not tamper-resistant against a user or process that can write its files.

## Operational notes

- `Stop` updates the main trace after each completed turn.
- `PreCompact` saves a checkpoint before context compaction.
- `SessionEnd` performs a final main-thread save.
- `SubagentStop` saves the subagent transcript separately.
- Full traces can contain prompts, tool inputs and outputs, source excerpts, paths, and secrets. Keep the archive private.
- Plugin hooks must be reviewed and trusted in `/hooks` after installation or after their definition changes.
