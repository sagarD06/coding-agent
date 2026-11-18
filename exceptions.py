class SandboxError(Exception):
    """Raised when a tool is asked to touch a path it is not allowed to."""

class ToolRegistryError(Exception):
    """Raised when there is a mismatch between the tool registry and the schema."""