from pathlib import Path

MAX_STEPS = 5  # Maximum number of steps to prevent infinite loops
MAX_READ_CHARS = 4000
MAX_LIST_ENTRIES = 100
MAX_SEARCH_ENTRIES = 30

# Tools can never open these, even inside the project.
BLOCKED_NAMES = {".git", "venv", ".venv", ".env"}
# Hidden from listings only (noise), but still readable.
HIDDEN_FROM_LISTING = BLOCKED_NAMES | {"__pycache__"}

ROOT = Path(__file__).resolve().parent