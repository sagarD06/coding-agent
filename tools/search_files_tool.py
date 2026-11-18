import os

from constants import HIDDEN_FROM_LISTING, MAX_SEARCH_ENTRIES, ROOT
from exceptions import SandboxError
from tools.helper import resolve_in_project


def search_files(keyword, path="."):
    """Searches for a keyword, first choice for finding where a function, class or value is defined or used in files inside the project."""
    try:
        if keyword is None or str(keyword).strip() == "":
            return "Error: No keyword provided for search."

        target = resolve_in_project(path)
        keyword = str(keyword).lower()  # Ensure keyword is a string

        if not target.exists():
            return f"Error: '{path}' does not exist."
        if not target.is_dir():
            return f"Error: '{path}' is not a directory. Use read_file to read it."

        matches = []
        for dirpath, dirs, files in os.walk(target):
            dirs[:] = [d for d in dirs if d not in HIDDEN_FROM_LISTING and not d.startswith(".")]  # filter dirs in-place
            files = [f for f in files if f not in HIDDEN_FROM_LISTING and not f.startswith(".")]  # filter files

            for file in files:
                file_path = os.path.join(dirpath, file)
                try:
                    file_path = resolve_in_project(file_path)
                    with open(file_path, "r", encoding="utf-8") as f:
                        for number, line in enumerate(f, start=1):
                            if keyword in line.strip().lower():
                                result = f"{file_path.relative_to(ROOT).as_posix()}:{number}: {line.strip()[:200]}"
                                matches.append(result)
                except SandboxError:
                    continue # Skip files that are outside the project
                except UnicodeError:
                    continue  # Skip files that can't be decoded as UTF-8
                except OSError:
                    continue  # Skip files that can't be opened
        if not matches:
            return f"No files found containing '{keyword}'."
        return "\n".join(matches[:MAX_SEARCH_ENTRIES]) + (
            f"\n[{len(matches) - MAX_SEARCH_ENTRIES} more matches not shown]"
            if len(matches) > MAX_SEARCH_ENTRIES
            else ""
        )
    except SandboxError as error:
        return f"Error: {error}"
    except PermissionError:
        return f"Error: the operating system denied permission to access '{path}'."
    except OSError as error:
        return f"Error accessing '{path}': {error}"