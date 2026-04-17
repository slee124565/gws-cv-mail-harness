from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence


@dataclass(frozen=True)
class CompletedCommand:
    args: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


class CommandExecutor(Protocol):
    def __call__(
        self,
        args: Sequence[str],
        *,
        env: Mapping[str, str] | None,
        cwd: Path | None,
        timeout: float | None,
    ) -> CompletedCommand: ...


def extract_json_payload(text: str) -> Any:
    decoder = json.JSONDecoder()
    for index, character in enumerate(text):
        if character not in "[{":
            continue
        try:
            payload, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        return payload
    raise ValueError("No JSON payload found in command output.")


def _subprocess_executor(
    args: Sequence[str],
    *,
    env: Mapping[str, str] | None,
    cwd: Path | None,
    timeout: float | None,
) -> CompletedCommand:
    completed = subprocess.run(
        list(args),
        capture_output=True,
        check=False,
        cwd=str(cwd) if cwd else None,
        env=dict(env) if env else None,
        text=True,
        timeout=timeout,
    )
    return CompletedCommand(
        args=tuple(str(item) for item in args),
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


class GWSCommandError(RuntimeError):
    def __init__(self, command: Sequence[str], returncode: int, stdout: str, stderr: str) -> None:
        self.command = tuple(command)
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        super().__init__(self._build_message())

    def _build_message(self) -> str:
        command_text = " ".join(self.command)
        return f"gws command failed with exit code {self.returncode}: {command_text}"


class GWSCommandRunner:
    def __init__(
        self,
        *,
        binary: str = "gws",
        cwd: Path | None = None,
        env: Mapping[str, str] | None = None,
        timeout: float | None = 30.0,
        executor: CommandExecutor | None = None,
    ) -> None:
        self.binary = binary
        self.cwd = cwd
        self.env = env
        self.timeout = timeout
        self.executor = executor or _subprocess_executor

    def run_json(self, args: Sequence[str]) -> Any:
        command = (self.binary, *args)
        completed = self.executor(
            command,
            env=self.env,
            cwd=self.cwd,
            timeout=self.timeout,
        )
        if completed.returncode != 0:
            raise GWSCommandError(command, completed.returncode, completed.stdout, completed.stderr)

        output = completed.stdout.strip()
        if output:
            return extract_json_payload(output)

        error_output = completed.stderr.strip()
        if error_output:
            return extract_json_payload(error_output)

        raise ValueError(f"Command produced no parseable output: {' '.join(command)}")
