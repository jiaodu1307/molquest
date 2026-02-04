from typing import Any, Dict, List, Optional, Union
import json
import re
import logging
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
    AIMessage,
    ToolMessage,
)
from langchain_core.tools import BaseTool
import httpx
import openai

logger = logging.getLogger(__name__)

class CompletionChatAdapter:
    """
    Adapter to use a Completion model (v1/completions) as a Chat model.
    It converts chat messages into a single prompt string and handles
    pseudo-tool-calling by prompting the model to output JSON.
    """

    def __init__(
        self,
        model_name: str,
        api_key: str,
        base_url: str,
        temperature: float = 0.0,
        stop: Optional[List[str]] = None,
        seed: Optional[int] = None,
        max_tokens: int = 4096,
        endpoint_url: Optional[str] = None,
        **kwargs
    ):
        self.model_name = model_name
        self.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self.temperature = temperature
        self.stop = stop
        self.seed = seed
        self.max_tokens = max_tokens
        self.endpoint_url = endpoint_url
        self.tools: List[BaseTool] = []
        self.tools_map: Dict[str, BaseTool] = {}
        self.kwargs = kwargs

    def bind_tools(self, tools: List[BaseTool]):
        """
        Bind tools to the model. In this adapter, we just store them
        to inject into the prompt later.
        """
        self.tools = tools
        self.tools_map = {t.name: t for t in tools}
        return self

    def invoke(self, messages: List[BaseMessage], **kwargs) -> AIMessage:
        """
        Invoke the model with a list of messages.
        """
        prompt = self._construct_prompt(messages)
        
        # Merge kwargs
        call_kwargs = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if self.stop:
            call_kwargs["stop"] = self.stop
        if self.seed is not None:
            call_kwargs["seed"] = self.seed
            
        # Add any other kwargs passed to init or invoke
        # Handle 'model_kwargs' which might contain 'extra_body'
        if "model_kwargs" in self.kwargs:
            call_kwargs.update(self.kwargs["model_kwargs"])
        
        call_kwargs.update({k: v for k, v in self.kwargs.items() if k != "model_kwargs"})
        call_kwargs.update({k: v for k, v in kwargs.items() if k not in ["tools", "tool_choice"]})

        # Remove custom adapter arguments that are not supported by the client
        call_kwargs.pop("endpoint_url", None)

        try:
            # Clean up potential conflict parameters
            if "messages" in call_kwargs:
                del call_kwargs["messages"]

            if self.endpoint_url:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": self.model_name,
                    "input": prompt,
                }
                if self.temperature is not None:
                    payload["temperature"] = self.temperature
                if self.max_tokens is not None:
                    payload["max_output_tokens"] = self.max_tokens
                if self.stop:
                    payload["stop"] = self.stop
                if self.seed is not None:
                    payload["seed"] = self.seed

                extra_body = None
                if "model_kwargs" in self.kwargs:
                    extra_body = self.kwargs.get("model_kwargs", {}).get("extra_body")
                if isinstance(extra_body, dict):
                    payload.update(extra_body)

                response = httpx.post(
                    self.endpoint_url,
                    headers=headers,
                    json=payload,
                    timeout=120.0
                )
                response.raise_for_status()
                data = response.json()

                if isinstance(data, dict):
                    if isinstance(data.get("output_text"), str):
                        text_response = data["output_text"]
                    elif "output" in data:
                        out = data["output"]
                        if isinstance(out, list):
                            parts = []
                            for item in out:
                                if isinstance(item, dict):
                                    content = item.get("content")
                                    if isinstance(content, list):
                                        for block in content:
                                            if isinstance(block, dict) and block.get("type") in ("output_text", "text", "input_text"):
                                                t = block.get("text")
                                                if isinstance(t, str) and t:
                                                    parts.append(t)
                                    if not parts and isinstance(item.get("text"), str):
                                        parts.append(item.get("text"))
                                else:
                                    parts.append(str(item))
                            text_response = "\n".join(parts).strip()
                        elif isinstance(out, dict):
                            if isinstance(out.get("text"), str):
                                text_response = out.get("text", "")
                            elif isinstance(out.get("content"), list):
                                parts = []
                                for block in out["content"]:
                                    if isinstance(block, dict) and block.get("type") in ("output_text", "text", "input_text"):
                                        t = block.get("text")
                                        if isinstance(t, str) and t:
                                            parts.append(t)
                                text_response = "\n".join(parts).strip()
                            else:
                                text_response = str(out)
                        else:
                            text_response = str(out)
                    elif "choices" in data:
                        text_response = data["choices"][0].get("text", "")
                    else:
                        text_response = str(data)
                else:
                    text_response = str(data)

            else:
                # Use standard OpenAI client
                response = self.client.completions.create(**call_kwargs)
                text_response = response.choices[0].text.strip()
            
            # Try to parse tool calls
            tool_calls = self._parse_tool_calls(text_response)
            
            if tool_calls:
                return AIMessage(content=text_response, tool_calls=tool_calls)
            else:
                return AIMessage(content=text_response)
                
        except Exception as e:
            logger.error(f"Error calling Completion API: {e}")
            raise

    def _construct_prompt(self, messages: List[BaseMessage]) -> str:
        """
        Convert messages to a single prompt string.
        """
        prompt_parts = []
        
        # 1. System Prompt & Tools
        system_prompt = "You are a helpful AI assistant."
        tools_desc = self._render_tools_description()
        
        if tools_desc:
            system_prompt += f"\n\nYou have access to the following tools:\n{tools_desc}"
            system_prompt += (
                "\n\nTo use a tool, you MUST respond with a valid JSON object strictly following this format:\n"
                "```json\n"
                "{\"tool_calls\": [{\"name\": \"tool_name\", \"arguments\": {\"arg_name\": \"value\"}}]}\n"
                "```\n"
                "If you want to use multiple tools, include them in the 'tool_calls' list.\n"
                "If you do not need to use a tool, just respond with natural language.\n"
                "IMPORTANT: Do not output any other text before or after the JSON if you are using a tool."
            )

        # Check if there is an existing system message
        existing_system = next((m for m in messages if isinstance(m, SystemMessage)), None)
        if existing_system:
            system_prompt += f"\n\n{existing_system.content}"
        
        prompt_parts.append(f"System:\n{system_prompt}\n")

        # 2. History
        for m in messages:
            if isinstance(m, SystemMessage):
                continue
            elif isinstance(m, HumanMessage):
                prompt_parts.append(f"User: {m.content}")
            elif isinstance(m, AIMessage):
                if m.tool_calls:
                    prompt_parts.append(f"Assistant (Tool Call): {json.dumps(m.tool_calls)}")
                else:
                    prompt_parts.append(f"Assistant: {m.content}")
            elif isinstance(m, ToolMessage):
                prompt_parts.append(f"Tool Output ({m.name or m.tool_call_id}): {m.content}")
            else:
                prompt_parts.append(f"User: {m.content}")

        # 3. Final trigger
        prompt_parts.append("Assistant:")
        
        return "\n\n".join(prompt_parts)

    def _render_tools_description(self) -> str:
        if not self.tools:
            return ""
        
        lines = []
        for t in self.tools:
            args = ""
            if hasattr(t, "args") and t.args:
                args = f" Args: {t.args}"
            elif hasattr(t, "args_schema") and hasattr(t.args_schema, "schema"):
                try:
                    schema = t.args_schema.schema()
                    props = schema.get("properties", {})
                    args_list = []
                    for prop_name, prop_info in props.items():
                        args_list.append(f"{prop_name} ({prop_info.get('type', 'any')}): {prop_info.get('description', '')}")
                    args = " Args: {" + ", ".join(args_list) + "}"
                except Exception:
                    args = " Args: <unknown>"
            
            lines.append(f"- {t.name}: {t.description}{args}")
        return "\n".join(lines)

    def _parse_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        """
        Attempt to parse JSON tool calls from the response text.
        """
        json_blocks = [m.group(1) for m in re.finditer(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)]

        def extract_json_objects(raw: str) -> List[str]:
            blocks: List[str] = []
            depth = 0
            start = None
            in_string = False
            escape = False
            for i, ch in enumerate(raw):
                if in_string:
                    if escape:
                        escape = False
                    elif ch == "\\":
                        escape = True
                    elif ch == '"':
                        in_string = False
                    continue
                if ch == '"':
                    in_string = True
                    continue
                if ch == "{":
                    if depth == 0:
                        start = i
                    depth += 1
                elif ch == "}":
                    if depth > 0:
                        depth -= 1
                        if depth == 0 and start is not None:
                            blocks.append(raw[start:i + 1])
                            start = None
            return blocks

        if not json_blocks:
            json_blocks = extract_json_objects(text)

        import uuid
        calls: List[Dict[str, Any]] = []
        for block in json_blocks:
            try:
                data = json.loads(block)
            except json.JSONDecodeError:
                continue
            if "tool_calls" in data and isinstance(data["tool_calls"], list):
                for tc in data["tool_calls"]:
                    if "name" in tc and "arguments" in tc:
                        calls.append({
                            "name": tc["name"],
                            "args": tc["arguments"],
                            "id": f"call_{uuid.uuid4().hex[:8]}"
                        })
        return calls