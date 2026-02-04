import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configuration
METRICS_CSV = Path("paper_metrics_results.csv")
COMPARISON_CSV = Path("results/final/agent/model_comparison.csv")
OUTPUT_DIR = Path("paper_plots")
OUTPUT_DIR.mkdir(exist_ok=True)

def load_data():
    if not METRICS_CSV.exists():
        print(f"Error: {METRICS_CSV} not found.")
        return None
    
    if not COMPARISON_CSV.exists():
        print(f"Error: {COMPARISON_CSV} not found.")
        return None

    # Load metrics (Avg Rnds, Avg IG)
    df_metrics = pd.read_csv(METRICS_CSV)
    
    # Load comparison (Accuracy)
    df_comp = pd.read_csv(COMPARISON_CSV)
    
    # Clean model names if necessary (trim whitespace)
    df_metrics['model'] = df_metrics['model'].str.strip()
    df_comp['Model'] = df_comp['Model'].str.strip()
    
    # Merge
    # df_metrics uses 'model', df_comp uses 'Model'
    df_merged = pd.merge(df_metrics, df_comp, left_on='model', right_on='Model', how='inner')
    
    return df_merged

def plot_pareto(df):
    plt.figure(figsize=(10, 8))
    sns.set_style("whitegrid")
    
    # X: Avg Rounds (Efficiency - lower is better? or just descriptive)
    # Y: Accuracy (%) (Effectiveness - higher is better)
    
    x = df['avg_rounds']
    y = df['Accuracy (%)']
    models = df['model']
    
    # Scatter plot
    plt.scatter(x, y, color='b', alpha=0.7, edgecolors='k', s=100)
    
    # Label points
    for i, model in enumerate(models):
        plt.annotate(model, (x[i], y[i]), xytext=(5, 5), textcoords='offset points', fontsize=9)
        
    plt.title('Efficiency-Effectiveness Pareto Frontier Analysis', fontsize=14)
    plt.xlabel('Average Solution Rounds (Efficiency)', fontsize=12)
    plt.ylabel('Final Structure Accuracy (%) (Effectiveness)', fontsize=12)
    
    # Invert X axis if "Efficiency" means fewer rounds is "more efficient" (visual preference)
    # But standard Pareto plots often have "Cost" on X (lower is better) and "Benefit" on Y.
    # Sometimes it's better to keep X increasing.
    # The user said: "X-axis as Average Solution Rounds (efficiency), Y-axis as Final Structure Accuracy (effectiveness)."
    # I'll keep it standard increasing.
    
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'pareto_frontier.png', dpi=300)
    print(f"Saved pareto_frontier.png to {OUTPUT_DIR}")
    plt.close()

def plot_ig_scores(df):
    plt.figure(figsize=(12, 6))
    sns.set_style("whitegrid")
    
    # Sort by IG Score descending
    df_sorted = df.sort_values('avg_ig', ascending=False)
    
    sns.barplot(x='model', y='avg_ig', data=df_sorted, palette='viridis')
    plt.title('Information-Gain-Weighted Score by Model', fontsize=14)
    plt.xlabel('Model', fontsize=12)
    plt.ylabel('Avg IG Score', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'ig_scores.png', dpi=300)
    print(f"Saved ig_scores.png to {OUTPUT_DIR}")
    plt.close()

def plot_rounds(df):
    plt.figure(figsize=(12, 6))
    sns.set_style("whitegrid")
    
    # Sort by Rounds ascending (fewer is better/more efficient)
    df_sorted = df.sort_values('avg_rounds', ascending=True)
    
    sns.barplot(x='model', y='avg_rounds', data=df_sorted, palette='rocket')
    plt.title('Average Solution Rounds by Model', fontsize=14)
    plt.xlabel('Model', fontsize=12)
    plt.ylabel('Avg Rounds', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'avg_rounds.png', dpi=300)
    print(f"Saved avg_rounds.png to {OUTPUT_DIR}")
    plt.close()

def main():
    df = load_data()
    if df is None or df.empty:
        print("No data to plot.")
        return

    print("Data loaded successfully. Models:", len(df))
    print(df[['model', 'avg_rounds', 'avg_ig', 'Accuracy (%)']])

    plot_pareto(df)
    plot_ig_scores(df)
    plot_rounds(df)

if __name__ == "__main__":
    main()
