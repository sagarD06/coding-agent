import copy
import unittest
from unittest.mock import patch

from exceptions import ToolRegistryError
from tool_registry import validate_tool_registry


def _schema(properties=None, required=None):
    parameters = {}
    if properties is not None:
        parameters["properties"] = properties
    if required is not None:
        parameters["required"] = required
    return {
        "function": {
            "name": "sample",
            "parameters": parameters,
        }
    }


class ValidateToolRegistryTests(unittest.TestCase):
    def _validate(self, func, schema):
        registry = {"sample": {"schema": schema, "function": func}}
        with patch("tool_registry.TOOL_REGISTRY", registry):
            validate_tool_registry()

    def test_optional_parameter_required_by_schema_is_reported_as_optional(self):
        def sample(path="."):
            pass

        with self.assertRaises(ToolRegistryError) as raised:
            self._validate(sample, _schema({"path": {}}, ["path"]))

        message = str(raised.exception)
        self.assertIn("corresponds to optional parameter 'path'", message)
        self.assertNotIn("is not a parameter", message)

    def test_required_schema_property_not_in_function_is_reported(self):
        def sample():
            pass

        with self.assertRaises(ToolRegistryError) as raised:
            self._validate(sample, _schema({}, ["unknown"]))

        self.assertIn(
            "Required property 'unknown' in schema is not a parameter",
            str(raised.exception),
        )

    def test_variadic_parameters_are_explicitly_unsupported(self):
        def sample(*args, **kwargs):
            pass

        with self.assertRaises(ToolRegistryError) as raised:
            self._validate(sample, _schema({}))

        message = str(raised.exception)
        self.assertIn("Variadic parameter '*args'", message)
        self.assertIn("Variadic parameter '**kwargs'", message)
        self.assertNotIn("Parameter 'args' in function", message)
        self.assertNotIn("Parameter 'kwargs' in function", message)

    def test_missing_parameter_properties_are_reported_without_crashing(self):
        def sample():
            pass

        schema = _schema()
        with self.assertRaises(ToolRegistryError) as raised:
            self._validate(sample, schema)

        self.assertIn("missing function parameter properties", str(raised.exception))

    def test_missing_parameters_are_reported_without_crashing(self):
        def sample():
            pass

        schema = copy.deepcopy(_schema({}))
        del schema["function"]["parameters"]
        with self.assertRaises(ToolRegistryError) as raised:
            self._validate(sample, schema)

        message = str(raised.exception)
        self.assertIn("missing function parameters", message)
        self.assertNotIn("missing function parameter properties", message)


if __name__ == "__main__":
    unittest.main()
