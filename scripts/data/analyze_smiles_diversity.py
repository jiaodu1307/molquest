import argparse
from pathlib import Path
import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from rdkit import Chem, DataStructs
from rdkit.Chem import Descriptors, AllChem, Draw
from rdkit.Chem.Scaffolds import MurckoScaffold
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import matplotlib.patches as mpatches

def load_data(filepath):
    """加载 JSON 数据"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return pd.DataFrame(data)

def calculate_properties(df):
    """计算理化性质"""
    mols = [Chem.MolFromSmiles(s) for s in df['smiles']]
    valid_mols = [m for m in mols if m is not None]

    props = {
        'MW': [Descriptors.MolWt(m) for m in valid_mols],
        'LogP': [Descriptors.MolLogP(m) for m in valid_mols],
        'TPSA': [Descriptors.TPSA(m) for m in valid_mols],
        'HBA': [Descriptors.NumHAcceptors(m) for m in valid_mols],
        'HBD': [Descriptors.NumHDonors(m) for m in valid_mols]
    }
    return pd.DataFrame(props), valid_mols

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = str(ROOT / "data/generated/diversity")

def plot_distributions(props_df):
    """绘制性质分布图 - 单独保存每张图"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 1. MW
    plt.figure(figsize=(8, 6))
    sns.histplot(props_df['MW'], kde=True, color='skyblue')
    plt.title('Molecular Weight Distribution')
    plt.xlabel('Molecular Weight')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'dist_MW.png'))
    plt.close()

    # 2. LogP
    plt.figure(figsize=(8, 6))
    sns.histplot(props_df['LogP'], kde=True, color='salmon')
    plt.title('LogP Distribution')
    plt.xlabel('LogP')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'dist_LogP.png'))
    plt.close()

    # 3. TPSA
    plt.figure(figsize=(8, 6))
    sns.histplot(props_df['TPSA'], kde=True, color='green')
    plt.title('TPSA Distribution')
    plt.xlabel('TPSA')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'dist_TPSA.png'))
    plt.close()

    # 4. HBA
    plt.figure(figsize=(8, 6))
    sns.histplot(props_df['HBA'], kde=False, color='orange', bins=10)
    plt.title('H-Bond Acceptors Distribution')
    plt.xlabel('H-Bond Acceptors')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'dist_HBA.png'))
    plt.close()

    # 5. HBD
    plt.figure(figsize=(8, 6))
    sns.histplot(props_df['HBD'], kde=False, color='purple', bins=10)
    plt.title('H-Bond Donors Distribution')
    plt.xlabel('H-Bond Donors')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'dist_HBD.png'))
    plt.close()

    print(f"Saved property distribution plots to {OUTPUT_DIR}")

def analyze_chemical_space(mols):
    """化学空间可视化 (PCA 2D & t-SNE 3D) - Publication Quality"""
    # 计算 Morgan 指纹
    fps = [AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=1024) for m in mols]
    X = np.array(fps)

    # --- 新增：K-Means 聚类 ---
    # 设定聚类数，例如 5 类，用于上色区分不同化学族群
    n_clusters = 5
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(X)

    # PCA (2D)
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(X)

    # t-SNE (3D)
    print("Running t-SNE (3D)... this may take a moment")
    # Remove n_iter as it might be causing issues in some sklearn versions or wrappers
    # Default is usually 1000 which is sufficient
    tsne = TSNE(n_components=3, random_state=42, perplexity=30)
    tsne_result = tsne.fit_transform(X)

    # 使用 seaborn 的配色方案
    palette = sns.color_palette("viridis", n_clusters)
    colors = [palette[c] for c in clusters]

    # Save PCA Plot
    plt.figure(figsize=(10, 8))
    # PCA 也使用聚类颜色
    plt.scatter(pca_result[:, 0], pca_result[:, 1], alpha=0.7, c=colors, s=50, edgecolors='w', linewidth=0.5)
    plt.title('Chemical Space (PCA - 2D)', fontsize=14)
    plt.xlabel('Principal Component 1', fontsize=12)
    plt.ylabel('Principal Component 2', fontsize=12)

    # 添加 PCA 图例
    legend_handles = [mpatches.Patch(color=palette[i], label=f'Cluster {i+1}') for i in range(n_clusters)]
    plt.legend(handles=legend_handles, title="Structural Clusters", loc='best')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'chemical_space_pca_2d_pub.png'), dpi=300)
    plt.close()

    # Save t-SNE Plot (High Quality)
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')

    # 绘制散点，使用聚类颜色
    ax.scatter(tsne_result[:, 0], tsne_result[:, 1], tsne_result[:, 2],
                     c=colors, s=40, alpha=0.8, edgecolors='w', linewidth=0.3)

    ax.set_title('Chemical Space Distribution (t-SNE)', fontsize=16, pad=20)
    ax.set_xlabel('t-SNE Dim 1', fontsize=12)
    ax.set_ylabel('t-SNE Dim 2', fontsize=12)
    ax.set_zlabel('t-SNE Dim 3', fontsize=12)

    # 添加 t-SNE 图例
    ax.legend(handles=legend_handles, title="Structural Clusters", loc='upper right')

    # 调整视角
    ax.view_init(elev=20, azim=45)

    plt.tight_layout()
    # 保存为高分辨率 PNG 和 PDF
    plt.savefig(os.path.join(OUTPUT_DIR, 'chemical_space_tsne_3d_pub.png'), dpi=300)
    plt.savefig(os.path.join(OUTPUT_DIR, 'chemical_space_tsne_3d_pub.pdf')) # PDF 适合插入论文
    plt.close()

    print(f"Saved publication-quality chemical space plots (PNG & PDF) to {OUTPUT_DIR}")

