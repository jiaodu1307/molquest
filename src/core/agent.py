from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from src.core.logger import logger

class BaseAgent(ABC):
    """
    Abstract base class for Agents.
    """
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.is_initialized = False

    def initialize(self):
        """
        Initialize the agent (load models, tools, etc.)
        """
        logger.info(f"Initializing agent: {self.name}")
        self._setup_tools()
        self._setup_model()
        self.is_initialized = True
        logger.info(f"Agent {self.name} initialized.")

    @abstractmethod
    def _setup_tools(self):
        """
        Setup tools required by the agent.
        """
        pass

    @abstractmethod
    def _setup_model(self):
        """
        Setup the LLM model.
        """
        pass

    @abstractmethod
    def run(self, input_data: Any) -> Any:
        """
        Execute the agent logic.
        """
        pass

    def terminate(self):
        """
        Cleanup resources.
        """
        logger.info(f"Terminating agent: {self.name}")
        self.is_initialized = False
