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