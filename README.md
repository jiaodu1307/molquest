# MolQuest

## Project Structure

The project is organized into the following directories:

- **`config/`**: Configuration files (e.g., `settings.yaml`) defining model parameters, prompt templates, and system settings.
- **`data/`**: Datasets and example files used for agent execution and evaluation (e.g., `molecules_final.json`).
- **`scripts/`**: Command-line scripts for batch processing, performance evaluation, and data maintenance.
  - `analyze/`: Tools for calculating metrics and visualizing results.
  - `batch_run.py`: Script for executing batch experiments across multiple samples.
- **`src/`**: Main source code directory.
  - **`agent/`**: Implementation of the MolQuest agent logic (`chem_detective.py`) and state management (`state.py`).
  - **`core/`**: Core infrastructure including base agent classes, tool registry, logging, and LLM adapters.
  - **`tools/`**: Implementation of chemical analysis simulation tools (NMR, MS, IR, etc.).
  - **`utils/`**: Helper functions for molecule data handling, validation, and execution tracing.
- **`tests/`**: Unit and integration tests.Usage

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Run the agent:
   ```bash
   uv run main.py --sample SAMPLE_001
   ```

## LLM Configuration

MolQuest is designed to work with any LLM provider that supports the OpenAI API specification (e.g., OpenAI, Azure OpenAI, vLLM, DeepSeek, etc.).

### 1. Environment Variables

Set the following environment variables to configure your LLM connection:

- `LLM_API_KEY`: Your API key.
- `LLM_BASE_URL`: The base URL of the API server (optional, defaults to OpenAI's standard endpoint if not set).

**Example:**

```bash
export LLM_API_KEY="sk-..."
export LLM_BASE_URL="https://api.example.com/v1"
```

### 2. Configuration File

You can fine-tune the LLM settings in `config/settings.yaml`:

```yaml
llm:
  provider: "generic"       # Always use "generic" for OpenAI-compatible APIs
  model_name: "gpt-4o"      # The specific model identifier to call
  temperature: 0.0          # Sampling temperature
  # base_url: "..."         # Optional: override env var
  # api_key: "..."          # Optional: override env var
```

### Examples

- **OpenAI**:
  - `LLM_API_KEY`: "sk-..."
  - `model_name`: "gpt-4o"

- **Local Inference (e.g., vLLM, Ollama)**:
  - `LLM_BASE_URL`: "http://localhost:8000/v1"
  - `LLM_API_KEY`: "EMPTY" (if authentication is disabled)
  - `model_name`: "meta-llama/Llama-3-70b-Instruct"

- **Other Providers**:
  - Simply point `LLM_BASE_URL` to the provider's compatible endpoint and set the corresponding `LLM_API_KEY`.

## Agent Architecture

MolQuest uses [LangGraph](https://github.com/langchain-ai/langgraph) to build a cyclic reasoning agent (ReAct loop).

### Framework

- **State Machine**:
  - **Nodes**: `agent` (LLM reasoning), `tools` (tool execution)
  - **Edges**:
    - `agent` -> `tools` (if the model decides to call a tool)
    - `tools` -> `agent` (tool execution completed, returning results to the model)
    - `agent` -> `END` (reasoning finished)
- **State**: Contains conversation history (`messages`), current sample ID (`sample_id`), and known data (`known_data`).

### Prompt

The current agent is initialized with the following instruction:

> "Analyze sample {sample_id}"

*(Note: A more complex System Prompt is under development, which will include role definition, chemical reasoning step guidance, and output format constraints.)*

### Agent Tools

The agent is equipped with the following tools to simulate operations in a chemical analysis laboratory:

| Tool Name | Description | Input |
| :--- | :--- | :--- |
| `Measure_MW` | Measure molecular weight (simulate MS) | `uuid` |
| `Measure_Formula` | Determine molecular formula (simulate HRMS) | `uuid` |
| `Get_1H_NMR` | Get 1H NMR data | `uuid` |
| `Get_13C_NMR` | Get 13C NMR data | `uuid` |
| `Get_IR` | Get Infrared Spectroscopy (IR) data | `uuid` |
| `Get_19F_NMR` | Get 19F NMR data | `uuid` |
| `Get_31P_NMR` | Get 31P NMR data | `uuid` |
| `Get_HRMS` | Get High-Resolution Mass Spectrometry (HRMS) data | `uuid` |
| `Get_MS` | Get Mass Spectrometry (MS) data | `uuid` |
| `Get_Melting_Point` | Get melting point data | `uuid` |
| `Get_TLC` | Get Thin Layer Chromatography (TLC) data | `uuid` |
| `Get_Optical_Rotation` | Get Optical Rotation data | `uuid` |
| `Calculate_DBE` | Calculate Double Bond Equivalent (DBE) | `uuid` |
| `Check_Data` | Check available data for the molecule in the database, output as list | `uuid` |

## License

This project is licensed under the terms of the [MIT license](LICENSE).
