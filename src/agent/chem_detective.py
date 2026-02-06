from typing import Any, Dict, List
import re
import os
import json
import time
import random
import yaml
import httpx
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage

from src.core.agent import BaseAgent
from src.core.registry import registry
from src.agent.state import AgentState
from src.tools.implementations.analysis_tools import (
    MeasureMWTool,
    MeasureFormulaTool,
    Get13CNMRTool,
    CalculateDBETool,
    Get1HNMRTool,
    CheckDataTool,
    GetIRTool,
    Get19FNMRTool,
    Get31PNMRTool,
    GetHRMSTool,
    GetMSTool,
    GetMeltingPointTool,
    GetTLCTool,
    GetOpticalRotationTool,
)
from src.core.logger import logger
from src.core.completion_adapter import CompletionChatAdapter

class MolQuestAgent(BaseAgent):
    def __init__(self, name: str = "MolQuest", config: Dict[str, Any] = None):
        loaded_config = self._load_config()
        if config:
            if "llm" in config and "llm" in loaded_config:
                incoming_llm = config.get("llm") or {}
                if "provider" in incoming_llm and "base_url" not in incoming_llm:
                    loaded_config["llm"].pop("base_url", None)
                loaded_config["llm"].update(incoming_llm)
            else:
                loaded_config.update(config)

        super().__init__(name, loaded_config)
        self.graph = None
        self.model = None
        self.final_model = None
        self.final_model_no_stream = None
        self._token_usage = {
            "calls": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "by_model_attr": {},
        }

    def initialize(self):
        super().initialize()
        self._build_graph()

    def _build_graph(self) -> None:
        if self.graph is not None:
            return

        workflow = StateGraph(AgentState)
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", self._run_tools)
        workflow.add_node("final", self._call_final_model)

        workflow.set_entry_point("agent")

        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "tools": "tools",
                "final": "final",
            },
        )

        workflow.add_edge("final", END)
        workflow.add_edge("tools", "agent")

        self.graph = workflow.compile()

    def _reset_token_usage(self) -> None:
        self._token_usage = {
            "calls": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "by_model_attr": {},
        }

    def _extract_token_usage(self, response: Any) -> Dict[str, int]:
        usage: Dict[str, Any] | None = None

        direct = getattr(response, "usage_metadata", None)
        if isinstance(direct, dict) and direct:
            usage = direct

        if usage is None:
            meta = getattr(response, "response_metadata", None)
            if isinstance(meta, dict) and meta:
                candidate = meta.get("token_usage")
                if isinstance(candidate, dict) and candidate:
                    usage = candidate
                else:
                    candidate = meta.get("usage")
                    if isinstance(candidate, dict) and candidate:
                        usage = candidate

        if usage is None:
            return {}

        def _as_int(value: Any) -> int:
            try:
                return int(value)
            except Exception:
                return 0

        prompt_tokens = _as_int(usage.get("prompt_tokens") or usage.get("input_tokens") or usage.get("promptTokenCount"))
        completion_tokens = _as_int(usage.get("completion_tokens") or usage.get("output_tokens") or usage.get("candidatesTokenCount"))
        total_tokens = _as_int(usage.get("total_tokens") or usage.get("totalTokenCount"))

        if total_tokens <= 0:
            total_tokens = max(0, prompt_tokens) + max(0, completion_tokens)

        out = {
            "prompt_tokens": max(0, prompt_tokens),
            "completion_tokens": max(0, completion_tokens),
            "total_tokens": max(0, total_tokens),
        }
        if out["total_tokens"] <= 0 and out["prompt_tokens"] <= 0 and out["completion_tokens"] <= 0:
            return {}
        return out

    def _accumulate_token_usage(self, model_attr: str, response: Any) -> None:
        u = self._extract_token_usage(response)
        if not u:
            return

        if not isinstance(getattr(self, "_token_usage", None), dict):
            self._reset_token_usage()

        self._token_usage["calls"] = int(self._token_usage.get("calls", 0)) + 1
        for k in ("prompt_tokens", "completion_tokens", "total_tokens"):
            self._token_usage[k] = int(self._token_usage.get(k, 0)) + int(u.get(k, 0))

        by = self._token_usage.get("by_model_attr")
        if not isinstance(by, dict):
            by = {}
            self._token_usage["by_model_attr"] = by

        entry = by.get(model_attr)
        if not isinstance(entry, dict):
            entry = {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            by[model_attr] = entry

        entry["calls"] = int(entry.get("calls", 0)) + 1
        for k in ("prompt_tokens", "completion_tokens", "total_tokens"):
            entry[k] = int(entry.get(k, 0)) + int(u.get(k, 0))

    def _load_config(self) -> Dict[str, Any]:
        try:
            # Assuming running from root or similar structure
            config_path = os.path.join(os.getcwd(), "config", "settings.yaml")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    return yaml.safe_load(f) or {}
            else:
                logger.warning(f"Config file not found at {config_path}. Using defaults.")
                return {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    def _setup_tools(self):

        # Register tools
        tools = [
            MeasureMWTool(),
            MeasureFormulaTool(),
            Get13CNMRTool(),
            CalculateDBETool(),
            Get1HNMRTool(),
            CheckDataTool(),
            GetIRTool(),
            Get19FNMRTool(),
            Get31PNMRTool(),
            GetHRMSTool(),
            GetMSTool(),
            GetMeltingPointTool(),
            GetTLCTool(),
            GetOpticalRotationTool(),
        ]
        for tool in tools:
            if not registry.get_tool(tool.name):
                registry.register(tool)
        
        # Convert to LangChain tools for ToolNode
        self.lc_tools = [t.to_langchain_tool() for t in tools]
        self.tools_map = {t.name: t for t in self.lc_tools}

    def _setup_model(self):
        llm_config = self.config.get("llm", {})
        provider = llm_config.get("provider", "generic")

        try:
            from langchain_openai import ChatOpenAI
            from dotenv import load_dotenv
        except ImportError as e:
            raise RuntimeError("Missing dependency: langchain-openai / python-dotenv") from e

        load_dotenv()

        # Set default model based on provider
        default_model = "gpt-4o"
            
        model_name = llm_config.get("model_name", default_model)
        temperature = llm_config.get("temperature", 0)
        
        # Determine API credentials based on provider
        base_url = llm_config.get("base_url") or os.getenv("LLM_BASE_URL")
        api_key = llm_config.get("api_key") or os.getenv("LLM_API_KEY")
        
        if not api_key:
            logger.warning(f"API key for provider '{provider}' not found in environment variables (LLM_API_KEY). Model might fail.")

        logger.info(f"Loading {provider} model: {model_name}")
        
        planner_streaming = bool(llm_config.get("planner_streaming", False))
        final_streaming = bool(llm_config.get("final_streaming", llm_config.get("streaming", True)))

        seed = llm_config.get("seed")
        stop = llm_config.get("stop")
        enable_thinking = llm_config.get("enable_thinking", False)
        reasoning_effort = llm_config.get("reasoning_effort")

        if isinstance(seed, str) and seed.strip():
            try:
                seed = int(seed)
            except Exception:
                seed = None

        stop_sequences = None
        if isinstance(stop, str):
            stop_sequences = [stop] if stop.strip() else None
        elif isinstance(stop, list):
            normalized = [str(x).strip() for x in stop if str(x).strip()]
            stop_sequences = normalized or None

        def _construct_with_optional_kwargs(ctor, kwargs: Dict[str, Any], optional_keys: List[str]):
            pending = list(optional_keys)
            while True:
                try:
                    return ctor(**kwargs)
                except TypeError:
                    if not pending:
                        raise
                    kwargs.pop(pending.pop(0), None)

        def build_model(streaming: bool):
            # Check for Completion API override or auto-detect for specific models
            use_completion = self.config.get("llm", {}).get("use_completion_api", False)

            extra_body: Dict[str, Any] = {}
            if enable_thinking:
                extra_body["enable_thinking"] = True
                if reasoning_effort:
                     extra_body["reasoning_effort"] = str(reasoning_effort).strip()

            if use_completion:
                return CompletionChatAdapter(
                    model_name=model_name,
                    api_key=api_key,
                    base_url=base_url,
                    temperature=temperature,
                    stop=stop_sequences,
                    seed=seed,
                    **({"model_kwargs": {"extra_body": extra_body}} if extra_body else {})
                )

            kwargs = {
                "model": model_name,
                "api_key": api_key,
                "base_url": base_url,
                "streaming": streaming,
                "temperature": temperature,
            }
            if seed is not None:
                kwargs["seed"] = seed
            if stop_sequences is not None:
                kwargs["stop"] = stop_sequences
            if extra_body:
                kwargs["model_kwargs"] = {"extra_body": extra_body}

            return _construct_with_optional_kwargs(
                ChatOpenAI,
                kwargs,
                ["stop", "seed"],
            )

        self.model = build_model(planner_streaming).bind_tools(self.lc_tools)
        self.final_model = build_model(final_streaming)
        self.final_model_no_stream = build_model(False)

    def _render_tools_description(self) -> str:
        lines: List[str] = []
        for t in getattr(self, "lc_tools", []) or []:
            args_schema = getattr(t, "args_schema", None)
            if args_schema is not None and hasattr(args_schema, "model_fields"):
                arg_list = ", ".join(args_schema.model_fields.keys())
            else:
                arg_list = ""

            name = getattr(t, "name", "")
            description = getattr(t, "description", "") or ""
            if arg_list:
                lines.append(f"- {name}({arg_list}): {description}")
            else:
                lines.append(f"- {name}: {description}")

        return "\n".join(lines)

    def _get_initial_prompt(self, uuid: str) -> str:
        prompts_config = self.config.get("prompts", {})
        template = prompts_config.get("initial_prompt", "Analyze sample {uuid}")
        tools_description = self._render_tools_description()

        try:
            prompt = template.format(uuid=uuid, sample_id=uuid, tools_description=tools_description)
        except Exception:
            prompt = f"Analyze sample {uuid}"

        if "{tools_description}" in template:
            return prompt

        if tools_description:
            return f"{prompt}\n\nAvailable tools:\n{tools_description}"

        return prompt

    def _is_retryable_exception(self, exc: Exception) -> bool:
        if isinstance(exc, (httpx.RemoteProtocolError, httpx.TimeoutException, httpx.TransportError)):
            return True

        msg = str(exc) or ""
        if isinstance(exc, AttributeError) and "model_dump" in msg:
            return True

        if isinstance(exc, json.JSONDecodeError):
            return True

        if isinstance(exc, RuntimeError) and "NON_JSON_GATEWAY_RESPONSE" in msg:
            return True

        try:
            import openai
        except Exception:
            return False

        retry_types = tuple(
            t
            for t in (
                getattr(openai, "APIConnectionError", None),
                getattr(openai, "APITimeoutError", None),
                getattr(openai, "RateLimitError", None),
                getattr(openai, "InternalServerError", None),
            )
            if isinstance(t, type)
        )
        return bool(retry_types) and isinstance(exc, retry_types)

    def _invoke_model(self, messages, model_attr: str = "model"):
        llm_config = self.config.get("llm", {}) or {}
        max_attempts = int(llm_config.get("network_retry_attempts", 5))
        min_wait_s = float(llm_config.get("network_retry_min_wait_s", 2))
        max_wait_s = float(llm_config.get("network_retry_max_wait_s", 10))

        last_exc: Exception | None = None
        for attempt in range(1, max_attempts + 1):
            try:
                model = getattr(self, model_attr)
                if model is None:
                    raise RuntimeError(f"Model not initialized: {model_attr}")

                response = model.invoke(messages)

                if isinstance(response, str):
                    head = response[:200].replace("\n", "\\n")
                    logger.warning(
                        f"Model returned raw string (possible HTML login page / gateway intercept). "
                        f"model_attr={model_attr} len={len(response)} head_200={head!r}"
                    )
                    raise RuntimeError("NON_JSON_GATEWAY_RESPONSE")

                self._accumulate_token_usage(model_attr, response)
                return response
            except Exception as e:
                last_exc = e

                if isinstance(e, AttributeError) and "model_dump" in str(e):
                    logger.warning(
                        f"Model response parsing failed (possible HTML login page / gateway intercept). "
                        f"model_attr={model_attr} err={type(e).__name__}: {e}"
                    )
                elif isinstance(e, json.JSONDecodeError):
                    logger.warning(
                        f"Model response JSON decode failed (possible non-JSON body / gateway intercept). "
                        f"model_attr={model_attr} err={type(e).__name__}: {e}"
                    )

                if attempt >= max_attempts or not self._is_retryable_exception(e):
                    raise

                logger.warning(
                    f"Model request failed (attempt {attempt}/{max_attempts}): {type(e).__name__}: {e}"
                )
                try:
                    self._setup_model()
                except Exception as setup_err:
                    logger.warning(f"Model reset failed: {setup_err}")

                backoff_s = min(
                    max_wait_s,
                    max(min_wait_s, min_wait_s * (2 ** (attempt - 1))),
                )
                time.sleep(backoff_s + random.random() * 0.2)

        if last_exc is not None:
            raise last_exc

        model = getattr(self, model_attr)
        if model is None:
            raise RuntimeError(f"Model not initialized: {model_attr}")
        response = model.invoke(messages)
        self._accumulate_token_usage(model_attr, response)
        return response

    def _call_model(self, state: AgentState):
        logger.info("Agent reasoning...")

        response = self._invoke_model(state["messages"], model_attr="model")
        
        # Patch tool calls with IDs if missing
        if hasattr(response, "tool_calls") and response.tool_calls:
            import uuid
            # Create a copy of tool calls to avoid modifying original if it's immutable/cached
            tool_calls = []
            for i, tc in enumerate(response.tool_calls):
                new_tc = tc.copy()
                
                # 检测是否存在合并的 ID (例如 call_xxxcall_yyy)
                tc_id = new_tc.get("id", "")
                if tc_id and "call_" in tc_id and tc_id.count("call_") > 1:
                    logger.warning(f"Detected malformed tool_call id (merged?): {tc_id}. This usually happens with streaming=True on some providers.")

                if not new_tc.get("id"):
                    new_tc["id"] = f"call_{uuid.uuid4().hex[:8]}_{i}"
                tool_calls.append(new_tc)
            
            # Ensure content is not empty (Gemini/VertexAI requirement)
            content = response.content
            if not content:
                content = "I will use the tools to retrieve information."
                
            # Create a new AIMessage to ensure changes are applied
            response = AIMessage(
                content=content,
                tool_calls=tool_calls,
                additional_kwargs=response.additional_kwargs,
                id=response.id,
                response_metadata=response.response_metadata
            )
            
        if not getattr(response, "tool_calls", None):
            has_tool_messages = any(isinstance(m, ToolMessage) for m in state.get("messages", []) or [])
            if not has_tool_messages:
                import uuid

                tool_call_id = f"call_{uuid.uuid4().hex[:8]}_0"
                response = AIMessage(
                    content="I will use the tools to retrieve information.",
                    tool_calls=[
                        {
                            "name": "Check_Data",
                            "args": {"uuid": state.get("uuid")},
                            "id": tool_call_id,
                            "type": "tool_call",
                        }
                    ],
                )

        return {"messages": [response]}

    def _should_continue(self, state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]

        if not isinstance(last_message, AIMessage):
            return "agent"

        if last_message.tool_calls:
            logger.info(f"Agent decided to call tools: {last_message.tool_calls}")
            return "tools"

        logger.info("Agent finished planning.")
        return "final"

    def _call_final_model(self, state: AgentState):
        logger.info("Agent finalizing...")

        prompts_config = self.config.get("prompts", {}) or {}
        final_prompt = prompts_config.get(
            "final_prompt",
            "Based on the conversation and tool results above, provide the final conclusion directly. Do not call any tools.",
        )

        messages = list(state["messages"])
        messages.append(HumanMessage(content=final_prompt))

        try:
            response = self._invoke_model(messages, model_attr="final_model")
        except Exception as e:
            if not self._is_retryable_exception(e):
                raise
            response = self._invoke_model(messages, model_attr="final_model_no_stream")

        return {"messages": [response]}

    def _run_tools(self, state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]

        tool_messages = []
        if hasattr(last_message, "tool_calls"):
            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call.get("args")
                tool_call_id = tool_call["id"]

                if isinstance(tool_args, str):
                    try:
                        tool_args = json.loads(tool_args)
                    except Exception:
                        tool_args = {"_raw": tool_args}

                tool = self.tools_map.get(tool_name)
                if tool:
                    try:
                        result = tool.invoke(tool_args or {})
                        content = json.dumps({"result": result}, ensure_ascii=False)
                        status = "success"
                    except Exception as e:
                        content = json.dumps({"error": str(e)}, ensure_ascii=False)
                        status = "error"
                else:
                    content = json.dumps({"error": f"Tool {tool_name} not found."}, ensure_ascii=False)
                    status = "error"

                tool_messages.append(
                    ToolMessage(
                        content=content,
                        tool_call_id=tool_call_id,
                        name=tool_name,
                        status=status,
                    )
                )

        return {"messages": tool_messages}

    def run(self, uuid: str) -> Any:
        if not self.is_initialized:
            self.initialize()

        if self.graph is None:
            self._build_graph()

        self._reset_token_usage()

        initial_prompt = self._get_initial_prompt(uuid)

        initial_state = {
            "messages": [
                SystemMessage(content=initial_prompt),
                HumanMessage(content=f"Please start analyzing sample {uuid}."),
            ],
            "uuid": uuid,
            "known_data": {},
        }

        logger.info(f"Starting analysis for {uuid}")
        final_state = self.graph.invoke(initial_state)
        try:
            messages = final_state.get("messages", [])
            final_answer = None
            for msg in reversed(messages):
                if isinstance(msg, AIMessage):
                    final_answer = msg.content
                    break
            final_state["final_answer"] = final_answer
        except Exception:
            final_state["final_answer"] = None

        final_state["token_usage"] = getattr(self, "_token_usage", None)
        return final_state
