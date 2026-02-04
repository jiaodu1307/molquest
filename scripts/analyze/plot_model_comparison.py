import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
import json
import numpy as np
from typing import List, Tuple, Dict, Any, Optional

try:
    from rdkit import Chem
    from rdkit import DataStructs
    from rdkit.Chem import AllChem
    from rdkit import RDLogger
    # Silence RDKit warnings/errors
    RDLogger.DisableLog('rdApp.*')
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    print("Warning: RDKit not found. Similarity calculations will default to 0.0.", file=sys.stderr)

def calculate_similarity(smiles1: str, smiles2: str) -> float:
    """
    Calculate Tanimoto similarity between two SMILES strings using Morgan fingerprints.
    Returns 0.0 if RDKit is unavailable or parsing fails.
    """
    if not RDKIT_AVAILABLE or not smiles1 or not smiles2:
        return 0.0

    try:
        mol1 = Chem.MolFromSmiles(smiles1)
        mol2 = Chem.MolFromSmiles(smiles2)
        if mol1 is None or mol2 is None:
            return 0.0
        
        fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, 2, nBits=2048)
        fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, 2, nBits=2048)
        
        return DataStructs.TanimotoSimilarity(fp1, fp2)
    except Exception:
        return 0.0

def calculate_rmsce_value(conf_sim_pairs: List[Tuple[float, float]], n_bins: int = 10) -> float:
    """
    Calculate Root Mean Square Calibration Error (RMSCE) using Similarity.
    RMSCE = sqrt( sum( (n_b/N) * (avg_sim_b - avg_conf_b)^2 ) )
    """
    if not conf_sim_pairs:
        return 0.0
        
    confs = np.array([p[0] for p in conf_sim_pairs])
    sims = np.array([p[1] for p in conf_sim_pairs])
    
    # Define bins (0.0 to 1.0)
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    
    # Digitize confidences
    # right=True: bins[i-1] < x <= bins[i]
    binids = np.digitize(confs, bins, right=True)
    
    rmsce_sq = 0.0
    total_samples = len(confs)
    
    # Iterate over all bins present in the data
    unique_bins = np.unique(binids)
    for b in unique_bins:
        mask = binids == b
        if np.sum(mask) > 0:
            avg_conf = np.mean(confs[mask])
            avg_sim = np.mean(sims[mask])
            n_b = np.sum(mask)
            
            rmsce_sq += (n_b / total_samples) * ((avg_sim - avg_conf) ** 2)
            
    return np.sqrt(rmsce_sq)

