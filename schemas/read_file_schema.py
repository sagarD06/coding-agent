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