def analyze_similarity(mols, sample_size=1000):
    """相似度分析 (Tanimoto Similarity)"""
    print("\nStarting Similarity Analysis...")
    # 计算 Morgan 指纹
    fps = [AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=1024) for m in mols]

    # 如果数据集过大，进行采样以避免计算过慢
    if len(fps) > sample_size:
        print(f"Dataset size ({len(fps)}) > {sample_size}, sampling for visualization...")
        import random
        # 保持随机性一致
        random.seed(42)
        indices = sorted(random.sample(range(len(fps)), sample_size))
        fps_subset = [fps[i] for i in indices]
    else:
        fps_subset = fps

    n_mols = len(fps_subset)
    sim_matrix = np.zeros((n_mols, n_mols))

    print(f"Calculating similarity matrix for {n_mols} molecules...")
    for i in range(n_mols):
        # DataStructs.BulkTanimotoSimilarity 计算一个指纹与列表指纹的相似度
        sims = DataStructs.BulkTanimotoSimilarity(fps_subset[i], fps_subset)
        sim_matrix[i] = sims

    # 获取上三角矩阵的索引（不包含对角线）用于统计分布
    upper_tri_indices = np.triu_indices(n_mols, k=1)
    pairwise_sims = sim_matrix[upper_tri_indices]

    avg_sim = np.mean(pairwise_sims)
    print(f"Average Pairwise Tanimoto Similarity: {avg_sim:.4f}")

    # 1. 相似度分布图
    plt.figure(figsize=(10, 6))
    sns.histplot(pairwise_sims, kde=True, color='teal', bins=50)
    plt.title(f'Pairwise Tanimoto Similarity Distribution\nMean: {avg_sim:.3f}')
    plt.xlabel('Tanimoto Similarity')
    plt.ylabel('Count')
    plt.axvline(avg_sim, color='red', linestyle='--', label=f'Mean: {avg_sim:.2f}')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'similarity_distribution.png'))
    plt.close()

    # 2. 相似度热图
    plt.figure(figsize=(10, 8))
    sns.heatmap(sim_matrix, cmap='viridis', vmin=0, vmax=1, xticklabels=False, yticklabels=False)
    plt.title('Similarity Matrix Heatmap')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'similarity_heatmap.png'))
    plt.close()

    print(f"Saved similarity plots to {OUTPUT_DIR}")

def analyze_scaffolds(mols):
    """骨架分析"""
    scaffolds = {}
    for m in mols:
        try:
            core = MurckoScaffold.GetScaffoldForMol(m)
            smi = Chem.MolToSmiles(core)
            scaffolds[smi] = scaffolds.get(smi, 0) + 1
        except:
            pass

    sorted_scaffolds = sorted(scaffolds.items(), key=lambda x: x[1], reverse=True)

    print(f"\nTotal unique scaffolds: {len(scaffolds)}")
    print("Top 5 most common scaffolds:")
    for i, (smi, count) in enumerate(sorted_scaffolds[:5]):
        print(f"{i+1}. {smi}: {count}")

    # 可视化 Top Scaffolds
    top_n = 8
    top_scaffolds = sorted_scaffolds[:top_n]
    mols_to_draw = []
    legends = []

    for smi, count in top_scaffolds:
        mol = Chem.MolFromSmiles(smi)
        if mol:
            mols_to_draw.append(mol)
            legends.append(f"Count: {count}")

    if mols_to_draw:
        try:
            img = Draw.MolsToGridImage(mols_to_draw, molsPerRow=4, subImgSize=(300, 300), legends=legends)
            # RDKit Draw.MolsToGridImage returns a PIL image or saves to file depending on returnPNG
            # In recent versions it returns a PIL image by default if returnPNG=False is not set?
            # Actually, let's just save it.
            # If it's a PIL image:
            if hasattr(img, 'save'):
                img.save(os.path.join(OUTPUT_DIR, 'top_scaffolds.png'))
            else:
                # If it's raw data (older rdkit versions sometimes), write bytes
                with open(os.path.join(OUTPUT_DIR, 'top_scaffolds.png'), 'wb') as f:
                    f.write(img.data)
            print(f"Saved top_scaffolds.png to {OUTPUT_DIR}")
        except Exception as e:
            print(f"Failed to save scaffold image: {e}")

def main():
    global OUTPUT_DIR
    parser = argparse.ArgumentParser(description="Analyze molecular dataset diversity.")
    parser.add_argument("--input", type=Path, default=ROOT / "data/molecules_final.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/generated/diversity")
    args = parser.parse_args()
    OUTPUT_DIR = str(args.output_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    filepath = args.input
    print(f"Loading data from {filepath}...")
    df = load_data(filepath)
    print(f"Loaded {len(df)} molecules.")

    print("Calculating properties...")
    props_df, valid_mols = calculate_properties(df)

    print("Plotting property distributions...")
    plot_distributions(props_df)

    print("Analyzing chemical space...")
    analyze_chemical_space(valid_mols)

    analyze_similarity(valid_mols)

    print("Analyzing scaffolds...")
    analyze_scaffolds(valid_mols)

    print("\nAnalysis complete.")

if __name__ == "__main__":
    main()
