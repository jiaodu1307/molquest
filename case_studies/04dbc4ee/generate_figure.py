import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.gridspec import GridSpec
import textwrap
import os

# Configuration
base_dir = "case_studies/04dbc4ee"
output_file = os.path.join(base_dir, "comparison_figure.png")

# Data
data = [
    {
        "title": "Ground Truth",
        "image": os.path.join(base_dir, "true.png"),
        "smiles": "C[C@H](NC(=O)[C@H](CC(=O)OC(C)(C)C)NC(=O)OC(C)(C)C)C(=O)OC(C)(C)C",
        "color": "black",
        "metrics": "Target Structure"
    },
    {
        "title": "Gemini-3-Flash",
        "image": os.path.join(base_dir, "gemini-3-flash_pred.png"),
        "smiles": "CC(C)(C)OC(=O)N[C@@H](CC(=O)OC(C)(C)C)C(=O)N[C@@H](C)C(=O)OC(C)(C)C",
        "color": "green",
        "metrics": "Status: Success | Sim: 1.00"
    },
    {
        "title": "Kimi-K2-Thinking",
        "image": os.path.join(base_dir, "kimi-k2_pred.png"),
        "smiles": "CC(NC(=O)OC(C)(C)C)C(=O)NC(C(=O)OC(C)(C)C)C(C)OC(C)(C)C",
        "color": "red",
        "metrics": "Status: Failure | Sim: 0.46"
    }
]

# Create Figure
fig = plt.figure(figsize=(18, 8))
gs = GridSpec(1, 3, figure=fig)

for i, item in enumerate(data):
    ax = fig.add_subplot(gs[0, i])
    
    # Load and display image
    try:
        img = mpimg.imread(item["image"])
        ax.imshow(img)
    except FileNotFoundError:
        ax.text(0.5, 0.5, "Image Not Found", ha='center', va='center')
    
    ax.axis('off')
    
    # Title
    ax.set_title(item["title"], fontsize=16, fontweight='bold', color=item["color"], pad=20)
    
    # Metrics
    ax.text(0.5, -0.05, item["metrics"], transform=ax.transAxes, 
            ha='center', fontsize=14, fontweight='bold', color=item["color"])
    
    # SMILES
    wrapped_smiles = "\n".join(textwrap.wrap(item["smiles"], width=40))
    ax.text(0.5, -0.15, wrapped_smiles, transform=ax.transAxes, 
            ha='center', va='top', fontsize=10, family='monospace',
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.5))

plt.tight_layout()
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"Figure saved to {output_file}")
