"""Tool registry for managing and discovering available SRE tools."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Type

from opensre.tools.base import BaseTool, ToolResult

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Central registry for all SRE tools.

    Provides registration, discovery, and execution of tools
    that are available in the current environment.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a tool instance.

        Args:
            tool: An instantiated tool that extends BaseTool.
        """
        name = tool.name
        if name in self._tools:
            logger.warning("Tool '%s' is already registered — overwriting.", name)
        self._tools[name] = tool
        logger.debug("Registered tool: %s", name)

    def register_class(self, tool_cls: Type[BaseTool], **kwargs) -> None:
        """Instantiate and register a tool from its class.

        Args:
            tool_cls: A subclass of BaseTool.
            **kwargs: Additional keyword arguments passed to the constructor.
        """
        instance = tool_cls(**kwargs)
        self.register(instance)

    def unregister(self, name: str) -> bool:
        """Remove a tool from the registry.

        Args:
            name: The tool name to remove.

        Returns:
            True if the tool was found and removed, False otherwise.
        """
        if name in self._tools:
            del self._tools[name]
            logger.debug("Unregistered tool: %s", name)
            return True
        return False

    def get(self, name: str) -> Optional[BaseTool]:
        """Retrieve a tool by name.

        Args:
            name: The registered tool name.

        Returns:
            The tool instance, or None if not found.
        """
        return self._tools.get(name)

    def available_tools(self) -> List[BaseTool]:
        """Return all tools that report themselves as available.

        Returns:
            List of tool instances where is_available() is True.
        """
        return [t for t in self._tools.values() if t.is_available()]

    def all_tools(self) -> List[BaseTool]:
        """Return every registered tool regardless of availability."""
        return list(self._tools.values())

    def run(self, name: str, **params) -> ToolResult:
        """Execute a registered tool by name.

        Args:
            name: The tool name to run.
            **params: Parameters forwarded to the tool's run() method.

        Returns:
            ToolResult produced by the tool.

        Raises:
            KeyError: If no tool with the given name is registered.
            RuntimeError: If the tool is not available in the current environment.
        """
        tool = self._tools.get(name)
        if tool is None:
            raise KeyError(f"No tool registered with name '{name}'")
        if not tool.is_available():
            raise RuntimeError(
                f"Tool '{name}' is registered but not available in this environment."
            )
        logger.info("Running tool '%s' with params: %s", name, params)
        return tool.run(**params)

    def __len__(self) -> int:
        return len(self._tools)

    def __repr__(self) -> str:  # pragma: no cover
        names = list(self._tools.keys())
        return f"ToolRegistry(tools={names})"


# Module-level default registry — importable as a singleton.
default_registry = ToolRegistry()
