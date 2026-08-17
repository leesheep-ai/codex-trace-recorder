from __future__ import annotations

# SPDX-License-Identifier: MIT

import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PLUGIN_ROOT / "scripts" / "trace_recorder.py"


class TraceRecorderTests(unittest.TestCase):
    def invoke(self, payload: dict, trace_root: Path) -> subprocess.CompletedProcess[bytes]:
        environment = os.environ.copy()
        environment["CODEX_TRACE_DIR"] = str(trace_root)
        return subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=json.dumps(payload).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environment,
            check=False,
        )

    def test_main_transcript_is_byte_identical_and_content_addressed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_name:
            temporary = Path(temporary_name)
            source = temporary / "rollout.jsonl"
            raw = b'{"type":"message","text":"a\\r\\n\\x00\\xff"}\r\n' + bytes(range(256))
            source.write_bytes(raw)

            result = self.invoke(
                {
                    "session_id": "thr_123",
                    "transcript_path": str(source),
                    "hook_event_name": "Stop",
                },
                temporary / "archive",
            )

            self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
            self.assertEqual(json.loads(result.stdout), {"continue": True})
            latest = temporary / "archive" / "thr_123" / "main" / "transcript.jsonl"
            digest = hashlib.sha256(raw).hexdigest()
            checkpoint = latest.parent / "checkpoints" / f"{digest}.jsonl"
            self.assertEqual(latest.read_bytes(), raw)
            self.assertEqual(checkpoint.read_bytes(), raw)

    def test_new_content_keeps_the_previous_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_name:
            temporary = Path(temporary_name)
            source = temporary / "rollout.jsonl"
            trace_root = temporary / "archive"
            first = b'{"step":1}\n'
            second = first + b'{"step":2}\n'
            payload = {
                "session_id": "thr_update",
                "transcript_path": str(source),
                "hook_event_name": "Stop",
            }

            source.write_bytes(first)
            self.assertEqual(self.invoke(payload, trace_root).returncode, 0)
            source.write_bytes(second)
            self.assertEqual(self.invoke(payload, trace_root).returncode, 0)

            main = trace_root / "thr_update" / "main"
            self.assertEqual((main / "transcript.jsonl").read_bytes(), second)
            self.assertEqual(
                (main / "checkpoints" / f"{hashlib.sha256(first).hexdigest()}.jsonl").read_bytes(),
                first,
            )
            self.assertEqual(
                (main / "checkpoints" / f"{hashlib.sha256(second).hexdigest()}.jsonl").read_bytes(),
                second,
            )

    def test_subagent_uses_agent_transcript_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_name:
            temporary = Path(temporary_name)
            main_source = temporary / "main.jsonl"
            agent_source = temporary / "agent.jsonl"
            main_source.write_bytes(b"main")
            agent_source.write_bytes(b"agent-raw")

            result = self.invoke(
                {
                    "session_id": "thr_agents",
                    "transcript_path": str(main_source),
                    "agent_transcript_path": str(agent_source),
                    "agent_id": "agent/one",
                    "hook_event_name": "SubagentStop",
                },
                temporary / "archive",
            )

            self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
            saved = temporary / "archive" / "thr_agents" / "subagents" / "agent_one" / "transcript.jsonl"
            self.assertEqual(saved.read_bytes(), b"agent-raw")

    @unittest.skipUnless(os.name == "posix", "POSIX directory permissions only")
    def test_archive_directory_tree_is_private(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_name:
            temporary = Path(temporary_name)
            source = temporary / "agent.jsonl"
            source.write_bytes(b"agent-raw")
            trace_root = temporary / "archive"
            session = trace_root / "thr_permissions"
            session.mkdir(parents=True)
            trace_root.chmod(0o755)
            session.chmod(0o755)

            result = self.invoke(
                {
                    "session_id": "thr_permissions",
                    "agent_transcript_path": str(source),
                    "agent_id": "agent-one",
                    "hook_event_name": "SubagentStop",
                },
                trace_root,
            )

            self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
            agent = session / "subagents" / "agent-one"
            directories = [trace_root, session, session / "subagents", agent, agent / "checkpoints"]
            for directory in directories:
                with self.subTest(directory=directory):
                    self.assertEqual(stat.S_IMODE(directory.stat().st_mode), 0o700)

    def test_missing_transcript_warns_but_does_not_block_stop(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_name:
            temporary = Path(temporary_name)
            result = self.invoke(
                {
                    "session_id": "thr_missing",
                    "transcript_path": str(temporary / "missing.jsonl"),
                    "hook_event_name": "Stop",
                },
                temporary / "archive",
            )
            output = json.loads(result.stdout)
            self.assertEqual(result.returncode, 0)
            self.assertTrue(output["continue"])
            self.assertIn("could not save", output["systemMessage"])

    def test_session_end_failure_is_reported_as_hook_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_name:
            temporary = Path(temporary_name)
            result = self.invoke(
                {
                    "session_id": "thr_missing",
                    "transcript_path": str(temporary / "missing.jsonl"),
                    "hook_event_name": "SessionEnd",
                },
                temporary / "archive",
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn(b"could not save", result.stderr)


if __name__ == "__main__":
    unittest.main()
