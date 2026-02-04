import os
import json
import asyncio
import re
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TRACE_DIR = os.path.join(PROJECT_ROOT, "traces", "traces_gpt-52")
BASE_URL = os.getenv("IDEALAB_BASE_URL") or "https://idealab.alibaba-inc.com/api/openai/v1"
API_KEY = os.getenv("IDEALAB_API_KEY")
MODEL_NAME = "qwen3-max"  # Use a capable model for analysis
CONCURRENCY_LIMIT = 10    # [设置] 在这里修改并发数 (Concurrency Limit)
OUTPUT_FILE = "scan_results.json" # [设置] 结果保存文件路径

async def check_file(sem, llm, file_path):
    async with sem:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            final_answer = data.get("final_answer", "")
            # Extract text from final_answer structure
            if isinstance(final_answer, list):
                texts = [item.get('text', '') for item in final_answer if isinstance(item, dict)]
                text = "\n".join(texts)
            elif isinstance(final_answer, str):
                text = final_answer
            else:
                return None

            if not text.strip():
                return None

            # Construct Prompt
            prompt = f"""
            请分析以下文本（这是AI针对化学结构推导的回答），判断其结论主要是通过“逻辑推理”（根据提供的波谱数据逐步推导结构）得出的，还是通过“记忆比对”（直接检索已知数据库、文献或通过与现有数据比对吻合，暗示模型可能记住了该分子）得出的。

            文本内容：
            {text[:8000]} 

            请严格只返回一个合法的 JSON 对象，格式如下：
            {{
                "is_memory": true,  // 如果是记忆比对/检索/直接给出已知结论则为 true，纯逻辑推理为 false
                "reason": "简述判断理由（30字以内）"
            }}
            不要包含 Markdown 标记（如 ```json ... ```）。
            """

            response = await llm.ainvoke([HumanMessage(content=prompt)])
            content = response.content.strip()
            
            # Clean up markdown if present
            if content.startswith("```"):
                # Remove first line (```json) and last line (```)
                lines = content.split('\n')
                if len(lines) >= 2:
                    content = "\n".join(lines[1:-1])
                content = content.replace("```", "").strip()
            
            try:
                result = json.loads(content)
                result['file'] = file_path.name
                return result
            except json.JSONDecodeError:
                # Fallback: simple string check if JSON parsing fails
                is_memory = "is_memory\": true" in content or '"is_memory": true' in content
                return {
                    "is_memory": is_memory, 
                    "reason": f"JSON Parse Error. Raw: {content[:50]}...", 
                    "file": file_path.name
                }

        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            return None

async def main():
    if not API_KEY:
        print("Error: IDEALAB_API_KEY not found in environment variables.")
        print("Please ensure .env file exists and contains IDEALAB_API_KEY.")
        return

    print(f"Initializing LLM: {MODEL_NAME}...")
    is_o_series = bool(re.match(r"^o\d", str(MODEL_NAME).strip().lower()))
    kwargs = {
        "model": MODEL_NAME,
        "api_key": API_KEY,
        "base_url": BASE_URL,
    }
    if not is_o_series:
        kwargs["temperature"] = 0
    llm = ChatOpenAI(**kwargs)

    trace_path = Path(TRACE_DIR)
    if not trace_path.exists():
        print(f"Directory not found: {TRACE_DIR}")
        return

    files = list(trace_path.glob("*.json"))
    total_files = len(files)
    print(f"Scanning {total_files} files in {TRACE_DIR} using AI analysis...\n")
    
    # Use Semaphore to limit concurrency and avoid rate limits
    sem = asyncio.Semaphore(CONCURRENCY_LIMIT) 
    tasks = [check_file(sem, llm, f) for f in files]
    
    # Show progress bar equivalent (simple print)
    results = []
    chunk_size = 50
    for i in range(0, len(tasks), chunk_size):
        chunk = tasks[i:i + chunk_size]
        print(f"Processing batch {i//chunk_size + 1}/{(len(tasks)+chunk_size-1)//chunk_size}...")
        chunk_results = await asyncio.gather(*chunk)
        results.extend(chunk_results)
    
    # Filter valid results
    valid_results = [r for r in results if r]
    memory_cases = [r for r in valid_results if r.get('is_memory')]
    
    print("\n" + "=" * 50)
    print("ANALYSIS REPORT")
    print("=" * 50)
    print(f"Total Files Analyzed: {len(valid_results)}")
    print(f"Suspicious (Memory/Retrieval): {len(memory_cases)}")
    print(f"Suspicious Rate: {len(memory_cases)/len(valid_results):.2%}")
    print("-" * 50)
    
    if memory_cases:
        print("\nSuspicious Cases (Top 20):")
        # Sort by filename for consistency
        memory_cases.sort(key=lambda x: x['file'])
        for i, case in enumerate(memory_cases[:20], 1):
            print(f"{i}. {case['file']}")
            print(f"   Reason: {case['reason']}")
            print("")

    # Save all results to file
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(valid_results, f, ensure_ascii=False, indent=2)
        print(f"\n[Success] 完整分析结果已保存至: {os.path.abspath(OUTPUT_FILE)}")
    except Exception as e:
        print(f"\n[Error] 保存结果失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())
