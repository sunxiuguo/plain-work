import contextlib
import hashlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import pilot


class PacketIdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        rows = [{"id": "1", "answer": "Identical approved fixture answer."}]
        for name, obj in (("cases", [{"id": "1", "prompt": "Synthetic question."}]),
                          ("first", rows), ("second", rows)):
            (self.root / f"{name}.json").write_text(json.dumps(obj), encoding="utf-8")
        self.first = self.prepare("first-packet", reverse=False)
        self.second = self.prepare("second-packet", reverse=True)
        self.receipt = self.root / "returned-receipt.json"
        shutil.copyfile(self.first / "review-receipt.json", self.receipt)

    def prepare(self, name, reverse):
        folder = self.root / name
        args = [item for name in ("cases", "first", "second")
                for item in (f"--{name}", str(self.root / f"{name}.json"))]
        with patch("pilot.random.SystemRandom") as mock_rng:
            mock_rng.return_value.shuffle.side_effect = lambda values: values.reverse() if reverse else None
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(pilot.main([*args, "--output", str(folder)]), 0)
        return folder

    def verify(self, folder):
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            result = pilot.main(["verify-review", str(folder), "--receipt", str(self.receipt)])
        return result, output.getvalue(), error.getvalue()

    def test_returned_receipt_binds_unchanged_packet(self):
        before = {p.name: p.read_bytes() for p in self.first.iterdir()}
        receipt = json.loads(self.receipt.read_bytes())
        self.assertEqual(set(receipt), {"run_id", "schema_version", "blind_sha256"})
        self.assertEqual(receipt["blind_sha256"], hashlib.sha256(before["blind.json"]).hexdigest())
        code, output, error = self.verify(self.first)
        self.assertEqual(code, 0)
        self.assertIn("match", output)
        self.assertEqual(error, "")
        self.assertEqual({p.name: p.read_bytes() for p in self.first.iterdir()}, before)

    def test_same_visible_text_opposite_order_cannot_pass_with_another_run(self):
        self.assertEqual((self.first / "blind.json").read_bytes(), (self.second / "blind.json").read_bytes())
        self.assertNotEqual((self.first / "key.json").read_bytes(), (self.second / "key.json").read_bytes())
        f = json.loads((self.first / "review-receipt.json").read_bytes())
        s = json.loads((self.second / "review-receipt.json").read_bytes())
        self.assertEqual(f["blind_sha256"], s["blind_sha256"])
        self.assertNotEqual(f["run_id"], s["run_id"])
        code, output, error = self.verify(self.second)
        self.assertEqual(code, 2)
        self.assertIn("Receipt does not match", error)
        self.assertEqual(output, "")

    def test_stale_key_rejected_in_otherwise_matching_packet(self):
        shutil.copyfile(self.second / "key.json", self.first / "key.json")
        code, _, error = self.verify(self.first)
        self.assertEqual(code, 2)
        self.assertIn("Review artifact differs: key.json", error)

    def test_changed_visible_packet_rejected(self):
        with (self.first / "blind.json").open("ab") as stream:
            stream.write(b" ")
        code, _, error = self.verify(self.first)
        self.assertEqual(code, 2)
        self.assertIn("Review artifact differs: blind.json", error)

    def test_legacy_manifest_is_not_verified(self):
        p = self.first / "manifest.json"
        wanted = ("cases_sha256", "first_sha256", "second_sha256", "method")
        data = json.loads(p.read_bytes())
        p.write_text(json.dumps({key: data[key] for key in wanted}), encoding="utf-8")
        code, _, error = self.verify(self.first)
        self.assertEqual(code, 2)
        self.assertIn("Unbound or unsupported", error)

    def test_ambiguous_returned_receipt_rejected(self):
        raw = self.receipt.read_text()
        self.receipt.write_text(raw.replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1'))
        code, _, error = self.verify(self.first)
        self.assertEqual(code, 2)
        self.assertIn("Duplicate JSON object fields", error)


if __name__ == "__main__":
    unittest.main()
