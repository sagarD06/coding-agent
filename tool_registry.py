from schema import get_current_date_schema, list_dir_schema, read_file_schema
from tools import get_current_date, list_dir, read_file

TOOL_REGISTRY = {
    "get_current_date": {
        "schema": get_current_date_schema,
        "function": get_current_date,
    },
    "read_file": {
        "schema": read_file_schema,
        "function": read_file,
    },
    "list_dir": {
        "schema": list_dir_schema,
        "function": list_dir,
    }
}