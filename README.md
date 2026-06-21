# Hutrol CLI — Enterprise Agentic Harness

**Hutrol** is an enterprise-grade, agentic Command Line Interface (CLI) harness designed to bring autonomous AI capabilities directly to your operating system, wrapped in a deterministic, highly secure, and fully auditable execution layer.

Unlike standard chat interfaces or basic script wrappers, Hutrol operates as a **secure broker** between advanced Large Language Models (LLMs) and your local filesystem and OS. It evaluates risk, enforces policies, requires explicit human approval for destructive actions, and exports immutable logs for enterprise compliance.

---

## 🎯 Why is Hutrol Needed?

As LLMs become capable of writing code, managing files, and executing shell commands, allowing them direct, unsupervised access to an operating system is a massive security risk.

Hutrol solves the **Agentic Security Problem** by wrapping the LLM inside a deterministic harness:
1. **Safety by Default:** No mutating command runs without explicit human approval or policy clearance.
2. **Auditability:** Every tool execution, approval decision, and system trace is logged in an immutable, append-only format that can be exported to enterprise SIEMs (like Splunk or Sentinel).
3. **Sub-Agent Delegation:** Complex tasks are broken down and assigned to isolated, memory-constrained sub-agents to prevent context contamination and runaway token usage.
4. **Air-Gap Capability:** For strict regulatory environments, Hutrol can disconnect entirely from the public internet and run completely locally.

---

## 🏗️ Detailed Architecture

The architecture of Hutrol follows a strict pipeline: **Parse → Plan → Evaluate Policy → Execute → Audit**.

### 1. The Orchestrator (State Machine)
The core of Hutrol is a deterministic finite state machine (FSM). Rather than letting the LLM dictate the execution loop in a recursive chain of thought, the FSM guarantees that every agent step passes through specific, hardcoded checkpoints.

### 2. Model Context Protocol (MCP) Broker
The MCP Broker acts as the **OS Firewall**. It intercepts all requests from the LLM to use a tool (e.g., `list_directory`, `run_system_command`). It classifies the request into Risk Tiers:
- `READ_ONLY`: Allowed automatically (e.g., `Get-ChildItem`).
- `MUTATING_SCOPED`: Requires notification (e.g., writing a new file).
- `MUTATING_UNSCOPED` / `DESTRUCTIVE`: Blocked or requires explicit Human-in-the-Loop `[y/N]` approval (e.g., `Remove-Item`).

### 3. The Compliance Layer
Sitting safely below the LLM, this layer ensures true enterprise governance:
- **Policy Engine**: Overrides risk tiers based on predefined roles (e.g., an `admin` may approve destructive actions, but a `junior_dev` is strictly blocked).
- **Approval Tracker**: Records *who* approved *what* command, logging it to `~/.human/approvals.jsonl`.
- **Audit Logger**: Maintains the immutable history of all system events.
- **SIEM Exporter**: Instantly forwards structured JSON event payloads to external security monitoring endpoints.

### 4. Sub-Agent Runtime
When a task is too complex, the Main Orchestrator can spawn a Sub-Agent. These are ephemeral workers that:
- Receive only a strict subset of the main context (preventing context bloat).
- Are limited to ~2k tokens.
- Execute a dedicated retry-recovery loop if a tool fails.
- Must still pass through the exact same MCP Broker and Approval Gates as the main agent.

---

## 🚀 Getting Started & Configuration

You can configure Hutrol to run either via **OpenRouter** (cloud APIs) or **Ollama** (completely local, air-gapped).

