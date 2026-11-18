import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from schemas.read_file_schema import read_file_schema
from tools.read_file_tool import read_file


class ReadFileTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.path = Path(self.temp_dir.name) / "sample.txt"
        self.resolve_patcher = patch(
            "tools.read_file_tool.resolve_in_project", return_value=self.path
        )
        self.resolve = self.resolve_patcher.start()
        self.addCleanup(self.resolve_patcher.stop)

    def _write(self, content):
        self.path.write_text(content, encoding="utf-8")

    def test_returns_numbered_lines_without_extra_blank_lines_or_lost_indent(self):
        self._write("first\n    indented\nthird\n")

        self.assertEqual(
            read_file("sample.txt"),
            "1: first\n2:     indented\n3: third",
        )

    def test_reads_requested_inclusive_line_range(self):
        self._write("first\nsecond\nthird\nfourth\n")

        self.assertEqual(
            read_file("sample.txt", start_line=2, end_line=3),
            "2: second\n3: third",
        )

    def test_invalid_line_arguments_return_messages_before_path_resolution(self):
        invalid_arguments = [
            ("20", None, "start_line must be a positive integer"),
            (0, None, "start_line must be a positive integer"),
            (-5, None, "start_line must be a positive integer"),
            (1, "2", "end_line must be an integer"),
            (5, 4, "must be greater than or equal to start_line"),
        ]

        for start_line, end_line, expected_message in invalid_arguments:
            with self.subTest(start_line=start_line, end_line=end_line):
                self.resolve.reset_mock()
                result = read_file("sample.txt", start_line, end_line)

                self.assertIn(expected_message, result)
                self.resolve.assert_not_called()

    def test_past_end_and_empty_file_return_explanatory_messages(self):
        self._write("first\nsecond\nthird\n")
        self.assertEqual(
            read_file("sample.txt", start_line=5),
            "Error: start_line 5 is past the end of 'sample.txt' (3 lines).",
        )

        self._write("")
        self.assertEqual(read_file("sample.txt"), "Error: 'sample.txt' is empty.")

    def test_budget_truncates_between_lines_and_provides_next_start_line(self):
        self._write("before\nsecond\nthird\nfourth\n")

        with patch("tools.read_file_tool.MAX_READ_CHARS", 12):
            result = read_file("sample.txt", start_line=2)

        self.assertEqual(
            result,
            "2: second\n[Truncated after line 2. Call read_file again "
            "with start_line=3 to continue.]",
        )

    def test_oversized_first_line_is_not_split(self):
        self._write("a line that exceeds the limit")

        with patch("tools.read_file_tool.MAX_READ_CHARS", 8):
            result = read_file("sample.txt")

        self.assertIn("line 1 exceeds the 8-character limit", result)
        self.assertIn("cannot be returned as a whole line", result)

    def test_schema_has_optional_integer_line_arguments(self):
        parameters = read_file_schema["function"]["parameters"]
        properties = parameters["properties"]

        self.assertEqual(parameters["required"], ["file_path"])
        self.assertEqual(properties["start_line"]["type"], "integer")
        self.assertEqual(properties["end_line"]["type"], "integer")
        self.assertIn(
            "search results", properties["start_line"]["description"].lower()
        )
        self.assertIn(
            "search results", properties["end_line"]["description"].lower()
        )


if __name__ == "__main__":
    unittest.main()
