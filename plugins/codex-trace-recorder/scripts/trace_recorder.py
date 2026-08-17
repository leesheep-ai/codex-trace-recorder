#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Archive Codex transcript files byte-for-byte.

The hook payload is used only to locate and name a transcript. Transcript
contents are never decoded, parsed, normalized, redacted, or re-serialized.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, BinaryIO


BUFFER_SIZE = 1024 * 1024
SAFE_COMPONENT = re.compile(r"[^A-Za-z0-9._-]+")
JSON_OUTPUT_EVENTS = {"PreCompact", "PostCompact", "SubagentStop", "Stop"}


class RecorderError(RuntimeError):
    """Raised when a requested transcript cannot be archived."""


def safe_component(value: Any, fallback: str) -> str:
    text = str(value or "").strip()
    cleaned = SAFE_COMPONENT.sub("_", text).strip("._-")
    return (cleaned[:180] or fallback)


def archive_root() -> Path:
    configured = os.environ.get("CODEX_TRACE_DIR", "").strip()
    if configured:
        return Path(os.path.expandvars(configured)).expanduser().resolve()
    return (Path.home() / ".codex" / "trace-archive").resolve()


def ensure_private_directory(path: Path) -> None:
    root = archive_root()
    path.mkdir(parents=True, exist_ok=True)

    try:
        relative = path.relative_to(root)
    except ValueError:
        directories = [path]
    else:
        directories = [root]
        current = root
        for part in relative.parts:
            current = current / part
            directories.append(current)

    for directory in directories:
        try:
            directory.chmod(0o700)
        except OSError:
            pass


def copy_and_hash(source: BinaryIO, destination: BinaryIO) -> str:
    digest = hashlib.sha256()
    while True:
        chunk = source.read(BUFFER_SIZE)
        if not chunk:
            break
        destination.write(chunk)
        digest.update(chunk)
    destination.flush()
    os.fsync(destination.fileno())
    return digest.hexdigest()


def make_temp_file(parent: Path, prefix: str) -> tuple[int, Path]:
    descriptor, name = tempfile.mkstemp(prefix=prefix, suffix=".tmp", dir=parent)
    return descriptor, Path(name)


def publish_latest(checkpoint: Path, latest: Path) -> None:
    descriptor, temporary = make_temp_file(latest.parent, ".latest-")
    os.close(descriptor)
    temporary.unlink(missing_ok=True)
    try:
        try:
            os.link(checkpoint, temporary)
        except OSError:
            shutil.copyfile(checkpoint, temporary)
        try:
            temporary.chmod(0o600)
        except OSError:
            pass
        os.replace(temporary, latest)
    finally:
        temporary.unlink(missing_ok=True)


def archive_raw_file(source: Path, target_directory: Path) -> tuple[Path, Path, str]:
    source = source.expanduser().resolve(strict=True)
    if not source.is_file():
        raise RecorderError(f"transcript is not a regular file: {source}")

    ensure_private_directory(target_directory)
    checkpoints = target_directory / "checkpoints"
    ensure_private_directory(checkpoints)

    suffix = "".join(source.suffixes) or ".raw"
    latest = target_directory / f"transcript{suffix}"
    descriptor, temporary = make_temp_file(target_directory, ".capture-")
    try:
        with source.open("rb") as reader, os.fdopen(descriptor, "wb") as writer:
            digest = copy_and_hash(reader, writer)
        try:
            temporary.chmod(0o600)
        except OSError:
            pass

        checkpoint = checkpoints / f"{digest}{suffix}"
        if checkpoint.exists():
            temporary.unlink(missing_ok=True)
        else:
            os.replace(temporary, checkpoint)
        publish_latest(checkpoint, latest)
        return latest, checkpoint, digest
    finally:
        temporary.unlink(missing_ok=True)


def select_transcript(payload: dict[str, Any]) -> tuple[Path | None, Path]:
    session_id = safe_component(payload.get("session_id"), "unknown-session")
    session_directory = archive_root() / session_id

    if payload.get("hook_event_name") == "SubagentStop":
        raw_path = payload.get("agent_transcript_path")
        agent_id = safe_component(payload.get("agent_id"), "unknown-agent")
        return (Path(raw_path) if raw_path else None), session_directory / "subagents" / agent_id

    raw_path = payload.get("transcript_path")
    return (Path(raw_path) if raw_path else None), session_directory / "main"


def success_output(event_name: str) -> None:
    if event_name in JSON_OUTPUT_EVENTS:
        print(json.dumps({"continue": True}, separators=(",", ":")))


def warning_output(event_name: str, message: str) -> None:
    if event_name in JSON_OUTPUT_EVENTS:
        print(
            json.dumps(
                {"continue": True, "systemMessage": message},
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
    else:
        print(message, file=sys.stderr)


def run_hook(payload: dict[str, Any]) -> int:
    event_name = str(payload.get("hook_event_name") or "")
    try:
        source, target_directory = select_transcript(payload)
        if source is None:
            success_output(event_name)
            return 0
        archive_raw_file(source, target_directory)
    except (OSError, RecorderError, ValueError) as exc:
        warning_output(event_name, f"Codex Trace Recorder could not save the raw trace: {exc}")
        return 1 if event_name == "SessionEnd" else 0

    success_output(event_name)
    return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"Codex Trace Recorder received invalid hook JSON: {exc}", file=sys.stderr)
        return 1
    if not isinstance(payload, dict):
        print("Codex Trace Recorder expected one JSON object on stdin.", file=sys.stderr)
        return 1
    return run_hook(payload)


if __name__ == "__main__":
    raise SystemExit(main())
