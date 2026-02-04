import sys
import argparse
import re
import json
import time
import random
import os
import logging
import glob
import asyncio
from typing import List

import httpx

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent.chem_detective import MolQuestAgent
from src.core.logger import logger, configure_logger
from src.utils.trace import RunArtifactsSaver, parse_final_result
from src.utils.molecule_manager import MoleculeManager


def _is_retryable_exception(exc: Exception) -> bool:
    if isinstance(exc, (httpx.RemoteProtocolError, httpx.TimeoutException, httpx.TransportError)):
        return True

    try:
        import openai
    except Exception:
        return False

    retry_types = tuple(
        t
        for t in (
            getattr(openai, "APIConnectionError", None),
            getattr(openai, "APITimeoutError", None),
            getattr(openai, "RateLimitError", None),
            getattr(openai, "InternalServerError", None),
        )
        if isinstance(t, type)
    )
    return bool(retry_types) and isinstance(exc, retry_types)


def process_sample(uuid: str, runs_dir: str, traces_dir: str, model_name: str = None, provider: str = None, enable_thinking: bool = False) -> None:
    """
    Process a single sample: run agent and save artifacts.
    """
    try:
        logger.info(f"Starting processing for UUID: {uuid}")

        config = {}
        llm_config = {}
        if model_name:
            llm_config["model_name"] = model_name
        if provider:
            llm_config["provider"] = provider
        if enable_thinking:
            llm_config["enable_thinking"] = True

        if llm_config:
            config["llm"] = llm_config

        max_attempts = int(os.getenv("RUN_NETWORK_RETRY_ATTEMPTS", "3"))
        min_wait_s = float(os.getenv("RUN_NETWORK_RETRY_MIN_WAIT_S", "2"))
        max_wait_s = float(os.getenv("RUN_NETWORK_RETRY_MAX_WAIT_S", "10"))

        started_at: float | None = None
        finished_at: float | None = None
        result_state = None
        effective_llm_config: dict = {}

        last_exc: Exception | None = None
        for attempt in range(1, max_attempts + 1):
            try:
                agent = MolQuestAgent(config=config)
                agent.initialize()

                started_at = time.time()
                result_state = agent.run(uuid)
                finished_at = time.time()

                effective_llm_config = getattr(agent, "config", {}).get("llm", {}) or {}
                last_exc = None
                break
            except Exception as e:
                last_exc = e
                finished_at = time.time()
                if attempt >= max_attempts or not _is_retryable_exception(e):
                    raise

                wait_s = min(max_wait_s, max(min_wait_s, min_wait_s * (2 ** (attempt - 1))))
                wait_s = wait_s + random.random() * 0.2
                logger.warning(
                    f"Retryable error for UUID {uuid} (attempt {attempt}/{max_attempts}): {type(e).__name__}: {e}. sleep_s={wait_s:.2f}"
                )
                time.sleep(wait_s)

        if last_exc is not None or result_state is None or started_at is None or finished_at is None:
            raise last_exc or RuntimeError("Agent run did not produce a result_state")

        final_result = parse_final_result(result_state.get("final_answer"), uuid)
        saver = RunArtifactsSaver(trace_dir=traces_dir, run_dir=runs_dir)

        save_attempts = int(os.getenv("RUN_SAVE_RETRY_ATTEMPTS", "5"))
        save_min_wait_s = float(os.getenv("RUN_SAVE_RETRY_MIN_WAIT_S", "1"))
        save_max_wait_s = float(os.getenv("RUN_SAVE_RETRY_MAX_WAIT_S", "10"))

        last_save_exc: Exception | None = None
        for save_attempt in range(1, save_attempts + 1):
            try:
                saver.save_run(
                    sample_uuid=uuid,
                    llm_config=effective_llm_config,
                    started_at=started_at,
                    finished_at=finished_at,
                    result_state=result_state,
                    final_result=final_result,
                )
                logger.info(f"Finished processing for UUID: {uuid}")
                return
            except Exception as e:
                last_save_exc = e
                if save_attempt >= save_attempts:
                    raise

                wait_s = min(save_max_wait_s, max(save_min_wait_s, save_min_wait_s * (2 ** (save_attempt - 1))))
                wait_s = wait_s + random.random() * 0.2
                logger.warning(
                    f"Save error for UUID {uuid} (attempt {save_attempt}/{save_attempts}): {type(e).__name__}: {e}. sleep_s={wait_s:.2f}"
                )
                time.sleep(wait_s)

        if last_save_exc is not None:
            raise last_save_exc

    except Exception as e:
        logger.error(f"Error processing UUID {uuid}: {e}", exc_info=True)

