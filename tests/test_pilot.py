import contextlib
import io
import json
from pathlib import Path
import random
import tempfile
import unittest

import pilot


class PilotTests(unittest.TestCase):
    def test_blinding_preserves_every_answer(self):
        cases = [{"id": str(i), "prompt": f"Question {i}"} for i in range(10)]
        first = [{"id": str(i), "answer": f"First {i}"} for i in range(10)]
        second = [{"id": str(i), "answer": f"Second {i}"} for i in range(10)]
        packet, key, lengths = pilot.blind(cases, first, second, random.Random(42))
        for i, (pair, mapping) in enumerate(zip(packet, key)):
            for label in ("A", "B"):
                expected = first if mapping[label] == "first" else second
                self.assertEqual(pair[label], expected[i]["answer"])
        self.assertEqual(len(packet), 10)
        self.assertEqual(lengths[0]["first_unicode_characters"], 7)
        self.assertEqual({row["A"] for row in key}, {"first", "second"})

    def test_missing_or_extra_case_rejected(self):
        cases = [{"id": "1", "prompt": "question"}]
        complete = [{"id": "1", "answer": "yes"}]
        for incomplete in ([], complete + [{"id": "2", "answer": "extra"}]):
            with self.assertRaises(ValueError):
                pilot.blind(cases, complete, incomplete)

    def test_records_reject_duplicate_empty_and_invalid_inputs(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "input.json"
            for data in ([], {}, [{"id": "a", "answer": ""}],
                         [{"id": "a", "answer": "one"}, {"id": "a", "answer": "two"}]):
                path.write_text(json.dumps(data))
                with self.subTest(data=data), self.assertRaises(ValueError):
                    pilot.read_records(path, "answer")

    def test_cli_writes_packet_without_overwriting_existing_directory(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            inputs = {"cases": [{"id": "1", "prompt": "问"}],
                      "first": [{"id": "1", "answer": "答一"}],
                      "second": [{"id": "1", "answer": "答二"}]}
            args = []
            for name, content in inputs.items():
                path = root / (name + ".json")
                path.write_text(json.dumps(content), encoding="utf-8")
                args.extend(["--" + name, str(path)])
            output = root / "review"
            args.extend(["--output", str(output)])
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(pilot.main(args), 0)
                before = (output / "blind.json").read_bytes()
                self.assertEqual(pilot.main(args), 2)
            self.assertEqual((output / "blind.json").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
