# Project Progress

## Phase 0 — Foundation: ✅ Completed
We have successfully built the end-to-end foundation of the `human` CLI platform.

### Deliverables Finished:
- **Project Configuration**: Set up `pyproject.toml` and initialized the `uv` environment with `typer`, `pydantic`, `openai`, and `python-dotenv`.
- **Configuration System**: Created `.env` parsing in `src/human/config/loader.py` to securely load API keys and model choices.
- **Provider Layer**: Implemented the LLM Provider interface and the specific OpenRouter integration using the `openai` SDK (`src/human/providers/openrouter_provider.py`).
- **Tool Registry & Safety**: 
  - Defined the initial `RiskTier.READ_ONLY` constraint in `src/human/safety/risk_classifier.py`.
  - Built a dynamic tool schema generator in `src/human/tools/registry.py`.
  - Implemented the `find_files` read-only tool in `src/human/tools/file_ops.py`.
- **Execution Harness**: Built the core orchestrator in `src/human/orchestrator/harness.py` to handle the parse → validate → check risk → execute loop.
- **CLI Shell**: Created the Typer application in `src/human/cli/main.py` with both one-shot (`human run`) and interactive (`human repl`) commands.

## Phase 1 — Harness MVP: ✅ Completed
We built the core safety and orchestration logic.

### Deliverables Finished:
- **State Machine Orchestration**: Migrated to a deterministic `PARSE -> PLAN -> RISK_CHECK -> APPROVAL -> EXECUTE -> VERIFY -> REPORT` flow (`src/human/orchestrator/state_machine.py`).
- **MCP Broker Setup**: Implemented an OS firewall to intercept commands and analyze intent before execution (`src/human/mcp/broker.py`).
- **Risk Classifier & Approval System**: Expanded risk tiers and implemented an interactive `[y/N]` block for `MUTATING_UNSCOPED` and `DESTRUCTIVE` actions (`src/human/safety/approval_gate.py`).
- **Audit Logging**: Created a JSONL logger to capture all system traces and decisions centrally at `~/.human/audit.jsonl`.
- **Golden Prompt Evaluations**: Built an assertion-based regression suite to guarantee the state machine and broker enforce safety boundaries correctly (`src/human/evals/run_evals.py`).

## Phase 2 — Agent Platform: ⏳ Pending
- Progressive Skills loading
- Context manager
- Sub-agent execution
- SQLite memory
- OpenTelemetry integration
- Multi-provider routing

## Phase 3 — Enterprise GA: ⏳ Pending
- MSI installer
- RBAC
- Policy management
- SIEM integration
- Air-gapped deployment
- Compliance export
