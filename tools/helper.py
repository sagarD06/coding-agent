from pathlib import Path

from constants import BLOCKED_NAMES, ROOT
from exceptions import SandboxError


def resolve_in_project(raw_path):
    """
    Turns the path the model sent into a safe absolute Path.
    Raises SandboxError if it is outside the project or in a blocked location.
    Does not check existence; callers do that so they can word their own errors.
    """
    path = Path(raw_path)
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()

    if not path.is_relative_to(ROOT):
        raise SandboxError(
            f"'{raw_path}' is outside the project folder. "
            "Only files inside the project folder can be accessed. "
            "Use a path relative to the project root."
        )
    if any(part in BLOCKED_NAMES for part in path.relative_to(ROOT).parts):
        raise SandboxError(
            f"'{raw_path}' is in a protected location (.git, venv or .env) "
            "that tools are not allowed to access."
        )
    return path