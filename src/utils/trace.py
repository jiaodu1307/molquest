import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from langchain_core.messages import AIMessage, ToolMessage
from src.core.logger import logger


def sanitize_filename_component(text: str) -> str:
    s = (text or "").strip()
    if not s:
        return "unknown"
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
    out_chars: List[str] = []
    for ch in s:
        out_chars.append(ch if ch in allowed else "_")
    normalized = "".join(out_chars)
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    return normalized.strip("_") or "unknown"


def write_json_file(path: str, data: Any, *, indent: int = 2) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
    os.replace(tmp_path, path)


def write_text_file(path: str, text: str) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp_path, path)

def _extract_json_object(text: str, start_index: int) -> str | None:
    if not text:
        return None

    left = text.find("{", start_index)
    if left < 0:
        return None

    depth = 0
    in_string = False
    escape = False

    for i in range(left, len(text)):
        ch = text[i]
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
            depth += 1
            continue

        if ch == "}":
            depth -= 1
            if depth == 0:
                return text[left : i + 1]

    return None

def normalize_final_answer(final_answer: Any) -> str:
    if isinstance(final_answer, list):
        parts: List[str] = []
        for x in final_answer:
            if isinstance(x, dict) and "text" in x:
                parts.append(str(x.get("text") or ""))
            else:
                parts.append(str(x))
        return "\n".join(parts).strip()

    if isinstance(final_answer, dict) and "text" in final_answer:
        return str(final_answer.get("text") or "").strip()

    return str(final_answer or "").strip()

def parse_final_result(final_answer: Any, fallback_uuid: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "uuid": fallback_uuid,
        "predicted_smiles": "UNKNOWN",
        "confidence": 0.0,
        "reason_brief": "",
    }

    text = normalize_final_answer(final_answer)
    if not text:
        return result

    marker_index = text.rfind("FINAL_RESULT_JSON")
    if marker_index >= 0:
        json_str = _extract_json_object(text, marker_index)
        if json_str:
            try:
                payload = json.loads(json_str)
                if isinstance(payload, dict):
                    result["uuid"] = str(payload.get("uuid") or result["uuid"])
                    result["predicted_smiles"] = str(payload.get("predicted_smiles") or result["predicted_smiles"])
                    try:
                        conf = float(payload.get("confidence"))
                    except Exception:
                        conf = result["confidence"]
                    result["confidence"] = max(0.0, min(1.0, conf))
                    result["reason_brief"] = str(payload.get("reason_brief") or result["reason_brief"])
                    return result
            except Exception:
                pass

    search_text = text
    final_marker = re.search(r"^\s*FINAL_RESULT\s*:\s*$", text, re.MULTILINE | re.IGNORECASE)
    if final_marker:
        search_text = text[final_marker.start() :]

    def _get_field(key: str) -> str | None:
        m = re.search(
            rf"^\s*(?:\*\*)?{re.escape(key)}(?:\*\*)?\s*:\s*(.+)\s*$",
            search_text,
            re.MULTILINE | re.IGNORECASE,
        )
        if not m:
            return None
        return (m.group(1) or "").strip().strip('"')

    uuid_val = _get_field("UUID")
    if uuid_val:
        result["uuid"] = uuid_val

    smiles_val = _get_field("PREDICTED_SMILES")
    if smiles_val:
        result["predicted_smiles"] = smiles_val

    conf_val = _get_field("CONFIDENCE")
    if conf_val:
        try:
            result["confidence"] = max(0.0, min(1.0, float(conf_val)))
        except Exception:
            pass

    reason_val = _get_field("REASON_BRIEF")
    if reason_val:
        result["reason_brief"] = reason_val

    return result

