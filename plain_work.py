#!/usr/bin/env python3
"""Preview, append or remove a small project-local instruction block. No network."""
from __future__ import annotations

import argparse
import difflib
import hashlib
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
START = b"<!-- plain-work:start -->"
END = b"<!-- plain-work:end -->"
MAX_BYTES = 1024 * 1024


def block(language: str) -> bytes:
    text = (ROOT / "prompts" / f"plain-work.{language}.md").read_bytes().rstrip(b"\n")
    return b"\n\n" + START + b"\n" + text + b"\n" + END + b"\n"


def transform(original: bytes, action: str, language: str = "zh") -> bytes:
    original.decode("utf-8")
    has_marker = START in original or END in original
    choices = [block(lang) for lang in ("zh", "en")]
    exact = [part for part in choices if original.count(part) == 1]
    if has_marker:
        if original.count(START) != 1 or original.count(END) != 1 or len(exact) != 1:
            raise ValueError("The managed block was changed or duplicated; review it manually.")
        if action == "remove":
            return original.replace(exact[0], b"", 1)
        if exact[0] != block(language):
            raise ValueError("A different language is installed. Remove it before switching.")
        return original
    if action == "remove":
        return original
    return original + block(language)


def read_target(path: Path) -> tuple[bytes, int]:
    if path.is_symlink():
        raise ValueError("Refusing to replace a symlink.")
    if not path.exists():
        return b"", 0o644
    if not path.is_file():
        raise ValueError("Target must be a regular file.")
    with path.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Target exceeds the 1 MiB instruction-file limit.")
    return data, path.stat().st_mode & 0o777


def write_change(path: Path, before: bytes, after: bytes, mode: int) -> Path:
    """Keep the original bytes, then atomically replace a single local file.

    Single-writer utility, not a lock or a security boundary. Do not edit the
    target concurrently. The final re-read catches ordinary stale previews.
    """
    if not path.parent.is_dir():
        raise ValueError("The target directory must already exist.")
    backup_dir = path.parent / ".plain-work-backups"
    if backup_dir.is_symlink():
        raise ValueError("Refusing a symlink backup directory.")
    backup_dir.mkdir(mode=0o700, exist_ok=True)
    backup = backup_dir / (hashlib.sha256(before).hexdigest() + ".bak")
    try:
        fd = os.open(backup, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        if backup.is_symlink() or not backup.is_file() or backup.read_bytes() != before:
            raise ValueError("Existing backup does not match the original bytes.")
    else:
        with os.fdopen(fd, "wb") as stream:
            stream.write(before)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temp_name = stream.name
            stream.write(after)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp_name, mode)
        current, _ = read_target(path)
        if current != before:
            raise ValueError("The target changed during this operation; no replacement made.")
        os.replace(temp_name, path)
        temp_name = None
    finally:
        if temp_name is not None:
            os.unlink(temp_name)
    return backup


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("show", "add", "remove"))
    parser.add_argument("--language", choices=("zh", "en"), default="zh")
    parser.add_argument("--path", type=Path, help="Explicit project-local instruction file")
    parser.add_argument("--apply", action="store_true", help="Write the previewed kind of change")
    args = parser.parse_args(argv)
    if args.action == "show":
        if args.path is not None or args.apply:
            parser.error("show does not accept --path or --apply")
        sys.stdout.write((ROOT / "prompts" / f"plain-work.{args.language}.md").read_text(encoding="utf-8"))
        return 0
    if args.path is None:
        parser.error("add/remove require --path")
    try:
        before, mode = read_target(args.path)
        after = transform(before, args.action, args.language)
        if len(after) > MAX_BYTES:
            raise ValueError("The resulting file would exceed the 1 MiB instruction-file limit.")
        if before == after:
            print("No change.")
            return 0
        if args.apply:
            backup = write_change(args.path, before, after, mode)
            print(f"Updated {args.path}. Original bytes retained in {backup}.")
            print("Backups may contain private instructions. Exclude .plain-work-backups/ from commits and sharing.")
        else:
            diff = difflib.unified_diff(before.decode().splitlines(True),
                                        after.decode().splitlines(True),
                                        fromfile="before", tofile="after")
            sys.stdout.writelines(diff)
            print("\nPreview only. Re-run with --apply to write. Backups are local and may contain private instructions.")
        return 0
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Cannot change instructions: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
