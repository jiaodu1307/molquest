import os
import json
import math
import csv
from pathlib import Path
import statistics

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
AGENT_RESULTS_DIR = PROJECT_ROOT / "results/final/agent"
OUTPUT_CSV = Path("paper_metrics_results.csv")
GAMMA = 0.95  # Discount factor for IG Score

# Predefined Information Gain (Hypothetical values for demonstration)
IG_MAP = {
    "Measure_MW": 0.3,
    "Measure_Formula": 0.5,
    "Calculate_DBE": 0.2,
    "Get_1H_NMR": 0.9,
    "Get_13C_NMR": 0.8,
    "Get_IR": 0.2,
    "Get_19F_NMR": 0.3,
    "Get_31P_NMR": 0.3,
    "Get_HRMS": 0.3,
    "Check_Data": 0,
    "default": 0
}

def calculate_metrics_for_model(model_name):
    model_dir = AGENT_RESULTS_DIR / model_name
    traces_dir = model_dir / "traces"
    
    if not traces_dir.exists():
        print(f"[{model_name}] Traces directory not found.")
        return None

    results = {
        "total_cases": 0,
        "rounds_list": [],
        "ig_scores": []
    }

    # Iterate over trace files (using json files as source of truth for traces)
    trace_files = list(traces_dir.glob("*.json"))
    results["total_cases"] = len(trace_files)
    
    print(f"[{model_name}] Processing {len(trace_files)} traces...")

    for trace_file in trace_files:
        try:
            with open(trace_file, 'r') as f:
                trace_data = json.load(f)
            
            # 2. Strategic Decision Efficiency
            steps = trace_data.get("steps", [])
            
            # Count interaction rounds (AI steps that called tools)
            # Filter steps where 'tool_calls' is present
            interaction_steps = [s for s in steps if s.get("type") == "ai" and s.get("tool_calls")]
            num_rounds = len(interaction_steps)
            
            results["rounds_list"].append(num_rounds)

            # 3. Information Gain Score
            # S = sum(Ig(t) * gamma^(t-1))
            # Flatten tool calls sequence
            tool_sequence = []
            for step in interaction_steps:
                for tool_call in step.get("tool_calls", []):
                    tool_sequence.append(tool_call["name"])
            
            score = 0.0
            for t, tool_name in enumerate(tool_sequence):
                ig = IG_MAP.get(tool_name, IG_MAP["default"])
                score += ig * (GAMMA ** t)
            
            results["ig_scores"].append(score)

        except Exception as e:
            # print(f"Error processing {trace_file.name}: {e}")
            pass

    return results

def main():
    summary_data = []

    print(f"{'Model':<25} | {'Avg Rnds':<8} | {'Avg IG':<8}")
    print("-" * 50)

    for model_name in sorted(os.listdir(AGENT_RESULTS_DIR)):
        if model_name.startswith('.'): continue
        if not (AGENT_RESULTS_DIR / model_name).is_dir(): continue
        
        metrics = calculate_metrics_for_model(model_name)
        if not metrics or metrics["total_cases"] == 0:
            continue
            
        avg_rounds = statistics.mean(metrics["rounds_list"]) if metrics["rounds_list"] else 0
        avg_ig = statistics.mean(metrics["ig_scores"]) if metrics["ig_scores"] else 0
        
        print(f"{model_name:<25} | {avg_rounds:<8.2f} | {avg_ig:<8.2f}")
        
        summary_data.append({
            "model": model_name,
            "avg_rounds": avg_rounds,
            "avg_ig": avg_ig
        })

    # Save to CSV
    if summary_data:
        keys = summary_data[0].keys()
        with open(OUTPUT_CSV, 'w', newline='') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(summary_data)
        print(f"\nResults saved to {OUTPUT_CSV.absolute()}")

if __name__ == "__main__":
    main()
