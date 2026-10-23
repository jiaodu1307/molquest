import argparse
from pathlib import Path
import json
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from rdkit import Chem
from collections import Counter

# 配置输出目录
ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = str(ROOT / "data/generated/stats")

def load_data(filepath):
    print(f"Loading data from {filepath}...")
    with open(filepath, 'r') as f:
        data = json.load(f)
    return pd.DataFrame(data)

def analyze_completeness(df):
    """分析数据完整性"""
    print("\n--- Data Completeness Analysis ---")

    # 基础字段检查
    basic_fields = ['molecule_name', 'smiles', 'molecular_formula', 'molecular_weight', 'inchi', 'inchi_key']
    stats = {field: df[field].notna().sum() for field in basic_fields if field in df.columns}

    # 动态统计 raw_data 中的所有字段
    raw_data_counts = Counter()

    for _, row in df.iterrows():
        raw = row.get('raw_data')
        if isinstance(raw, dict):
            for key, value in raw.items():
                if value:  # 只有非空值才统计
                    raw_data_counts[key] += 1

    stats.update(raw_data_counts)
    total = len(df)

    # 打印报告
    report = []
    report.append(f"Total Molecules: {total}")
    report.append("-" * 30)
    report.append(f"{'Field':<30} | {'Count':<8} | {'Coverage':<8}")
    report.append("-" * 30)

    completeness_data = []
    # 按数量降序排列
    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)

    for field, count in sorted_stats:
        percent = (count / total) * 100
        report.append(f"{field:<30} | {count:<8} | {percent:.1f}%")
        completeness_data.append({'Field': field, 'Count': count, 'Percentage': percent})

    print("\n".join(report))

    # 绘图 - 只绘制覆盖率 > 1% 的字段，避免图表过大
    plt.figure(figsize=(14, 8))
    plot_data = [d for d in completeness_data if d['Percentage'] > 1.0]
    comp_df = pd.DataFrame(plot_data)

    if not comp_df.empty:
        sns.barplot(data=comp_df, x='Field', y='Percentage', palette='viridis')
        plt.title('Data Completeness / Coverage (Fields > 1%)')
        plt.ylabel('Coverage (%)')
        plt.xticks(rotation=45, ha='right') # 旋转标签以防重叠
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'completeness.png'))
    plt.close()

    return completeness_data

def extract_nmr_metadata(df):
    """从 1H NMR 文本中提取溶剂和频率"""
    print("\n--- NMR Metadata Extraction (Solvent & Frequency) ---")

    solvents = []
    frequencies = []

    # 正则表达式
    # 匹配常见的溶剂格式，如 CDCl3, DMSO-d6, Acetone-d6, D2O, Methanol-d4
    solvent_pattern = re.compile(r'\b(CDCl3|DMSO|DMSO-d6|CD3OD|MeOD|Acetone-d6|D2O|C6D6|CD2Cl2)\b', re.IGNORECASE)
    # 匹配频率，如 300 MHz, 400 MHz, 500MHz
    freq_pattern = re.compile(r'(\d{3})\s*MHz', re.IGNORECASE)

    for _, row in df.iterrows():
        raw = row.get('raw_data')
        if isinstance(raw, dict):
            h_nmr = raw.get('1H_NMR')
            if h_nmr and isinstance(h_nmr, str):
                # 提取溶剂
                s_match = solvent_pattern.search(h_nmr)
                if s_match:
                    # 统一格式，例如 meod -> MeOD
                    s_norm = s_match.group(1).upper()
                    if 'DMSO' in s_norm: s_norm = 'DMSO-d6'
                    if 'MEOD' in s_norm or 'CD3OD' in s_norm: s_norm = 'MeOD'
                    if 'ACETONE' in s_norm: s_norm = 'Acetone-d6'
                    solvents.append(s_norm)

                # 提取频率
                f_match = freq_pattern.search(h_nmr)
                if f_match:
                    frequencies.append(f_match.group(1) + " MHz")

    # 统计并绘图
    plot_categorical_counts(solvents, 'NMR Solvents Distribution (Top 10)', 'nmr_solvents.png')
    plot_categorical_counts(frequencies, 'NMR Frequency Distribution', 'nmr_frequencies.png')

    # 准备返回的统计数据
    meta_stats = []
    total = len(df)

    def collect_top_stats(data_list, prefix):
        if not data_list: return
        counter = Counter(data_list)
        # 取前10个
        for item, count in counter.most_common(10):
            percent = (count / total) * 100
            meta_stats.append({
                'Field': f"{prefix}: {item}",
                'Count': count,
                'Percentage': percent
            })

    collect_top_stats(solvents, "Solvent")
    collect_top_stats(frequencies, "Frequency")

    return meta_stats

