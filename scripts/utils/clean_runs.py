import os
import json
import glob
import argparse

def clean_empty_runs(directory, dry_run=False):
    """
    清理指定目录下 final_answer 为空的 JSON 文件及其关联的 trace 文件
    """
    # 转换为绝对路径以确保安全
    directory = os.path.abspath(directory)
    # 获取目录下所有的 json 文件
    json_files = glob.glob(os.path.join(directory, "*.json"))
    # 假设项目根目录是 directory 的上两级 (nmr-agent/)
    project_root = os.path.dirname(os.path.dirname(directory))
    
    deleted_count = 0
    prefix = "[预览] " if dry_run else ""
    print(f"{prefix}开始扫描目录: {directory}")
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查 final_answer 是否为空字符串
            if data.get("final_answer") == "":
                print(f"\n{prefix}发现空结果: {os.path.basename(file_path)}")
                
                # 尝试删除关联的 trace 文件
                for trace_key in ["trace_json_path", "trace_mermaid_path"]:
                    trace_rel_path = data.get(trace_key)
                    if trace_rel_path:
                        trace_abs_path = os.path.join(project_root, trace_rel_path)
                        if os.path.exists(trace_abs_path):
                            if not dry_run:
                                os.remove(trace_abs_path)
                                print(f"  - 已删除关联 trace: {trace_rel_path}")
                            else:
                                print(f"  - [待删除] 关联 trace: {trace_rel_path}")

                # 删除 run 文件本身
                if not dry_run:
                    os.remove(file_path)
                    print(f"  - 已删除 run 文件")
                else:
                    print(f"  - [待删除] run 文件")
                
                deleted_count += 1
                
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
            
    result_msg = "预览完成" if dry_run else "清理完成"
    count_msg = "发现" if dry_run else "删除了"
    print(f"\n{result_msg}。共 {count_msg} {deleted_count} 个空运行记录及其关联文件。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="清理 final_answer 为空的运行记录文件及其关联的 trace 文件")
    parser.add_argument(
        "directory", 
        nargs="?", 
        default="runs/runs_glm-4.7",
        help="要清理的目录路径 (默认: runs/runs_glm-4.7)"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="预览模式：只显示将要删除的文件，不执行实际删除操作"
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"错误: 目录不存在 - {args.directory}")
    else:
        clean_empty_runs(args.directory, args.dry_run)