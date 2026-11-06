import contextlib
import io
from pathlib import Path
import tempfile
import unittest

import plain_work as pw


class TransformTests(unittest.TestCase):
    def test_round_trip_exact_bytes(self):
        for content in (b"", b"Existing", b"Existing\n", b"Existing\r\n", "旧规则\n".encode()):
            for language in ("zh", "en"):
                with self.subTest(content=content, language=language):
                    added = pw.transform(content, "add", language)
                    self.assertEqual(pw.transform(added, "remove"), content)

    def test_idempotent(self):
        added = pw.transform(b"rules", "add")
        self.assertEqual(pw.transform(added, "add"), added)
        self.assertEqual(pw.transform(b"rules", "remove"), b"rules")

    def test_preserves_new_surrounding_content(self):
        added = pw.transform(b"first", "add") + b"\nsecond"
        self.assertEqual(pw.transform(added, "remove"), b"first\nsecond")

    def test_refuses_modified_or_duplicate_blocks(self):
        part = pw.block("zh")
        for data in (part + part, part.replace(b"<!-- plain-work:end -->", b"changed"),
                     part.replace("先完成".encode(), "先改变".encode())):
            with self.subTest(data=data), self.assertRaises(ValueError):
                pw.transform(data, "remove")

    def test_language_change_is_explicit(self):
        with self.assertRaises(ValueError):
            pw.transform(pw.transform(b"", "add", "en"), "add", "zh")

    def test_invalid_utf8(self):
        with self.assertRaises(UnicodeDecodeError):
            pw.transform(b"\xff", "add")


class FileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "AGENTS.md"

    def cli(self, *args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return pw.main(list(args))

    def test_preview_does_not_write(self):
        self.assertEqual(self.cli("add", "--path", str(self.path)), 0)
        self.assertFalse(self.path.exists())
        self.assertFalse((self.path.parent / ".plain-work-backups").exists())

    def test_apply_and_remove_preserve_original(self):
        original = b"Original rules\r\n"
        self.path.write_bytes(original)
        self.path.chmod(0o600)
        self.assertEqual(self.cli("add", "--path", str(self.path), "--apply"), 0)
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.cli("remove", "--path", str(self.path), "--apply"), 0)
        self.assertEqual(self.path.read_bytes(), original)
        backups = list((self.path.parent / ".plain-work-backups").glob("*.bak"))
        self.assertTrue(any(path.read_bytes() == original for path in backups))

    def test_symlink_target_rejected(self):
        other = self.path.parent / "other"
        other.write_text("other")
        self.path.symlink_to(other)
        self.assertEqual(self.cli("add", "--path", str(self.path), "--apply"), 2)
        self.assertEqual(other.read_text(), "other")

    def test_symlink_backup_directory_rejected(self):
        other = self.path.parent / "other"
        other.mkdir()
        (self.path.parent / ".plain-work-backups").symlink_to(other)
        self.assertEqual(self.cli("add", "--path", str(self.path), "--apply"), 2)
        self.assertFalse(self.path.exists())

    def test_stale_original_is_not_overwritten(self):
        self.path.write_bytes(b"new")
        with self.assertRaises(ValueError):
            pw.write_change(self.path, b"old", b"replacement", 0o600)
        self.assertEqual(self.path.read_bytes(), b"new")

    def test_oversized_file(self):
        self.path.write_bytes(b"a" * (pw.MAX_BYTES + 1))
        self.assertEqual(self.cli("add", "--path", str(self.path)), 2)

    def test_add_cannot_exceed_its_own_read_limit(self):
        original = b"a" * pw.MAX_BYTES
        self.path.write_bytes(original)
        self.assertEqual(self.cli("add", "--path", str(self.path), "--apply"), 2)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertFalse((self.path.parent / ".plain-work-backups").exists())

    def test_largest_allowed_add_can_be_removed(self):
        original = b"a" * (pw.MAX_BYTES - len(pw.block("zh")))
        self.path.write_bytes(original)
        self.assertEqual(self.cli("add", "--path", str(self.path), "--apply"), 0)
        self.assertEqual(self.path.stat().st_size, pw.MAX_BYTES)
        self.assertEqual(self.cli("remove", "--path", str(self.path), "--apply"), 0)
        self.assertEqual(self.path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