def get_rmsce_for_model(row, base_dir, ground_truth_map):
    """
    Helper to calculate RMSCE for a single model/mode row.
    Prioritizes reading from {model}_evaluated.json if it exists (contains pre-calculated similarity).
    Falls back to {model}_merged_runs.json and calculating similarity on the fly.
    """
    model = row['Model']
    mode = row['Mode'] # 'Agent' or 'Baseline'
    
    mode_dir = mode.lower()
    model_dir_path = os.path.join(base_dir, f"results/final/{mode_dir}/{model}")
    
    # 1. Try loading pre-evaluated results (with similarity)
    evaluated_json_path = os.path.join(model_dir_path, f"{model}_evaluated.json")
    if os.path.exists(evaluated_json_path):
        try:
            with open(evaluated_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            conf_sim_pairs = []
            for item in data:
                # In evaluated json, we expect 'confidence' and 'similarity' fields
                # Check structure: evaluate_predictions.py saves list of dicts with keys:
                # "uuid", "match", "valid", "similarity", "confidence", ...
                conf = item.get('confidence', 0.0)
                sim = item.get('similarity', 0.0)
                # Ensure valid entries
                if conf is not None and sim is not None:
                    conf_sim_pairs.append((float(conf), float(sim)))
            
            if conf_sim_pairs:
                print(f"  Using pre-calculated similarity for {model} ({len(conf_sim_pairs)} items)")
                return calculate_rmsce_value(conf_sim_pairs)
        except Exception as e:
            print(f"  Error reading {evaluated_json_path}: {e}. Falling back to raw data.")

    # 2. Fallback: Load merged runs and calculate similarity
    json_path = os.path.join(model_dir_path, f"{model}_merged_runs.json")
    
    if not os.path.exists(json_path):
        print(f"Warning: JSON not found at {json_path}")
        return np.nan
        
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {json_path}: {e}")
        return np.nan
        
    # Extract (conf, sim) pairs
    conf_sim_pairs = []
    for item in data:
        uuid = item.get('uuid')
        # Skip if uuid not in ground truth
        if not uuid or uuid not in ground_truth_map:
            continue
            
        final_result = item.get('final_result', {})
        if not final_result:
             continue

        confidence = final_result.get('confidence', 0.0)
        predicted_smiles = final_result.get('predicted_smiles')
        true_smiles = ground_truth_map[uuid].get('smiles')
        
        sim = calculate_similarity(predicted_smiles, true_smiles)
        conf_sim_pairs.append((confidence, sim))
        
    if not conf_sim_pairs:
        return np.nan
        
    return calculate_rmsce_value(conf_sim_pairs)

def set_style():
    """配置全局绘图样式，提升视觉质感"""
    # 尝试使用更现代的样式
    styles = ['seaborn-v0_8-whitegrid', 'seaborn-whitegrid', 'bmh']
    for style in styles:
        try:
            plt.style.use(style)
            break
        except:
            continue
            
    # 全局字体配置
    plt.rcParams['font.family'] = 'sans-serif'
    # 优先使用无衬线字体
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans', 'sans-serif']
    
    # 去除多余边框
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.spines.left'] = False 
    
    # 网格线设置
    plt.rcParams['grid.color'] = '#E0E0E0'
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.alpha'] = 0.7

def plot_comparison():
    """
    读取 Agent 和 Baseline 的对比数据，并生成可视化图表
    """
    # 定义文件路径
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    agent_csv = os.path.join(base_dir, "results/final/agent/model_comparison.csv")
    baseline_csv = os.path.join(base_dir, "results/final/baseline/model_comparison.csv")
    output_dir = os.path.join(base_dir, "plots/comparsion")

    # 检查文件是否存在
    if not os.path.exists(agent_csv) or not os.path.exists(baseline_csv):
        print(f"错误: 找不到输入 CSV 文件。\n检查路径:\n{agent_csv}\n{baseline_csv}")
        return

    # 读取数据
    print("正在读取数据...")
    try:
        df_agent = pd.read_csv(agent_csv)
        df_baseline = pd.read_csv(baseline_csv)
    except Exception as e:
        print(f"读取 CSV 文件失败: {e}")
        return

    # 添加模式列以区分来源 (Agent vs Baseline)
    df_agent['Mode'] = 'Agent'
    df_baseline['Mode'] = 'Baseline'

    # 合并数据
    df_combined = pd.concat([df_agent, df_baseline], ignore_index=True)

    # ---------------------------------------------------------
    # Calculate RMSCE (Root Mean Square Calibration Error)
    # ---------------------------------------------------------
    print("Calculating RMSCE (Confidence vs Similarity)...")
    
    # Load Ground Truth
    gt_path = os.path.join(base_dir, "data/processed/molecules_version_3_0113.json")
    if os.path.exists(gt_path):
        try:
            with open(gt_path, 'r', encoding='utf-8') as f:
                gt_data = json.load(f)
            # Map uuid -> item
            gt_map = {item['uuid']: item for item in gt_data}
            
            # Apply calculation
            # We use a lambda or loop. Since we need base_dir and gt_map, loop is easier or apply with args.
            # Using apply is cleaner
            df_combined['RMSCE'] = df_combined.apply(
                lambda row: get_rmsce_for_model(row, base_dir, gt_map), axis=1
            )
        except Exception as e:
            print(f"Failed to calculate RMSCE: {e}")
            df_combined['RMSCE'] = np.nan
    else:
        print(f"Ground truth file not found at {gt_path}. Skipping RMSCE.")
        df_combined['RMSCE'] = np.nan

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 设置绘图风格
    set_style()
    
    # Define metrics to plot
    # Accuracy (%): Accuracy
    # Validity Rate (%): Validity Rate
    # Average Similarity: Average Similarity
    # Parsing Errors: Parsing Errors
    # RMSCE: RMS Calibration Error (Confidence vs Similarity)
    metrics = [
        'Accuracy (%)', 
        'Validity Rate (%)', 
        'Average Similarity', 
        'Parsing Errors',
        'RMSCE'
    ]

    # Generate a consistent color palette for all models
    # Ensure each model has a unique fixed color across all charts
    unique_models = sorted(df_combined['Model'].unique())
    # Use 'mako' palette but skip the darkest colors to avoid "black-like" appearance
    n_models = len(unique_models)
    # Generate extra colors to allow skipping the darkest ones
    # Skipping first 3 shades usually avoids the near-black tones
    total_colors = n_models + 3 
    full_palette = sns.color_palette("mako", n_colors=total_colors)
    # Slice to take the lighter portion (skip the first 3 darkest)
    base_palette = full_palette[3:]
    model_color_map = {model: base_palette[i] for i, model in enumerate(unique_models)}

    # Generate separate plots for each metric
    for metric in metrics:
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # 1. Determine Sort Order
        # Pivot to sort by Agent values for the current metric
        temp_df = df_combined[['Model', 'Mode', metric]].copy()
        try:
            pivot = temp_df.pivot(index='Model', columns='Mode', values=metric)
            if 'Agent' in pivot.columns:
                # Sort descending. Handle NaNs if any (put at end)
                sorted_models = pivot.sort_values(by='Agent', ascending=False, na_position='last').index.tolist()
            else:
                sorted_models = unique_models
        except Exception as e:
            print(f"Sorting failed for {metric}: {e}")
            sorted_models = unique_models

        # 2. Plot Bar Chart
        # We set hue_order to ensure Agent is first, then Baseline
        hue_order = ['Agent', 'Baseline']
        
        # Note: We don't use 'palette' here because we will manually color the bars
        # We pass a dummy palette or just let it be, then override.
        sns.barplot(
            data=df_combined,
            x='Model',
            y=metric,
            hue='Mode',
            hue_order=hue_order,
            order=sorted_models,
            ax=ax,
            edgecolor='white',
            linewidth=1.5
        )
        
        # 3. Apply Custom Colors (Same Hue, Different Opacity)
        # Iterate through the containers (groups of bars)
        # container[0] -> Agent (due to hue_order)
        # container[1] -> Baseline
        
        for i, container in enumerate(ax.containers):
            # Determine mode based on container index
            is_agent = (i == 0) 
            
            for j, bar in enumerate(container):
                # j corresponds to the index in sorted_models
                if j < len(sorted_models):
                    model_name = sorted_models[j]
                    color = model_color_map.get(model_name, (0.5, 0.5, 0.5))
                    
                    # Apply color
                    bar.set_facecolor(color)
                    
                    # Apply opacity/shading
                    if is_agent:
                        bar.set_alpha(1.0)
                    else:
                        bar.set_alpha(0.4) # Lighter/Transparent for Baseline
                        # Optional: Add hatch for Baseline to distinguish further
                        # bar.set_hatch('///') 

        # 4. Add Value Labels
        for container in ax.containers:
             labels = []
             for v in container.datavalues:
                 if pd.isna(v):
                     labels.append("")
                     continue
                     
                 if v < 1.1 and ('Similarity' in metric or 'RMSCE' in metric): 
                     labels.append(f'{v:.3f}')
                 elif 'Errors' in metric:
                     labels.append(f'{int(v)}')
                 else:
                     labels.append(f'{v:.1f}')
             
             ax.bar_label(container, labels=labels, padding=3, fontsize=9, fontweight='bold', color='#333333')
        
        # Set titles and labels in English with bold font
        ax.set_title(f'Model Comparison: {metric}', fontsize=18, fontweight='bold', pad=25, color='#333333')
        ax.set_xlabel('Model', fontsize=14, fontweight='bold', labelpad=15, color='#333333')
        ax.set_ylabel(metric, fontsize=14, fontweight='bold', labelpad=15, color='#333333')
        
        # Rotate x-axis labels
        ax.set_xticks(range(len(sorted_models)))
        ax.set_xticklabels(sorted_models, rotation=45, ha='right', fontsize=12, fontweight='bold', color='#555555')
        ax.tick_params(axis='y', labelsize=12, labelcolor='#555555')
        
        # Optimize legend
        # Create custom legend handles to show "Agent" vs "Baseline" style
        from matplotlib.patches import Patch
        legend_handles = [
            Patch(facecolor='gray', alpha=1.0, edgecolor='white', label='Agent'),
            Patch(facecolor='gray', alpha=0.4, edgecolor='white', label='Baseline')
        ]
        ax.legend(handles=legend_handles, title='Mode', loc='upper right', frameon=True, fancybox=True, framealpha=0.9)
        
        plt.tight_layout()
        
        # Save individual plot
        # Create a safe filename from the metric name
        safe_metric_name = metric.replace(' (%)', '').replace(' ', '_').lower()
        output_path = os.path.join(output_dir, f'comparison_{safe_metric_name}.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close() # Close the figure to free memory
        print(f"Saved plot to: {output_path}")

    # Generate pivot table for detailed comparison
    pivot_df = df_combined.pivot(index='Model', columns='Mode', values=metrics)
    pivot_csv_path = os.path.join(output_dir, 'model_comparison_pivot.csv')
    pivot_df.to_csv(pivot_csv_path)
    print(f"Pivot table saved to: {pivot_csv_path}")

    # Generate Scientific Three-Line Table (Image & LaTeX)
    save_scientific_table(df_combined, output_dir)

    # Generate Delta Plots (Improvement/Regression)
    plot_delta_charts(df_combined, metrics, model_color_map, output_dir)

def plot_delta_charts(df, metrics, model_color_map, output_dir):
    """
    Generate charts showing the difference (Delta) between Agent and Baseline.
    Models with improvement are on the left, models with regression are on the right.
    """
    print("\nGenerating Delta (Improvement) charts...")
    
    for metric in metrics:
        # Pivot to get Agent and Baseline columns
        temp_df = df[['Model', 'Mode', metric]].copy()
        try:
            pivot = temp_df.pivot(index='Model', columns='Mode', values=metric)
            if 'Agent' not in pivot.columns or 'Baseline' not in pivot.columns:
                print(f"Skipping delta plot for {metric}: missing data columns.")
                continue
                
            # Calculate Delta (Improvement)
            # For 'Parsing Errors' and 'RMSCE', lower is better, so Improvement = Baseline - Agent
            # For others, higher is better, so Improvement = Agent - Baseline
            if 'Errors' in metric or 'RMSCE' in metric:
                pivot['Delta'] = pivot['Baseline'] - pivot['Agent']
                ylabel_text = f'Improvement in {metric}\n(Baseline - Agent, Higher is Better)'
                title_suffix = "(Reduction in Error)"
            else:
                pivot['Delta'] = pivot['Agent'] - pivot['Baseline']
                ylabel_text = f'Improvement in {metric}\n(Agent - Baseline)'
                title_suffix = ""

            # Sort by Delta descending (Improved on left, Regressed on right)
            pivot = pivot.sort_values(by='Delta', ascending=False)
            
            # Plot
            fig, ax = plt.subplots(figsize=(14, 8))
            
            models = pivot.index.tolist()
            deltas = pivot['Delta'].tolist()
            colors = [model_color_map.get(m, '#333333') for m in models]
            
            # Create bars
            bars = ax.bar(models, deltas, color=colors, edgecolor='white', linewidth=1)
            
            # Add a horizontal line at 0
            ax.axhline(0, color='#444444', linewidth=1.5, linestyle='-')
            
            # Add value labels
            for bar, delta in zip(bars, deltas):
                height = bar.get_height()
                # Position label above positive bars and below negative bars
                xy_pos = (bar.get_x() + bar.get_width() / 2, height)
                text_xytext = (0, 3) if height >= 0 else (0, -12)
                
                label_val = f"{delta:+.1f}"
                if 'Similarity' in metric or 'RMSCE' in metric:
                    label_val = f"{delta:+.3f}"
                elif 'Errors' in metric:
                    label_val = f"{delta:+.0f}"
                    
                ax.annotate(label_val,
                            xy=xy_pos,
                            xytext=text_xytext,
                            textcoords="offset points",
                            ha='center', va='bottom',
                            fontsize=10, fontweight='bold', color='#333333')

            # Formatting
            safe_metric_name = metric.replace(' (%)', '')
            ax.set_title(f'Performance Delta: {safe_metric_name} {title_suffix}\n(Left: Empowered, Right: Challenged)', 
                         fontsize=16, fontweight='bold', pad=20, color='#333333')
            ax.set_xlabel('Model', fontsize=14, fontweight='bold', labelpad=15, color='#333333')
            ax.set_ylabel(ylabel_text, fontsize=14, fontweight='bold', labelpad=15, color='#333333')
            
            ax.set_xticks(range(len(models)))
            ax.set_xticklabels(models, rotation=45, ha='right', fontsize=12, fontweight='bold', color='#555555')
            
            # Add grid only on y-axis
            ax.grid(axis='y', linestyle='--', alpha=0.5)
            ax.grid(axis='x', visible=False)
            
            plt.tight_layout()
            
            # Save
            safe_metric_filename = metric.replace(' (%)', '').replace(' ', '_').lower()
            output_path = os.path.join(output_dir, f'delta_{safe_metric_filename}.png')
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"Saved delta plot to: {output_path}")
            
        except Exception as e:
            print(f"Failed to generate delta plot for {metric}: {e}")

def save_scientific_table(df, output_dir):
    """
    Generates a scientific 'three-line table' suitable for academic papers.
    Outputs both a PNG image and LaTeX code.
    """
    print("\nGenerating scientific three-line table...")
    
    # 1. Prepare Data
    # We select key metrics
    metrics_map = {
        'Accuracy (%)': 'Acc',
        'Validity Rate (%)': 'Valid',
        'Average Similarity': 'Sim',
        'RMSCE': 'RMSCE'
    }
    
    # Filter and rename
    cols = ['Model', 'Mode'] + list(metrics_map.keys())
    temp = df[cols].copy()
    temp = temp.rename(columns=metrics_map)
    
    # Pivot: Index=Model, Columns=(Metric, Mode)
    pivot = temp.pivot(index='Model', columns='Mode')
    
    # Sort by Agent Accuracy (descending)
    if ('Acc', 'Agent') in pivot.columns:
        pivot = pivot.sort_values(by=('Acc', 'Agent'), ascending=False)
        
    # Reorder columns to group by Metric: Acc(Base, Agent), Valid(Base, Agent)...
    new_cols = []
    for metric_short in metrics_map.values():
        new_cols.append((metric_short, 'Baseline'))
        new_cols.append((metric_short, 'Agent'))
        
    # Select and reorder
    pivot = pivot[new_cols]
    
    # 2. Generate LaTeX Code (Standard Booktabs format)
    latex_path = os.path.join(output_dir, 'model_comparison_table.tex')
    try:
        # Use simple format for numbers
        # Check if jinja2 is available implicitly via to_latex
        pivot.to_latex(latex_path, float_format="%.2f", multirow=True, caption="Model Performance Comparison: Baseline vs Agent")
        print(f"LaTeX Table code saved to: {latex_path}")
    except Exception as e:
        print(f"Standard to_latex failed ({e}). Using fallback method...")
        try:
            # Fallback: Manual LaTeX generation
            with open(latex_path, 'w') as f:
                f.write("\\begin{table}\n")
                f.write("\\centering\n")
                f.write("\\caption{Model Performance Comparison: Baseline vs Agent}\n")
                f.write("\\begin{tabular}{l" + "rr" * len(metrics_map) + "}\n")
                f.write("\\toprule\n")
                
                # Header
                header_top = " & " + " & ".join([f"\\multicolumn{{2}}{{c}}{{{m}}}" for m in metrics_map.values()]) + " \\\\\n"
                header_bottom = "Model & " + " & ".join(["Base & Agent"] * len(metrics_map)) + " \\\\\n"
                
                f.write(header_top)
                f.write("\\cmidrule(lr){2-3} \\cmidrule(lr){4-5} \\cmidrule(lr){6-7}\n") # Adjust based on number of metrics
                f.write(header_bottom)
                f.write("\\midrule\n")
                
                # Rows
                for idx, row in pivot.iterrows():
                    row_str = f"{idx}"
                    for val in row:
                        if pd.isna(val):
                            row_str += " & -"
                        else:
                            row_str += f" & {val:.2f}"
                    row_str += " \\\\\n"
                    f.write(row_str)
                    
                f.write("\\bottomrule\n")
                f.write("\\end{tabular}\n")
                f.write("\\end{table}\n")
            print(f"LaTeX Table code saved (fallback) to: {latex_path}")
        except Exception as e2:
             print(f"Fallback LaTeX generation also failed: {e2}")

    # 3. Generate Image (Matplotlib) simulation of Three-Line Table
    # Flatten columns for display: "Acc (Base)", "Acc (Agent)"...
    display_df = pivot.copy()
    display_df.columns = [f"{m} ({'B' if mode=='Baseline' else 'A'})" for m, mode in pivot.columns]
    display_df = display_df.reset_index() # Make Model a column
    
    # Setup plot
    rows = len(display_df)
    cols = len(display_df.columns)
    fig, ax = plt.subplots(figsize=(cols * 1.5, rows * 0.4 + 1))
    ax.axis('off')
    
    # Create table
    # Cell text formatting
    cell_text = []
    for idx, row in display_df.iterrows():
        row_txt = []
        for col in display_df.columns:
            val = row[col]
            if isinstance(val, float):
                row_txt.append(f"{val:.2f}")
            else:
                row_txt.append(str(val))
        cell_text.append(row_txt)
        
    mpl_table = ax.table(cellText=cell_text,
                         colLabels=display_df.columns,
                         loc='center',
                         cellLoc='center',
                         edges='open') # 'open' removes most borders, we add lines manually
    
    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(10)
    mpl_table.scale(1, 1.5)
    
    # Add Three Lines (Top, Header-Bottom, Bottom)
    # Get table extent
    # Note: This is a visual approximation. 
    # For perfect "three-line", we rely on the LaTeX output, but we try to make the PNG look good.
    
    # Iterate cells to set borders
    # Row 0 is header
    # Rows 1..N are data
    
    for (row, col), cell in mpl_table.get_celld().items():
        cell.set_linewidth(0) # Clear all defaults
        
        # Header (Row 0): Top line (thick), Bottom line (thin)
        if row == 0:
            cell.visible_edges = 'TB'
            cell.set_edgecolor('black')
            cell.set_linewidth(1.5) # Top
            # Note: matplotlib table cells handle one linewidth. 
            # To get different widths (Thick Top, Thin Bottom for header), it's tricky.
            # We will just use standard lines.
            
        # Last Row: Bottom line (thick)
        elif row == rows:
            cell.visible_edges = 'B'
            cell.set_edgecolor('black')
            cell.set_linewidth(1.5)
    
    # Refine Header Bottom Line (Row 0 bottom should be distinct)
    # Matplotlib table edge control is limited per cell.
    # Drawing manual lines is better for "Three-Line" look.
    
    # Reset styles to simpler approach for image
    # We will just use 'horizontal' lines logic if we could, but let's stick to simple "visible_edges"
    # Re-loop to simplify
    for (row, col), cell in mpl_table.get_celld().items():
        cell.set_linewidth(0)
        if row == 0: # Header
            cell.set_text_props(weight='bold')
            # Top of header
            # Bottom of header
    
    # Draw lines manually using plot coordinates
    # Table coordinates: (0,0) is bottom left? No.
    # We can use ax.axhline but need correct y-coords.
    # It's easier to let the user use the LaTeX for the paper and this PNG for quick preview.
    # We will just add a title and save.
    
    plt.title("Scientific Table Preview (See .tex for Paper)", y=1.0, pad=20, fontweight='bold')
    
    img_path = os.path.join(output_dir, 'model_comparison_table.png')
    plt.savefig(img_path, dpi=300, bbox_inches='tight')
    print(f"Scientific table image saved to: {img_path}")
    plt.close()

if __name__ == "__main__":
    try:
        plot_comparison()
    except ImportError as e:
        print("缺少必要的 Python 库。请运行以下命令安装：")
        print("pip install pandas matplotlib seaborn")
    except Exception as e:
        print(f"发生未知错误: {e}")