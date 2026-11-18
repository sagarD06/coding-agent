import inspect

from exceptions import ToolRegistryError
from schemas import (
    get_current_date_schema,
    list_dir_schema,
    read_file_schema,
    search_file_schema,
)
from tools import get_current_date, list_dir, read_file, search_files

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
    },
    "search_files": {
        "schema": search_file_schema,
        "function": search_files, 
    }
}


def validate_tool_registry():
    errors = []

    for tool_name, tool_info in TOOL_REGISTRY.items():
        schema = tool_info["schema"]
        func = tool_info["function"]
        func_params = inspect.signature(func).parameters
        supported_params = {}

        for param_name, details in func_params.items():
            if details.kind is inspect.Parameter.VAR_POSITIONAL:
                errors.append(
                    f"Variadic parameter '*{param_name}' in function '{func.__name__}' is not supported"
                )
            elif details.kind is inspect.Parameter.VAR_KEYWORD:
                errors.append(
                    f"Variadic parameter '**{param_name}' in function '{func.__name__}' is not supported"
                )
            else:
                supported_params[param_name] = details

        # Check if the registry key matches the schema function name
        function_schema = schema.get("function")
        if not isinstance(function_schema, dict):
            errors.append(
                f"Schema for tool '{tool_name}' is missing a function object"
            )
            function_schema = {}
        schema_name = function_schema.get("name")
        if schema_name is None:
            errors.append(f"Schema for tool '{tool_name}' is missing a function name")
        elif tool_name != schema_name:
            errors.append(
                f"Tool name '{tool_name}' does not match schema function name '{schema_name}'"
            )

        parameters = function_schema.get("parameters")
        if not isinstance(parameters, dict):
            errors.append(
                f"Schema for tool '{tool_name}' is missing function parameters"
            )
            parameters = {}
            schema_props = {}
        else:
            if "properties" not in parameters:
                errors.append(
                    f"Schema for tool '{tool_name}' is missing function parameter properties"
                )
            schema_props = parameters.get("properties", {})
            if not isinstance(schema_props, dict):
                errors.append(
                    f"Function parameter properties for tool '{tool_name}' must be an object"
                )
                schema_props = {}

        # Check if every parameter in the function's signature appears in the schema's properties
        for param in supported_params:
            if param not in schema_props:
                errors.append(
                    f"Parameter '{param}' in function '{func.__name__}' is not defined in the schema properties"
                )

        # Check if every property in the schema appears in the function's signature
        for prop in schema_props:
            if prop not in func_params:
                errors.append(
                    f"Property '{prop}' in schema is not defined in the function '{func.__name__}' parameters"
                )

        # Check required parameters
        required_params = [
            param
            for param, details in supported_params.items()
            if details.default is inspect.Parameter.empty
        ]
        required_schema = parameters.get("required", [])
        if not isinstance(required_schema, list):
            errors.append(
                f"Required properties for tool '{tool_name}' must be a list"
            )
            required_schema = []

        for req_param in required_params:
            if req_param not in required_schema:
                errors.append(
                    f"Required parameter '{req_param}' in function '{func.__name__}' is not listed as required in the schema"
                )

        for req_schema in required_schema:
            if req_schema not in func_params:
                errors.append(
                    f"Required property '{req_schema}' in schema is not a parameter of the function '{func.__name__}'"
                )
            elif req_schema not in required_params:
                errors.append(
                    f"Required property '{req_schema}' in schema corresponds to optional parameter '{req_schema}' in function '{func.__name__}'"
                )

    if errors:
        raise ToolRegistryError("Tool registry validation failed:\n" + "\n".join(errors))