class TraceRecorder:
    def __init__(self):
        self.steps: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}

    @classmethod
    def from_state(cls, state: Dict[str, Any]) -> "TraceRecorder":
        recorder = cls()
        recorder.parse_state(state)
        return recorder

    def reset(self) -> None:
        self.steps = []
        self.metadata = {}

    def parse_state(self, state: Dict[str, Any]):
        self.reset()

        messages = state.get("messages", [])
        self.metadata = {
            "uuid": state.get("uuid"),
            "final_answer": state.get("final_answer"),
            "token_usage": state.get("token_usage"),
        }
        for i, msg in enumerate(messages):
            step = {
                "step": i,
                "type": msg.type,
                "content": msg.content,
            }
            if isinstance(msg, AIMessage) and msg.tool_calls:
                step["tool_calls"] = msg.tool_calls
            if isinstance(msg, ToolMessage):
                step["tool_call_id"] = msg.tool_call_id
                step["tool_name"] = getattr(msg, "name", None)
                step["tool_status"] = getattr(msg, "status", None)
            
            self.steps.append(step)
        
        logger.info(f"Recorded {len(self.steps)} steps in trace.")

    def to_trace_dict(self) -> Dict[str, Any]:
        return {
            "uuid": self.metadata.get("uuid"),
            "final_answer": self.metadata.get("final_answer"),
            "steps": self.steps,
        }

    def save_json(self, path: str) -> None:
        write_json_file(path, self.to_trace_dict(), indent=2)

    def save(self, trace_prefix: str) -> Dict[str, str]:
        json_path = f"{trace_prefix}.json"
        mermaid_path = f"{trace_prefix}.md"
        self.save_json(json_path)
        saved_mermaid_path = ""
        try:
            self.save_mermaid(mermaid_path)
            saved_mermaid_path = mermaid_path
        except Exception as e:
            logger.warning(f"Failed to save mermaid trace: {e}")
        return {"json_path": json_path, "mermaid_path": saved_mermaid_path}

    def _format_mermaid_label(self, text: Optional[str | list], max_chars: int) -> str:
        if isinstance(text, list):
            try:
                text = "\n".join(str(x) for x in text)
            except Exception:
                text = str(text)

        s = (text or "").replace("\r\n", "\n").replace("\r", "\n")
        s = " ".join(s.split())
        s = s.replace('"', "'").replace("[", "(").replace("]", ")")
        if len(s) > max_chars:
            return s[:max_chars] + "..."
        return s

    def to_mermaid(self, *, max_label_chars: int = 80) -> str:
        graph = ["graph TD"]
        for i, step in enumerate(self.steps):
            node_id = f"node_{i}"
            step_type = step.get("type")
            content = self._format_mermaid_label(step.get("content"), max_label_chars)
            
            if step_type == "human":
                graph.append(f"{node_id}[User: {content}]")
            elif step_type == "ai":
                tool_calls = step.get("tool_calls")
                if tool_calls:
                    calls = ", ".join([str(tc.get("name") or "") for tc in tool_calls])
                    calls = self._format_mermaid_label(calls, max_label_chars)
                    graph.append(f"{node_id}[AI: Call {calls}]")
                else:
                    graph.append(f"{node_id}[AI: {content}]")
            elif step_type == "tool":
                tool_name = self._format_mermaid_label(step.get("tool_name"), max_label_chars)
                tool_status = self._format_mermaid_label(step.get("tool_status"), max_label_chars)
                head = "Tool"
                if tool_name:
                    head += f": {tool_name}"
                if tool_status:
                    head += f" ({tool_status})"
                graph.append(f"{node_id}[{head}: {content}]")
            
            if i > 0:
                prev_id = f"node_{i-1}"
                graph.append(f"{prev_id} --> {node_id}")
        
        return "\n".join(graph)

    def save_mermaid(self, path: str):
        mermaid_content = self.to_mermaid()
        markdown = f"```mermaid\n{mermaid_content}\n```"
        write_text_file(path, markdown)


class RunArtifactsSaver:
    def __init__(self, *, trace_dir: str = "traces", run_dir: str = "runs"):
        self.trace_dir = trace_dir
        self.run_dir = run_dir

    def _build_trace_prefix(self, *, timestamp: str, model_tag: str, sample_uuid: str) -> str:
        return os.path.join(self.trace_dir, f"trace_{timestamp}_{model_tag}_{sample_uuid}")

    def _build_run_path(self, *, timestamp: str, model_tag: str, sample_uuid: str) -> str:
        filename = f"run_{timestamp}_{model_tag}_{sample_uuid}.json"
        return os.path.join(self.run_dir, filename)

    def save_run(
        self,
        *,
        sample_uuid: str,
        llm_config: Dict[str, Any],
        started_at: float,
        finished_at: float,
        result_state: Dict[str, Any],
        final_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        model_name = str((llm_config or {}).get("model_name") or "unknown")
        model_tag = sanitize_filename_component(model_name)

        trace_prefix = self._build_trace_prefix(
            timestamp=timestamp,
            model_tag=model_tag,
            sample_uuid=sample_uuid,
        )
        tracer = TraceRecorder.from_state(result_state)
        trace_paths = tracer.save(trace_prefix)
        logger.info(f"Trace saved to {trace_paths['json_path']} and {trace_paths['mermaid_path']}")

        duration_ms = int(max(0.0, finished_at - started_at) * 1000)
        record = {
            "uuid": sample_uuid,
            "created_at": datetime.now().isoformat(),
            "duration_ms": duration_ms,
            "llm": {
                "provider": (llm_config or {}).get("provider", "generic"),
                "model_name": (llm_config or {}).get("model_name", "unknown"),
                "temperature": (llm_config or {}).get("temperature"),
                "base_url": (llm_config or {}).get("base_url"),
            },
            "final_answer": result_state.get("final_answer"),
            "final_result": final_result,
            "token_usage": result_state.get("token_usage"),
            "trace_json_path": trace_paths["json_path"],
            "trace_mermaid_path": trace_paths["mermaid_path"],
        }

        run_path = self._build_run_path(
            timestamp=timestamp,
            model_tag=model_tag,
            sample_uuid=sample_uuid,
        )
        write_json_file(run_path, record, indent=2)
        logger.info(f"Run record saved to {run_path}")
        record["run_record_path"] = run_path
        return record
