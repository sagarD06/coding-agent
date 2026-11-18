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
                },
                "start_line": {
                    "type": "integer",
                    "description": (
                        "Optional 1-indexed line number to start reading from. "
                        "Search results include line numbers you can pass here."
                    ),
                    "default": 1,
                },
                "end_line": {
                    "type": "integer",
                    "description": (
                        "Optional 1-indexed inclusive line number to stop at. "
                        "Search results include line numbers you can pass here."
                    ),
                },
            },
            "required": ["file_path"],
        },
    },
}