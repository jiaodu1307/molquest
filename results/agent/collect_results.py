import os
import csv
import re
from pathlib import Path
from typing import Dict, List, Optional

# 定义要提取的字段模式
# 使用正则表达式匹配 markdown 文件中的统计数据
PATTERNS = {
    'Accuracy': r"- \*\*Accuracy\*\*: ([\d\.]+)% \((\d+)/(\d+)\)",
    'Validity Rate': r"- \*\*Validity Rate\*\*: ([\d\.]+)% \((\d+)/(\d+)\)",
    'Average Similarity': r"- \*\*Average Similarity\*\*: ([\d\.]+)",
    'Average Confidence': r"- \*\*Average Confidence\*\*: ([\d\.]+)",
    'Parsing Errors': r"- \*\*Parsing Errors\*\*: (\d+)"
}

def extract_metrics(content: str) -> Dict[str, str]:
    """
    从文件内容中提取各项指标数据。
    
    Args:
        content: markdown 文件的内容字符串
        
    Returns:
        包含提取指标的字典
    """
    metrics = {}
    
    # 提取准确率 (Accuracy)
    acc_match = re.search(PATTERNS['Accuracy'], content)
    if acc_match:
        metrics['Accuracy (%)'] = acc_match.group(1)
        metrics['Accuracy (Count)'] = acc_match.group(2)
        metrics['Total Samples'] = acc_match.group(3)
    
    # 提取有效率 (Validity Rate)
    val_match = re.search(PATTERNS['Validity Rate'], content)
    if val_match:
        metrics['Validity Rate (%)'] = val_match.group(1)
        metrics['Valid Samples'] = val_match.group(2)
        
    # 提取平均相似度 (Average Similarity)
    sim_match = re.search(PATTERNS['Average Similarity'], content)
    if sim_match:
        metrics['Average Similarity'] = sim_match.group(1)
        
    # 提取平均置信度 (Average Confidence)
    conf_match = re.search(PATTERNS['Average Confidence'], content)
    if conf_match:
        metrics['Average Confidence'] = conf_match.group(1)
        
    # 提取解析错误数 (Parsing Errors)
    err_match = re.search(PATTERNS['Parsing Errors'], content)
    if err_match:
        metrics['Parsing Errors'] = err_match.group(1)
        
    return metrics

def process_report_file(file_path: Path) -> Optional[Dict[str, str]]:
    """
    处理单个报告文件，读取并解析内容。
    
    Args:
        file_path: 报告文件的路径对象
        
    Returns:
        包含模型名称和指标数据的字典，如果读取失败则返回 None
    """
    try:
        # 获取模型名称，优先使用父文件夹名称作为模型标识
        # 例如: .../claude-haiku-4_5/report.md -> claude-haiku-4_5
        model_name = file_path.parent.name
        
        content = file_path.read_text(encoding='utf-8')
        metrics = extract_metrics(content)
        
        # 将模型名称添加到结果中
        metrics['Model'] = model_name
        return metrics
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
        return None

def main():
    """
    主函数：遍历目录，收集数据并保存为 CSV。
    """
    # 设定基础目录为当前脚本所在目录
    base_dir = Path(__file__).parent
    output_file = base_dir / 'model_comparison.csv'
    
    results = []
    
    # 遍历所有子目录寻找以 _evaluation_report.md 结尾的文件
    # 使用 glob 模式匹配
    report_files = list(base_dir.glob('**/*_evaluation_report.md'))
    
    print(f"找到 {len(report_files)} 个报告文件。开始处理...")
    
    for file_path in report_files:
        data = process_report_file(file_path)
        if data:
            results.append(data)
            
    if not results:
        print("未找到有效数据。")
        return

    # 定义 CSV 的列头顺序
    fieldnames = [
        'Model', 
        'Accuracy (%)', 'Accuracy (Count)', 'Total Samples',
        'Validity Rate (%)', 'Valid Samples',
        'Average Similarity', 
        'Average Confidence', 
        'Parsing Errors'
    ]
    
    # 写入 CSV 文件
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"统计完成！结果已保存至: {output_file}")
    except IOError as e:
        print(f"写入 CSV 文件失败: {e}")

if __name__ == "__main__":
    main()