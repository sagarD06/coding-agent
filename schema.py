get_current_date_schema = {
    "type": "function",
    "function": {
        "name": "get_current_date",
        "description": "Returns the current date in YYYY-MM-DD format.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}

read_file_schema = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": (
            "Reads a file from the project folder. Paths are relative to the project "
            "folder; read the file to verify its contents instead of guessing."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to be read.",
                }
            },
            "required": ["file_path"],
        },
    },
}

list_dir_schema = {
    "type": "function",
    "function": {
        "name": "list_dir",
        "description": (
            "Lists the contents of a directory in the project folder. "
            "Directories end with '/'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": (
                        "The path to the directory to be listed. "
                        "If not provided, defaults to the project root."
                    ),
                }
            },
            "required": [],
        },
    },
}
