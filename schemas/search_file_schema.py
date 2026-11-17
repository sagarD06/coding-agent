search_file_schema = {
    "type": "function",
    "function": {
        "name": "search_files",
        "description": (
            "Searches for a keyword, first choice for finding where a function, class or value is defined or used in files inside the project folder."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "The keyword to search for in the file contents.",
                },
                "path": {
                    "type": "string",
                    "description": (
                        "The path to the directory to search in. "
                        "If not provided, defaults to the project root."
                    ),
                },
            },
            "required": ["keyword"],
        },
    },
}