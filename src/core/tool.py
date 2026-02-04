from abc import ABC, abstractmethod
from typing import Any, Dict, Type, Optional
from pydantic import BaseModel, Field

class BaseTool(ABC):
    """
    Abstract base class for all tools in the framework.
    """
    name: str
    description: str
    args_schema: Type[BaseModel]

    def __init__(self, name: str, description: str, args_schema: Type[BaseModel]):
        self.name = name
        self.description = description
        self.args_schema = args_schema

    @abstractmethod
    def _run(self, **kwargs: Any) -> Any:
        """
        The actual execution logic of the tool.
        """
        pass

    def run(self, **kwargs: Any) -> Any:
        """
        Public method to execute the tool with validation.
        """
        # Validate inputs
        try:
            validated_args = self.args_schema(**kwargs)
        except Exception as e:
            raise ValueError(f"Invalid arguments for tool {self.name}: {e}")

        return self._run(**validated_args.model_dump())

    def to_langchain_tool(self):
        """
        Convert to a format compatible with LangChain if needed.
        """
        from langchain_core.tools import Tool
        
        # This is a simplified conversion, real implementation might use StructuredTool
        from langchain_core.tools import StructuredTool
        
        return StructuredTool.from_function(
            func=self._run,
            name=self.name,
            description=self.description,
            args_schema=self.args_schema
        )
