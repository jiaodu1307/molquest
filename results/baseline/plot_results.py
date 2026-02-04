import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

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
    plt.rcParams['axes.spines.left'] = False # 仅保留底部轴线或完全无轴线，依靠网格
    
    # 网格线设置
    plt.rcParams['grid.color'] = '#E0E0E0'
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.alpha'] = 0.7

def get_model_colors(models):
    """
    生成高级感配色方案。
    使用 Seaborn 的 'mako' 调色板生成同色系渐变（蓝绿色调），
    既保持统一感，又有区分度。
    """
    unique_models = sorted(models.unique())
    # 使用 mako 调色板，颜色从深到浅
    palette = sns.color_palette("mako", n_colors=len(unique_models))
    
    colors = {}
    for i, model in enumerate(unique_models):
        colors[model] = palette[i]
    return colors

def plot_single_metric(df, metric_col, filename, ylabel, model_colors):
    """
    绘制单个指标的柱状图，优化视觉效果。
    """
    output_dir = Path(__file__).parent / 'plots'
    print(f"正在绘制: {metric_col} ...")
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # 排序数据
    df_sorted = df.sort_values(by=metric_col, ascending=False)
    models = df_sorted['Model']
    values = df_sorted[metric_col]
    
    # 获取对应颜色
    bar_colors = [model_colors[m] for m in models]
    
    # 绘制 (增加白色边框使柱子更清晰)
    bars = ax.bar(models, values, color=bar_colors, alpha=0.9, width=0.65, 
                  edgecolor='white', linewidth=1.5, zorder=3)
    
    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        label_text = f'{height:.4f}' if 'Average' in metric_col else f'{height:.2f}%'
        ax.text(bar.get_x() + bar.get_width()/2., height + (height * 0.01),
                label_text,
                ha='center', va='bottom', fontsize=11, fontweight='bold', color='#333333')
    
    # 设置标题和标签 (加粗)
    ax.set_title(f'Model Comparison: {metric_col}', fontsize=18, fontweight='bold', pad=25, color='#333333')
    ax.set_xlabel('Model', fontsize=14, fontweight='bold', labelpad=15, color='#333333')
    ax.set_ylabel(ylabel, fontsize=14, fontweight='bold', labelpad=15, color='#333333')
    
    # 坐标轴刻度样式
    plt.xticks(rotation=45, ha='right', fontsize=12, fontweight='bold', color='#555555')
    plt.yticks(fontsize=12, fontweight='bold', color='#555555')
    
    # 开启垂直网格 (zorder < 3 确保在柱子后面)
    ax.grid(axis='y', zorder=0)
    
    plt.tight_layout()
    
    save_path = output_dir / f'{filename}.png'
    plt.savefig(save_path, dpi=400, bbox_inches='tight')
    print(f"图表已保存至: {save_path}")
    plt.close()

def plot_combined_sim_conf(df, model_colors):
    """
    绘制合并图表，优化视觉效果。
    """
    output_dir = Path(__file__).parent / 'plots'
    print("正在绘制合并图表: Similarity & Confidence ...")
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 按 Similarity 排序
    df_sorted = df.sort_values(by='Average Similarity', ascending=False)
    models = df_sorted['Model']
    sim_values = df_sorted['Average Similarity']
    conf_values = df_sorted['Average Confidence']
    
    x = np.arange(len(models))
    width = 0.38
    
    bar_colors = [model_colors[m] for m in models]
    
    # 绘制 Similarity (实心，饱和度高)
    bars1 = ax.bar(x - width/2, sim_values, width, label='Similarity', 
                   color=bar_colors, alpha=1.0, edgecolor='white', linewidth=1.5, zorder=3)
    
    # 绘制 Confidence (带纹理，透明度高，产生层次感)
    # 使用白色纹理叠加
    bars2 = ax.bar(x + width/2, conf_values, width, label='Confidence', 
                   color=bar_colors, alpha=0.5, hatch='///', edgecolor='white', linewidth=1.5, zorder=3)
    
    # 添加数值标签
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.2f}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold', color='#444444', rotation=90)
            
    ax.set_title('Average Similarity vs Average Confidence', fontsize=18, fontweight='bold', pad=25, color='#333333')
    ax.set_xlabel('Model', fontsize=14, fontweight='bold', labelpad=15, color='#333333')
    ax.set_ylabel('Score (0-1)', fontsize=14, fontweight='bold', labelpad=15, color='#333333')
    
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=45, ha='right', fontsize=12, fontweight='bold', color='#555555')
    plt.yticks(fontsize=12, fontweight='bold', color='#555555')
    
    ax.set_ylim(0, 1.15)
    
    # 开启网格
    ax.grid(axis='y', zorder=0)
    
    # 自定义图例
    import matplotlib.patches as mpatches
    sim_patch = mpatches.Patch(facecolor='#666666', edgecolor='white', label='Average Similarity')
    conf_patch = mpatches.Patch(facecolor='#666666', alpha=0.5, hatch='///', edgecolor='white', label='Average Confidence')
    
    legend = ax.legend(handles=[sim_patch, conf_patch], loc='upper right', fontsize=12, frameon=True, fancybox=True, framealpha=0.9)
    plt.setp(legend.get_title(), fontweight='bold')
    
    plt.tight_layout()
    
    save_path = output_dir / 'combined_sim_conf.png'
    plt.savefig(save_path, dpi=400, bbox_inches='tight')
    print(f"图表已保存至: {save_path}")
    plt.close()

def plot_metrics():
    """
    读取 CSV 文件并绘制所有图表。
    """
    base_dir = Path(__file__).parent
    csv_file = base_dir / 'model_comparison.csv'
    output_dir = base_dir / 'plots'
    output_dir.mkdir(exist_ok=True)
    
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"读取 CSV 出错: {e}")
        return

    # 应用样式
    set_style()
    
    # 为每个模型分配颜色
    model_colors = get_model_colors(df['Model'])
    
    # 1. 绘制 Accuracy
    if 'Accuracy (%)' in df.columns:
        plot_single_metric(df, 'Accuracy (%)', 'accuracy', 'Accuracy (%)', model_colors)
        
    # 2. 绘制 Validity Rate
    if 'Validity Rate (%)' in df.columns:
        plot_single_metric(df, 'Validity Rate (%)', 'validity_rate', 'Validity Rate (%)', model_colors)
        
    # 3. 绘制 Combined Similarity & Confidence
    if 'Average Similarity' in df.columns and 'Average Confidence' in df.columns:
        plot_combined_sim_conf(df, model_colors)

    print("\n所有图表绘制完成！请查看 plots 文件夹。")

if __name__ == "__main__":
    try:
        plot_metrics()
    except ImportError:
        print("请安装必要库: pip install pandas matplotlib")