#!/usr/bin/env python3
"""Make a blinded review packet from two complete, verbatim answer sets."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import sys

LIMIT = 2 * 1024 * 1024


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


def main(argv=None):
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
            "manifest.json": {"cases_sha256": case_hash, "first_sha256": first_hash,
                              "second_sha256": second_hash,
                              "method": "Independent random A/B order per case; preserve key to reproduce assignment."},
        }
        for name, value in artifacts.items():
            with (args.output / name).open("x", encoding="utf-8") as stream:
                json.dump(value, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
        print("Created blind.json. Give only that file and your predeclared rubric to the reviewer.")
        print("Keep key.json and lengths.json hidden until ratings are complete. Review content for privacy before sharing.")
        return 0
    except (OSError, ValueError, UnicodeError) as error:
        print(f"Cannot prepare review: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
