from constants import MAX_READ_CHARS
from exceptions import SandboxError
from tools.helper import resolve_in_project


def read_file(file_path):
    """Reads a text file inside the project and returns its contents."""
    try:
        path = resolve_in_project(file_path)

        if not path.exists():
            return f"Error: '{file_path}' does not exist. Use list_dir to see available files."
        if path.is_dir():
            return f"Error: '{file_path}' is a directory. Use list_dir to see its contents."
        if not path.is_file():
            return f"Error: '{file_path}' is not a regular file."

        with path.open("r", encoding="utf-8") as file:
            content = file.read(MAX_READ_CHARS + 1)
        if len(content) > MAX_READ_CHARS:
            return (
                content[:MAX_READ_CHARS]
                + f"\n[Truncated: showing the first {MAX_READ_CHARS} characters; the file is longer.]"
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