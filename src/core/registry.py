from typing import Dict, List, Optional
from src.core.tool import BaseTool
from src.core.logger import logger

class ToolRegistry:
    _instance = None
    _tools: Dict[str, BaseTool] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ToolRegistry, cls).__new__(cls)
        return cls._instance

    def register(self, tool: BaseTool):
        """
        Register a tool instance.
        """
        if tool.name in self._tools:
            logger.warning(f"Tool {tool.name} is already registered. Overwriting.")
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """
        Retrieve a tool by name.
        """
        return self._tools.get(name)

    def list_tools(self) -> List[BaseTool]:
        """
        List all registered tools.
        """
        return list(self._tools.values())

    def clear(self):
        """
        Clear all registered tools.
        """
        self._tools.clear()

registry = ToolRegistry()
