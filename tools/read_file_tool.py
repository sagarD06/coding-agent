import itertools

from constants import MAX_READ_CHARS
from exceptions import SandboxError
from tools.helper import resolve_in_project


def read_file(file_path, start_line=1, end_line=None):
    """Reads whole numbered lines from a text file inside the project."""
    if not isinstance(start_line, int) or isinstance(start_line, bool):
        return "Error: start_line must be a positive integer (1 or greater)."
    if start_line < 1:
        return "Error: start_line must be a positive integer (1 or greater)."
    if end_line is not None and (
        not isinstance(end_line, int) or isinstance(end_line, bool)
    ):
        return "Error: end_line must be an integer greater than or equal to start_line."
    if end_line is not None and end_line < start_line:
        return (
            f"Error: end_line ({end_line}) must be greater than or equal to "
            f"start_line ({start_line})."
        )

    try:
        path = resolve_in_project(file_path)

        if not path.exists():
            return f"Error: '{file_path}' does not exist. Use list_dir to see available files."
        if path.is_dir():
            return f"Error: '{file_path}' is a directory. Use list_dir to see its contents."
        if not path.is_file():
            return f"Error: '{file_path}' is not a regular file."

        with path.open("r", encoding="utf-8") as file:
            formatted_lines = []
            used_chars = 0
            last_line = None
            truncated = False
            oversized_line = None

            selected_lines = itertools.islice(file, start_line - 1, end_line)
            for line_num, line in enumerate(selected_lines, start=start_line):
                line_content = line.rstrip("\r\n")
                formatted_line = f"{line_num}: {line_content}"
                line_size = len(formatted_line) + (1 if formatted_lines else 0)
                if used_chars + line_size > MAX_READ_CHARS:
                    if formatted_lines:
                        truncated = True
                    else:
                        oversized_line = line_num
                    break

                formatted_lines.append(formatted_line)
                used_chars += line_size
                last_line = line_num

            if not formatted_lines:
                if oversized_line is not None:
                    return (
                        f"Error: line {oversized_line} exceeds the "
                        f"{MAX_READ_CHARS}-character limit and cannot be returned "
                        "as a whole line."
                    )

                file.seek(0)
                line_count = sum(1 for _ in file)
                if line_count == 0:
                    return f"Error: '{file_path}' is empty."
                return (
                    f"Error: start_line {start_line} is past the end of "
                    f"'{file_path}' ({line_count} lines)."
                )

        content = "\n".join(formatted_lines)
        if truncated and last_line is not None:
            content += (
                f"\n[Truncated after line {last_line}. Call read_file again "
                f"with start_line={last_line + 1} to continue.]"
            )
        return content
    except SandboxError as error:
        return f"Error: {error}"
    except UnicodeDecodeError:
        return f"Error: '{file_path}' is not a UTF-8 text file (it may be binary)."
    except PermissionError:
        return f"Error: the operating system denied permission to read '{file_path}'."
    except OSError as error:
        return f"Error reading '{file_path}': {error}"