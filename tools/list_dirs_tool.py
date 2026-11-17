from constants import HIDDEN_FROM_LISTING, MAX_LIST_ENTRIES
from exceptions import SandboxError
from tools.helper import resolve_in_project


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