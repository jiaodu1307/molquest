from typing import TypedDict, Annotated, List, Optional, Any
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    uuid: str
    known_data: dict # Store gathered info (mw, formula, etc.)
    final_answer: Optional[str]
    token_usage: Optional[dict]
