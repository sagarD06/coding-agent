from datetime import datetime
from pathlib import Path

root = Path(__file__).resolve().parent

MAX_READ_CHARS = 4000
MAX_LIST_ENTRIES = 100

# Tools can never open these, even inside the project.
BLOCKED_NAMES = {".git", "venv", ".venv", ".env"}
# Hidden from listings only (noise), but still readable.
HIDDEN_FROM_LISTING = BLOCKED_NAMES | {"__pycache__"}


class SandboxError(Exception):
    """Raised when a tool is asked to touch a path it is not allowed to."""


def resolve_in_project(raw_path):
    """
    Turns the path the model sent into a safe absolute Path.
    Raises SandboxError if it is outside the project or in a blocked location.
    Does not check existence; callers do that so they can word their own errors.
    """
    path = Path(raw_path)
    if not path.is_absolute():
        path = root / path
    path = path.resolve()

    if not path.is_relative_to(root):
        raise SandboxError(
            f"'{raw_path}' is outside the project folder. "
            "Only files inside the project folder can be accessed. "
            "Use a path relative to the project root."
        )
    if any(part in BLOCKED_NAMES for part in path.relative_to(root).parts):
        raise SandboxError(
            f"'{raw_path}' is in a protected location (.git, venv or .env) "
            "that tools are not allowed to access."
        )
    return path


def get_current_date():
    """Returns the current date in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")


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


def list_dir(path="."):
    """Lists a directory inside the project. Directories end with '/'."""
    try:
        target = resolve_in_project(path)

        if not target.exists():
            return f"Error: '{path}' does not exist."
        if not target.is_dir():
            return f"Error: '{path}' is not a directory. Use read_file to read it."

        entries = sorted(
            (e for e in target.iterdir() if e.name not in HIDDEN_FROM_LISTING),
            key=lambda e: (not e.is_dir(), e.name.lower()),  # folders first
        )
        names = [e.name + "/" if e.is_dir() else e.name for e in entries]
        if not names:
            return "(empty directory)"

        result = "\n".join(names[:MAX_LIST_ENTRIES])
        if len(names) > MAX_LIST_ENTRIES:
            result += f"\n[{len(names) - MAX_LIST_ENTRIES} more entries not shown]"
        return result
    except SandboxError as error:
        return f"Error: {error}"
    except PermissionError:
        return f"Error: the operating system denied permission to open '{path}'."
    except OSError as error:
        return f"Error accessing '{path}': {error}"