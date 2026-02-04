import sys
import os
import argparse
import time

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.agent.chem_detective import MolQuestAgent
from src.core.logger import logger, configure_logger
from src.utils.trace import RunArtifactsSaver, parse_final_result


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MolQuest Agent")
    parser.add_argument(
        "--sample",
        type=str,
        default="550e8400-e29b-41d4-a716-446655440001",
        help="Sample UUID to analyze",
    )
    return parser.parse_args(argv)


def _run_agent(sample_uuid: str) -> tuple[MolQuestAgent, dict, float, float]:
    agent = MolQuestAgent()
    agent.initialize()

    started_at = time.time()
    result_state = agent.run(sample_uuid)
    finished_at = time.time()
    return agent, result_state, started_at, finished_at

def main():
    args = _parse_args()

    config_path = os.path.join(PROJECT_ROOT, "config", "settings.yaml")
    configure_logger(config_path)

    try:
        agent, result_state, started_at, finished_at = _run_agent(args.sample)

        logger.info("Analysis Complete.")

        llm_config = getattr(agent, "config", {}).get("llm", {}) or {}
        final_result = parse_final_result(result_state.get("final_answer"), args.sample)
        saver = RunArtifactsSaver()
        saver.save_run(
            sample_uuid=args.sample,
            llm_config=llm_config,
            started_at=started_at,
            finished_at=finished_at,
            result_state=result_state,
            final_result=final_result,
        )
        
        for msg in result_state["messages"]:
            print(f"[{msg.type.upper()}]: {msg.content}")

    except Exception as e:
        logger.error(f"Error during execution: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
