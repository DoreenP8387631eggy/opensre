"""Base tool interface for opensre integrations.

All tools must inherit from BaseTool and implement the required methods
as defined in .cursor/rules/tools.mdc.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    """Encapsulates the result of a tool execution."""

    success: bool
    output: Any = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return self.success


class BaseTool(ABC):
    """Abstract base class for all opensre tools.

    Subclasses must implement `is_available`, `extract_params`, and `run`
    following the contract described in tools.mdc.

    Example::

        class MyTool(BaseTool):
            my_tool_name = "my_tool"

            def is_available(self) -> bool:
                return shutil.which("my_tool") is not None

            def extract_params(self, raw: dict[str, Any]) -> dict[str, Any]:
                return {"target": raw["target"]}

            def run(self, params: dict[str, Any]) -> ToolResult:
                ...
    """

    # Subclasses set this to a unique snake_case identifier.
    my_tool_name: str = ""

    # ---------------------------------------------------------------------------
    # Required interface
    # ---------------------------------------------------------------------------

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the tool's underlying dependency is present."""

    @abstractmethod
    def extract_params(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Validate and extract parameters from a raw input mapping.

        Raises:
            ValueError: if required parameters are missing or invalid.
        """

    @abstractmethod
    def run(self, params: dict[str, Any]) -> ToolResult:
        """Execute the tool with the given parameters.

        Always returns a :class:`ToolResult`; must not raise.
        """

    # ---------------------------------------------------------------------------
    # Convenience helpers
    # ---------------------------------------------------------------------------

    def safe_run(self, raw: dict[str, Any]) -> ToolResult:
        """Validate availability, extract params, then run the tool.

        This is the recommended entry-point for callers so that error
        handling is consistent across all tools.
        """
        if not self.is_available():
            return ToolResult(
                success=False,
                error=f"Tool '{self.my_tool_name}' is not available in this environment.",
            )

        try:
            params = self.extract_params(raw)
        except (ValueError, KeyError) as exc:
            return ToolResult(
                success=False,
                error=f"Parameter extraction failed for '{self.my_tool_name}': {exc}",
            )

        return self.run(params)

    def __repr__(self) -> str:  # pragma: no cover
        available = self.is_available()
        return f"<{type(self).__name__} name={self.my_tool_name!r} available={available}>"