def plot_categorical_counts(data_list, title, filename, top_n=10):
    if not data_list:
        print(f"No data found for {title}")
        return

    counter = Counter(data_list)
    common = counter.most_common(top_n)

    labels, counts = zip(*common)

    print(f"\n{title}:")
    for l, c in common:
        print(f"  {l}: {c}")

    plt.figure(figsize=(10, 6))
    sns.barplot(x=list(labels), y=list(counts), palette='rocket')
    plt.title(title)
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename))
    plt.close()

def analyze_elements(df):
    """元素组成分析"""
    print("\n--- Elemental Composition Analysis ---")

    element_counts = Counter()
    total_mols = 0

    for smiles in df['smiles']:
        if not isinstance(smiles, str): continue

        mol = Chem.MolFromSmiles(smiles)
        if mol:
            total_mols += 1
            atoms = set([atom.GetSymbol() for atom in mol.GetAtoms()])
            for atom in atoms:
                element_counts[atom] += 1

    # 转换为百分比
    element_stats = []
    print(f"Analyzed {total_mols} valid molecules.")
    print("Element presence (% of molecules containing the element):")

    # 排序：常见有机元素在前，其他按频率
    priority_elements = ['C', 'H', 'N', 'O', 'S', 'F', 'Cl', 'Br', 'I', 'P']

    for elem in priority_elements:
        if elem in element_counts:
            count = element_counts[elem]
            pct = (count / total_mols) * 100
            print(f"  {elem}: {pct:.1f}% ({count})")
            element_stats.append({'Field': elem, 'Count': count, 'Percentage': pct})
            del element_counts[elem] # 移除已处理的

    # 处理剩余元素
    for elem, count in element_counts.most_common():
        pct = (count / total_mols) * 100
        print(f"  {elem}: {pct:.1f}% ({count})")
        element_stats.append({'Field': elem, 'Count': count, 'Percentage': pct})

    # 绘图
    plt.figure(figsize=(12, 6))
    e_df = pd.DataFrame(element_stats)
    sns.barplot(data=e_df, x='Field', y='Percentage', color='steelblue')
    plt.title('Elemental Composition (% of molecules containing element)')
    plt.ylabel('Percentage (%)')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'elemental_composition.png'))
    plt.close()

    return element_stats

def main():
    global OUTPUT_DIR
    parser = argparse.ArgumentParser(description="Analyze molecular dataset stats.")
    parser.add_argument("--input", type=Path, default=ROOT / "data/molecules_final.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/generated/stats")
    args = parser.parse_args()
    OUTPUT_DIR = str(args.output_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    filepath = args.input
    df = load_data(filepath)

    comp_stats = analyze_completeness(df)
    nmr_stats = extract_nmr_metadata(df)
    elem_stats = analyze_elements(df)

    # 汇总所有统计数据到 CSV
    all_stats = []

    # 1. 数据完整性
    for item in comp_stats:
        item['Category'] = 'Data Completeness'
        all_stats.append(item)

    # 2. NMR 元数据 (溶剂/频率)
    for item in nmr_stats:
        item['Category'] = 'NMR Metadata'
        all_stats.append(item)

    # 3. 元素组成
    for item in elem_stats:
        item['Category'] = 'Elemental Composition'
        all_stats.append(item)

    # 创建 DataFrame 并保存
    if all_stats:
        stats_df = pd.DataFrame(all_stats)
        # 调整列顺序
        cols = ['Category', 'Field', 'Count', 'Percentage']
        # 确保列存在 (防止某些情况下字段缺失)
        cols = [c for c in cols if c in stats_df.columns]
        stats_df = stats_df[cols]

        csv_path = os.path.join(OUTPUT_DIR, 'dataset_stats_summary.csv')
        stats_df.to_csv(csv_path, index=False)
        print(f"\nDetailed statistics saved to: {csv_path}")

    print(f"\nAll statistics plots saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