class BatchProcessor:
    """
    处理器类，用于管理批量运行任务，支持异步并发。
    Handles batch processing with async concurrency support.
    """
    def __init__(self, args, uuids: List[str]):
        self.args = args
        self.uuids = uuids
        self.total = len(uuids)
        self.done = 0
        self.start_time = 0

    async def run(self):
        """
        执行批处理任务
        """
        self.start_time = time.time()
        
        # 使用 Semaphore 限制并发数量
        # Limit concurrency using Semaphore
        sem = asyncio.Semaphore(self.args.concurrency)
        
        # 获取当前的事件循环
        loop = asyncio.get_running_loop()

        async def worker(uuid: str):
            async with sem:
                # 检查是否需要跳过 (Resume 模式)
                if self._should_skip(uuid):
                    self._update_progress()
                    return

                # 在线程池中运行同步的处理函数，避免阻塞事件循环
                # Run synchronous process_sample in thread pool
                await loop.run_in_executor(
                    None,  # Use default ThreadPoolExecutor
                    process_sample, 
                    uuid, 
                    self.args.runs_dir, 
                    self.args.traces_dir,
                    self.args.model,
                    self.args.provider,
                    self.args.enable_thinking
                )
                self._update_progress()

        # 创建并启动所有任务
        tasks = [worker(uuid) for uuid in self.uuids]
        
        # 等待所有任务完成
        await asyncio.gather(*tasks)
        
        self._finish()

    def _should_skip(self, uuid: str) -> bool:
        if not self.args.resume:
            return False
        # Check if output file exists
        pattern = os.path.join(self.args.runs_dir, f"*{uuid}.json")
        if glob.glob(pattern):
            if self.args.verbose:
                logger.info(f"Skipping {uuid} (already processed)")
            return True
        return False

    def _update_progress(self):
        # 注意：此方法在主线程事件循环中调用，无需锁
        # Note: Called within the event loop, so simple increment is safe between awaits
        self.done += 1
        if self.args.progress_every > 0:
            if self.done % self.args.progress_every == 0 or self.done == self.total:
                print(f"progress: {self.done}/{self.total}", flush=True)

    def _finish(self):
        if self.args.verbose:
            elapsed = int(max(0.0, time.time() - self.start_time))
            logger.info(f"Batch processing complete. elapsed_s={elapsed}")

def main():
    parser = argparse.ArgumentParser(description="Batch run ChemDetective Agent on dataset")
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Limit number of samples to run (for testing)",
    )
    parser.add_argument(
        "--runs-dir",
        type=str,
        default="runs",
        help="Directory to save run results JSON",
    )
    parser.add_argument(
        "--traces-dir",
        type=str,
        default="traces",
        help="Directory to save traces",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=1,
        help="每完成 N 条打印一次进度",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="输出详细日志（默认只输出关键进度）",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override LLM model name (optional, otherwise uses settings.yaml)",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default=None,
        help="Override LLM provider (e.g. idealab, arena, nonelinear, model_router, dashscope)",
    )
    parser.add_argument(
        "--enable-thinking",
        action="store_true",
        help="Enable thinking mode (e.g. for Qwen-Thinking)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip already processed samples (check if result file exists in runs-dir)",
    )
    parser.add_argument(
        "--concurrency",
        "-j",
        type=int,
        default=1,
        help="并发数量 (Concurrency level). Default: 1",
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default="data/processed/molecules_version_3_0113.json",
        help="指定分子数据 JSON 文件路径 (默认: data/processed/molecules_version_3_0113.json)",
    )
    
    args = parser.parse_args()

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    config_path = os.path.join(project_root, "config", "settings.yaml")
    configure_logger(config_path)

    if not args.verbose:
        logger.setLevel(logging.WARNING)

    # Set environment variable if data path is provided
    if args.data_path:
        os.environ["MOLECULE_DATA_PATH"] = args.data_path
        logger.info(f"Setting molecule data path to: {args.data_path}")

    # Load all molecules
    manager = MoleculeManager(data_path=args.data_path)
    all_molecules = manager.get_all_molecules()
    
    if args.max_samples:
        all_molecules = all_molecules[:args.max_samples]
        
    uuids = sorted([m.uuid for m in all_molecules])
    logger.info(f"Found {len(uuids)} samples to process (sorted by UUID).")
    
    if args.model:
        logger.info(f"Overriding model to: {args.model}")

    # 预先初始化以避免多线程下的工具注册竞争
    # Pre-initialize to avoid race conditions in tool registry during multi-threading
    if args.concurrency > 1:
        try:
            logger.info("Pre-initializing agent to populate tool registry...")
            # Also pass model config here to ensure it's valid
            pre_init_llm = {}
            if args.model:
                pre_init_llm["model_name"] = args.model
            if args.provider:
                pre_init_llm["provider"] = args.provider
            if args.enable_thinking:
                pre_init_llm["enable_thinking"] = True
                
            pre_init_config = {"llm": pre_init_llm} if pre_init_llm else None
            ChemDetectiveAgent(config=pre_init_config).initialize()
        except Exception as e:
            logger.warning(f"Agent pre-initialization failed: {e}")

    # Run the batch processor
    processor = BatchProcessor(args, uuids)
    asyncio.run(processor.run())

if __name__ == "__main__":
    main()
