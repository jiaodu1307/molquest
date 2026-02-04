#!/usr/bin/env python3
import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


UUID_RE = re.compile(
    r"[0-9a-fA-F]{8}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{12}"
)


@dataclass(frozen=True)
class RunInfo:
    path: str
    created_at: str
    completed: bool
    parse_error: bool


def extract_uuid(text: str) -> Optional[str]:
    m = UUID_RE.search(text)
    return m.group(0).lower() if m else None


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_molecules(molecules_json: Path) -> Dict[str, str]:
    data = load_json(molecules_json)
    if isinstance(data, dict):
        if "molecules" in data and isinstance(data["molecules"], list):
            items = data["molecules"]
        else:
            raise ValueError(f"不支持的 molecules.json 结构：{molecules_json}")
    elif isinstance(data, list):
        items = data
    else:
        raise ValueError(f"不支持的 molecules.json 顶层类型：{type(data).__name__}")

    uuid_to_name: Dict[str, str] = {}
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        uuid = item.get("uuid")
        if not isinstance(uuid, str) or not uuid.strip():
            continue
        name = item.get("molecule_name")
        uuid_to_name[uuid.lower()] = name if isinstance(name, str) and name.strip() else f"<unknown:{idx}>"
    return uuid_to_name


def is_completed_run(obj: Any) -> bool:
    if not isinstance(obj, dict):
        return False
    final_result = obj.get("final_result")
    if not isinstance(final_result, dict):
        return False
    predicted_smiles = final_result.get("predicted_smiles")
    if not isinstance(predicted_smiles, str) or not predicted_smiles.strip():
        return False
    return True


def scan_runs(runs_dir: Path) -> Tuple[Dict[str, List[RunInfo]], List[str]]:
    runs_by_uuid: Dict[str, List[RunInfo]] = defaultdict(list)
    orphan_files: List[str] = []

    for path in sorted(runs_dir.glob("*.json")):
        if not path.is_file():
            continue

        uuid_from_name = extract_uuid(path.name)
        try:
            obj = load_json(path)
            uuid = obj.get("uuid") if isinstance(obj, dict) else None
            uuid = uuid.lower() if isinstance(uuid, str) and uuid.strip() else uuid_from_name
            if not uuid:
                orphan_files.append(str(path))
                continue

            created_at = obj.get("created_at") if isinstance(obj, dict) else ""
            created_at = created_at if isinstance(created_at, str) else ""
            runs_by_uuid[uuid].append(
                RunInfo(
                    path=str(path),
                    created_at=created_at,
                    completed=is_completed_run(obj),
                    parse_error=False,
                )
            )
        except Exception:
            uuid = uuid_from_name
            if not uuid:
                orphan_files.append(str(path))
                continue
            runs_by_uuid[uuid].append(
                RunInfo(
                    path=str(path),
                    created_at="",
                    completed=False,
                    parse_error=True,
                )
            )

    return runs_by_uuid, orphan_files


def summarize(
    uuid_to_name: Dict[str, str],
    runs_by_uuid: Dict[str, List[RunInfo]],
) -> Dict[str, Any]:
    molecule_uuids = set(uuid_to_name.keys())
    run_uuids = set(runs_by_uuid.keys())

    not_started = sorted(molecule_uuids - run_uuids)

    not_completed: List[str] = []
    duplicated_completed: List[str] = []

    for uuid in sorted(molecule_uuids & run_uuids):
        runs = runs_by_uuid.get(uuid, [])
        completed_cnt = sum(1 for r in runs if r.completed)
        if completed_cnt == 0:
            not_completed.append(uuid)
        if completed_cnt > 1:
            duplicated_completed.append(uuid)

    return {
        "counts": {
            "molecules_total": len(molecule_uuids),
            "runs_uuid_total": len(run_uuids),
            "not_started": len(not_started),
            "not_completed": len(not_completed),
            "duplicated_completed": len(duplicated_completed),
        },
        "not_started": not_started,
        "not_completed": not_completed,
        "duplicated_completed": duplicated_completed,
    }


def format_one(uuid: str, uuid_to_name: Dict[str, str], runs_by_uuid: Dict[str, List[RunInfo]]) -> str:
    name = uuid_to_name.get(uuid, "<unknown>")
    runs = runs_by_uuid.get(uuid, [])
    completed_cnt = sum(1 for r in runs if r.completed)
    parse_err_cnt = sum(1 for r in runs if r.parse_error)
    created_ats = [r.created_at for r in runs if r.created_at]
    created_ats = created_ats[:3]
    created_at_part = f", created_at[:3]={created_ats}" if created_ats else ""
    return f"{uuid} | {name} | runs={len(runs)}, completed={completed_cnt}, parse_error={parse_err_cnt}{created_at_part}"


def print_section(
    title: str,
    uuids: Iterable[str],
    uuid_to_name: Dict[str, str],
    runs_by_uuid: Dict[str, List[RunInfo]],
    max_show: int,
) -> None:
    uuids = list(uuids)
    print(f"\n== {title} ({len(uuids)}) ==")
    show = uuids if max_show < 0 else uuids[:max_show]
    for u in show:
        print(format_one(u, uuid_to_name, runs_by_uuid))
    if max_show >= 0 and len(uuids) > max_show:
        print(f"... 省略 {len(uuids) - max_show} 条，可用 --max-show -1 显示全部")


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--molecules",
        default="data/molecules_final.json",
    )
    parser.add_argument(
        "--runs-dir",
        default="runs_qwen3-max",
    )
    parser.add_argument("--max-show", type=int, default=50)
    parser.add_argument("--show-details", action="store_true")
    args = parser.parse_args(argv)

    molecules_json = Path(args.molecules)
    runs_dir = Path(args.runs_dir)

    uuid_to_name = load_molecules(molecules_json)
    runs_by_uuid, orphan_files = scan_runs(runs_dir)
    summary = summarize(uuid_to_name, runs_by_uuid)

    counts = summary["counts"]
    print("== 汇总 ==")
    for k in ["molecules_total", "runs_uuid_total", "not_started", "not_completed", "duplicated_completed"]:
        print(f"{k}: {counts[k]}")

    if orphan_files:
        print(f"\n== 注意：发现 {len(orphan_files)} 个无法解析/不含 uuid 的 run 文件（前 10 个）==")
        for p in orphan_files[:10]:
            print(p)

    if args.show_details:
        print_section("没有任何 run 文件（未开始）", summary["not_started"], uuid_to_name, runs_by_uuid, args.max_show)
        print_section("存在 run 文件但没有完成（final_result 缺失或 predicted_smiles 为空/解析失败）", summary["not_completed"], uuid_to_name, runs_by_uuid, args.max_show)
        print_section("重复完成（同一 uuid 有 >1 个 completed run）", summary["duplicated_completed"], uuid_to_name, runs_by_uuid, args.max_show)

    has_problem = (counts["not_started"] + counts["not_completed"] + counts["duplicated_completed"]) > 0
    return 2 if has_problem else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))