### Installation (Source / Development)
Assuming you have [uv](https://github.com/astral-sh/uv) installed, clone the repository and sync the dependencies:
```bash
uv sync
```

### Installation (Pre-Built Installer)
For enterprise deployment, you can use the generated `HutrolSetup.exe` Windows installer. 
During installation, **make sure to check the box** that says: `"Add Hutrol to system PATH environment variable"`.
This will configure your system's `PATH` automatically so that you can simply type `hutrol` into any terminal window without needing to navigate to the installation folder.

### Setup Option 1: OpenRouter (Cloud Models)
By default, Hutrol uses OpenRouter. To set this up, you need to provide your API key and specify a model that supports Tool Calling (like Llama 3.1, Claude 3.5 Sonnet, or GPT-4o).

```bash
# 1. Set the provider
uv run hutrol config set PROVIDER openrouter

# 2. Add your OpenRouter API Key
uv run hutrol config set OPENROUTER_API_KEY sk-or-v1-...

# 3. Choose a Tool-Calling capable model
uv run hutrol config set OPENROUTER_MODEL meta-llama/llama-3.1-8b-instruct
```

### Setup Option 2: Ollama (Air-Gapped / Local Only)
If you are working in a highly secure environment without internet access, you can run models locally using Ollama. Make sure you have Ollama installed and a model pulled (e.g., `ollama run llama3.1`).

```bash
# 1. Switch the provider to Ollama
uv run hutrol config set PROVIDER ollama

# 2. Set the model name exactly as it appears in your local Ollama list
uv run hutrol config set OLLAMA_MODEL llama3.1

# 3. (Optional) Set the host if running on a different port/machine
uv run hutrol config set OLLAMA_HOST http://localhost:11434
```

### Viewing Your Configuration
At any time, you can verify your setup. *(Note: API keys are securely masked).*
```bash
uv run hutrol config list
```

---

## 🛠️ Usage Examples

### 1. Single Command Execution
Run a specific task and exit immediately:
```bash
uv run hutrol run "Find all python files in the src directory and tell me how many there are."
```

### 2. Interactive REPL Mode
Start an ongoing conversation with the agent where it retains context across multiple queries:
```bash
uv run hutrol repl
```
```text
Hutrol CLI Started. Type 'exit' or 'quit' to leave.
hutrol> Please list my directories
...
```

### 3. Compliance Export (Auditor Mode)
To generate a cryptographic, tamper-evident zip file of all system logs, traces, and approvals:
```bash
uv run hutrol export-audit
```
*Outputs: `human_compliance_export_17398234.zip` and its `SHA-256 Checksum`.*

---

## Settings & Command Reference

Hutrol provides several commands to manage your AI provider, security configuration, and execution mode. You can always list all available commands by typing:
```bash
hutrol --help
```

Below is a detailed list of every command available in the CLI.

### 1. `hutrol config set <KEY> <VALUE>`
Modifies your `~/.human/config.json` persistent configuration file.
* **`PROVIDER`**: Set to `openrouter` (for cloud) or `ollama` (for local air-gapped).
* **`OPENROUTER_API_KEY`**: Your secure API key (will be automatically masked when listing).
* **`OPENROUTER_MODEL`**: The cloud model to use (default: `meta-llama/llama-3.1-8b-instruct`).
* **`OLLAMA_MODEL`**: The local model name pulled in Ollama (default: `llama3`).
* **`OLLAMA_HOST`**: The URL for your local Ollama server (default: `http://localhost:11434`).
* **`SAFETY`**: Set to `false` to completely disable the human-in-the-loop (Y/N) confirmation prompts and allow the agent to auto-approve executing system commands (default: `true`).

**Example:**
```bash
hutrol config set OPENROUTER_MODEL anthropic/claude-3.5-sonnet
```

### 2. `hutrol config list`
Displays all of your currently active configuration settings. Sensitive information, like API keys or Tokens, are automatically obscured (e.g., `sk-o*******************`) so they never leak in your terminal logs.

**Example:**
```bash
hutrol config list
```

### 3. `hutrol run "<prompt>"`
The "Single Shot" execution mode. Hutrol will parse the prompt, execute the necessary tools or system commands to accomplish the task, and then immediately terminate. Ideal for CI/CD pipelines or background scripts.

**Example:**
```bash
hutrol run "Find all python files in the src directory and tell me how many there are."
```

### 4. `hutrol repl`
Starts an interactive terminal session (`hutrol>`). Context is maintained across your prompts. You can chat with the agent, ask it to look up information, write code, or execute complex multi-step workflows. Type `exit` or `quit` to leave.

**Example:**
```bash
hutrol repl
```

### 5. `hutrol export-audit`
Packages your local immutable system logs (`audit.jsonl`), tool execution traces (`trace.jsonl`), and human-in-the-loop decisions (`approvals.jsonl`) into a timestamped, zipped archive. It also generates a cryptographic `SHA-256 Checksum` for the file to prove the integrity of the audit logs to enterprise compliance teams.

**Example:**
```bash
hutrol export-audit
```

---

## 📂 Project Structure

Understanding the layout of the Hutrol codebase is essential for developers extending the harness.

```text
Hutrol/
├── scripts/
│   └── build_installer.iss      # Inno Setup deployment script for building HumanSetup.exe
├── skills/                      # Directory for dynamically loaded YAML-based agent skills
├── src/
│   └── human/
│       ├── cli/                 # Typer-based command-line interface entry points (main.py)
│       ├── compliance/          # Enterprise governance layer (Policy Engine, SIEM Export, Audit Logger)
│       ├── config/              # Persistent JSON configuration loader and manager
│       ├── evals/               # Golden prompt evaluations and regression tests
│       ├── mcp/                 # Model Context Protocol Broker (Acts as the OS Firewall)
│       ├── memory/              # Persistent SQLite memory for conversational context
│       ├── observability/       # Structured tracing logic for debugging latency and flow
│       ├── orchestrator/        # The deterministic FSM, Context Manager, and Sub-Agent spawning
│       ├── providers/           # Modular LLM API connections (OpenRouter, Ollama)
│       ├── safety/              # Interactive [y/N] Approval Gates and Risk classification logic
│       └── tools/               # Native Python tool executors (System Ops, File Ops, Agent Ops)
├── pyproject.toml               # Project dependencies and script definitions (uv package manager)
└── README.md                    # This documentation file
```
