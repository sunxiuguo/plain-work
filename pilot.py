#!/usr/bin/env python3
"""Make a blinded review packet from two complete, verbatim answer sets."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import re
import secrets
import sys

LIMIT = 2 * 1024 * 1024
REVIEW_SCHEMA = 1
OUTPUT_LIMIT = 16 * 1024 * 1024
REVIEW_FILES = {"blind.json", "key.json", "lengths.json", "review-receipt.json"}


def unique_object(pairs):
    """Reject ambiguous JSON instead of silently dropping an earlier value."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object fields are not allowed.")
        result[key] = value
    return result


def read_records(path: Path, field: str) -> tuple[list[dict], str]:
    with path.open("rb") as stream:
        raw = stream.read(LIMIT + 1)
    if len(raw) > LIMIT:
        raise ValueError("Input exceeds 2 MiB.")
    data = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object)
    if not isinstance(data, list) or not data:
        raise ValueError("Expected a nonempty JSON list.")
    seen = set()
    for item in data:
        if (not isinstance(item, dict) or not isinstance(item.get("id"), str)
                or not item["id"] or not isinstance(item.get(field), str)
                or not item[field].strip()):
            raise ValueError(f"Each record needs nonempty string id and {field}.")
        if item["id"] in seen:
            raise ValueError("Duplicate case IDs are not allowed.")
        seen.add(item["id"])
    return data, hashlib.sha256(raw).hexdigest()


def blind(cases: list[dict], first: list[dict], second: list[dict], rng=None):
    ids = {case["id"] for case in cases}
    if {row["id"] for row in first} != ids or {row["id"] for row in second} != ids:
        raise ValueError("Both answer sets must cover every case exactly; no omissions or extras.")
    by_arm = [{row["id"]: row["answer"] for row in arm} for arm in (first, second)]
    rng = rng or random.SystemRandom()
    packet, key, lengths = [], [], []
    for case in cases:
        order = [0, 1]
        rng.shuffle(order)
        answers = {letter: by_arm[arm][case["id"]] for letter, arm in zip("AB", order)}
        packet.append({"id": case["id"], "prompt": case["prompt"], **answers})
        key.append({"id": case["id"], "A": "first" if order[0] == 0 else "second",
                    "B": "first" if order[1] == 0 else "second"})
        lengths.append({"id": case["id"], "first_unicode_characters": len(by_arm[0][case["id"]]),
                        "second_unicode_characters": len(by_arm[1][case["id"]])})
    return packet, key, lengths


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(64 * 1024), b""):
            size += len(chunk)
            if size > OUTPUT_LIMIT:
                raise ValueError(f"{path.name} exceeds the review artifact limit.")
            digest.update(chunk)
    return digest.hexdigest()


def review_object(path: Path) -> dict:
    with path.open("rb") as stream:
        raw = stream.read(LIMIT + 1)
    if len(raw) > LIMIT:
        raise ValueError("Review metadata exceeds 2 MiB.")
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object)
    if not isinstance(value, dict):
        raise ValueError("Review metadata must be an object.")
    return value


def matches_hex(value, length: int) -> bool:
    return isinstance(value, str) and re.fullmatch(f"[0-9a-f]{{{length}}}", value) is not None


def verify_review(directory: Path, returning: Path) -> None:
    manifest = review_object(directory / "manifest.json")
    if type(manifest.get("schema_version")) is not int or manifest["schema_version"] != REVIEW_SCHEMA:
        raise ValueError("Unbound or unsupported review manifest.")
    run_id = manifest.get("run_id")
    expected = manifest.get("output_sha256")
    if (not matches_hex(run_id, 32) or not isinstance(expected, dict)
            or expected.keys() != REVIEW_FILES
            or not all(matches_hex(digest, 64) for digest in expected.values())):
        raise ValueError("Invalid review manifest.")
    for name in sorted(REVIEW_FILES):
        if digest_file(directory / name) != expected[name]:
            raise ValueError(f"Review artifact differs: {name}.")
    actual_receipt = review_object(directory / "review-receipt.json")
    returned_receipt = review_object(returning)
    receipt = {"schema_version": REVIEW_SCHEMA, "run_id": run_id,
               "blind_sha256": expected["blind.json"]}
    for value in (actual_receipt, returned_receipt):
        if type(value.get("schema_version")) is not int or value != receipt:
            raise ValueError("Receipt does not match the reviewed packet.")


def verify_main(argv) -> int:
    parser = argparse.ArgumentParser(prog="pilot.py verify-review",
                                     description="Verify the exact packet and returned receipt before unblinding.")
    parser.add_argument("directory", type=Path)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        verify_review(args.directory, args.receipt)
    except (OSError, ValueError, UnicodeError) as error:
        print(f"Cannot verify review: {error}", file=sys.stderr)
        return 2
    print("Review receipt and local packet match. This does not establish review quality.")
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["verify-review"]:
        return verify_main(argv[1:])
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--first", type=Path, required=True)
    parser.add_argument("--second", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="New directory; must not exist")
    args = parser.parse_args(argv)
    try:
        cases, case_hash = read_records(args.cases, "prompt")
        first, first_hash = read_records(args.first, "answer")
        second, second_hash = read_records(args.second, "answer")
        packet, key, lengths = blind(cases, first, second)
        args.output.mkdir(parents=False, exist_ok=False, mode=0o700)
        artifacts = {
            "blind.json": packet,
            "key.json": key,
            "lengths.json": {"unit": "Unicode code points, not tokens, money or quality", "cases": lengths},
        }
        for name, value in artifacts.items():
            with (args.output / name).open("x", encoding="utf-8") as stream:
                json.dump(value, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
        run_id = secrets.token_hex(16)  # Reviewer-visible and independent of the A/B assignment.
        receipt = {"schema_version": REVIEW_SCHEMA, "run_id": run_id,
                   "blind_sha256": digest_file(args.output / "blind.json")}
        manifest = {"schema_version": REVIEW_SCHEMA, "run_id": run_id,
                    "cases_sha256": case_hash, "first_sha256": first_hash,
                    "second_sha256": second_hash,
                    "method": "Independent random A/B order per case; preserve key to reproduce assignment."}
        with (args.output / "review-receipt.json").open("x", encoding="utf-8") as stream:
            json.dump(receipt, stream, indent=2)
            stream.write("\n")
        manifest["output_sha256"] = {name: digest_file(args.output / name) for name in sorted(REVIEW_FILES)}
        with (args.output / "manifest.json").open("x", encoding="utf-8") as stream:
            json.dump(manifest, stream, indent=2)
            stream.write("\n")
        print("Share only blind.json, review-receipt.json, and the predeclared rubric; verify returned receipt before unblinding.")
        print("Keep the key, lengths and manifest private until ratings are complete. Check packet content for privacy.")
        return 0
    except (OSError, ValueError, UnicodeError) as error:
        print(f"Cannot prepare review: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
