import os
import subprocess
import sys

def run_batch_evaluation():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    script_path = os.path.join(base_dir, "scripts/analyze/evaluate_predictions.py")
    ground_truth = os.path.join(base_dir, "data/molecules_final.json")
    
    results_dir = os.path.join(base_dir, "results/final")
    modes = ["agent", "baseline"]
    
    for mode in modes:
        mode_path = os.path.join(results_dir, mode)
        if not os.path.exists(mode_path):
            continue
            
        print(f"Processing {mode} models...")
        for model_name in os.listdir(mode_path):
            if model_name.startswith('.'): continue
            if model_name == 'plots': continue
            
            model_dir = os.path.join(mode_path, model_name)
            if not os.path.isdir(model_dir):
                continue
                
            # Input file: {model}_merged_runs.json
            input_json = os.path.join(model_dir, f"{model_name}_merged_runs.json")
            # Output file: {model}_evaluated.json
            output_json = os.path.join(model_dir, f"{model_name}_evaluated.json")
            # Report file: {model}_evaluation_report.md
            report_md = os.path.join(model_dir, f"{model_name}_evaluation_report.md")
            
            if not os.path.exists(input_json):
                print(f"  Skipping {model_name}: Input file not found")
                continue
                
            print(f"  Evaluating {model_name}...")
            cmd = [
                sys.executable, script_path,
                "--predictions", input_json,
                "--ground_truth", ground_truth,
                "--output-md", report_md,
                "--output-json", output_json
            ]
            
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
                print(f"    -> Saved to {os.path.basename(output_json)}")
            except subprocess.CalledProcessError as e:
                print(f"    -> Error evaluating {model_name}: {e}")

if __name__ == "__main__":
    run_batch_evaluation()