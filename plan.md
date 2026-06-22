# Human CLI — Enterprise Agentic Harness Platform

## Unified Architecture, Engineering, and Delivery Plan

---

# 1. Problem Statement

The current `human` CLI concept successfully demonstrates natural-language-to-command execution, but it has a fundamental enterprise limitation:

> It treats the LLM as both planner and executor.

In a production environment, allowing a model to generate arbitrary PowerShell or shell commands and execute them directly introduces unacceptable risks:

* Command hallucinations
* Unsafe file or system modifications
* Privilege misuse
* Prompt injection attacks
* Lack of auditability
* Context degradation over long sessions
* Vendor lock-in to a specific model
* No enterprise governance layer

Modern agent systems deployed by leading organizations in 2025–2026 no longer rely on "prompt → command → execute" architectures.

Instead, they use a **Harness Architecture**:

```text
Agent = Model + Harness
```

where:

* Models provide reasoning
* Harnesses provide control
* Tools provide execution
* Humans provide authorization

The objective is therefore:

> Transform `human` from a command-generation utility into a secure, auditable, enterprise-grade Agentic Harness Platform capable of operating safely on developer workstations, corporate endpoints, and infrastructure environments.

---

# 2. Solution Strategy

The solution follows the architectural lessons learned from:

* OpenAI Harness Engineering
* Anthropic Progressive Skills Architecture
* HumanLayer 12-Factor Agents
* LangChain Agent Infrastructure
* Claude Code Execution Model
* Long-running Agent Systems

The core design principle is:

### The model never directly controls the operating system.

Instead:

```text
User Request
    ↓
Harness Planning Layer
    ↓
Tool Selection
    ↓
Risk Evaluation
    ↓
Human Approval (if needed)
    ↓
Execution Sandbox
    ↓
Verification
    ↓
Audit Logging
```

This creates a deterministic execution path where every action is governed by policy, validation, and observability.

---

# 3. Target Architecture

## Enterprise System Topology

```text
┌──────────────────────────────────────────────┐
│               human.exe CLI                  │
│     One-shot Mode + Interactive REPL         │
└─────────────────────┬────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────┐
│           Agent Harness Runtime              │
│                                              │
│ Parse → Plan → Risk → Approve → Execute      │
│            → Verify → Report                 │
└───────┬──────────────┬──────────────┬────────┘
        │              │              │
        ▼              ▼              ▼

┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Context Mgr │ │ Skills Layer │ │ MCP Broker   │
│             │ │ Progressive  │ │ Secure Exec  │
└──────┬──────┘ └──────┬───────┘ └──────┬───────┘
       │               │                │
       ▼               ▼                ▼

┌──────────────────────────────────────────────┐
│             Tool Registry                    │
│ Typed Schemas + Risk Tiers + Adapters        │
└──────────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────┐
│             Execution Sandbox                │
│ Timeouts • Isolation • Policies              │
└──────────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────┐
│       Audit + Memory + Observability         │
└──────────────────────────────────────────────┘
```

---

# 4. Architectural Principles

## Principle 1 — Harness First

The harness owns execution.

The model only proposes:

```json
{
  "tool": "find_files",
  "arguments": {
    "pattern": "*.pdf"
  }
}
```

The harness decides whether execution is allowed.

---

## Principle 2 — Progressive Skill Loading

Following Anthropic's Progressive Skills model:

### Initial Context

Only metadata is loaded.

```json
{
  "system_diagnostics": {
    "intent": "Network diagnostics",
    "description": "Analyze ports and processes"
  }
}
```

### On Demand

The model requests:

```json
{
  "action": "load_skill",
  "skill": "system_diagnostics"
}
```

Only then is the full skill content loaded.

Benefits:

* Reduced token usage
* Reduced context rot
* Faster planning
* Easier maintenance

---

## Principle 3 — Context Externalization

Large transcripts are not trusted.

Instead:

```text
Raw Outputs
       ↓
Summarizer
       ↓
Structured Scratchpad
```

Scratchpad Example:

```json
{
  "intent": "Investigate port 3000",
  "tool": "port_check",
  "result": "Node process bound to port 3000",
  "risk": "read_only"
}
```

This prevents context degradation.

---

## Principle 4 — Explicit State Machine

No autonomous loops controlled by the model.

Instead:

```python
Parse
Plan
RiskCheck
Approval
Execute
Verify
Report
```

Each state is:

* deterministic
* testable
* observable

---

# 5. Core Platform Components

## 5.1 CLI Layer

Framework:

```text
Typer
```

Modes:

```bash
human "show all pdf files"

human
> show all pdf files
> what is using port 3000
```

Commands:

```bash
human doctor
human config
human history
human audit
human skills
human update
```

---

## 5.2 Agent Orchestrator

Responsible for:

### Planning

Model determines:

```json
{
  "intent": "Find PDFs",
  "tool": "find_files"
}
```

### Execution

Harness executes.

### Verification

Harness validates outcome.

### Reporting

Human-readable response.

---

## 5.3 Context Manager

Responsibilities:

### Context Budget Enforcement

Example:

```text
Maximum Runtime Context:
4096 Tokens
```

Regardless of provider capabilities.

### Transcript Compaction

Convert:

```text
1000-line directory listing
```

Into:

```text
241 PDF files found.
Largest directory:
D:\Documents
```

---

## 5.4 MCP Secure Broker

Acts as the operating system firewall.

### Read-Only Examples

Allowed automatically:

```powershell
Get-Process
Get-Service
Get-ChildItem
Get-NetTCPConnection
```

### Mutating Examples

Require approval:

```powershell
Stop-Process
Remove-Item
Set-ItemProperty
Restart-Service
```

Approval:

```text
Proposed Action:
Delete 34 files

[Y/n]
```

---

## 5.5 Tool Registry

The preferred execution mechanism.

Example:

```json
{
  "name": "find_files",
  "risk_tier": "read_only"
}
```

### Tool Categories

#### Diagnostics

```text
port_check
process_inspect
service_status
disk_usage
```

#### File Operations

```text
find_files
archive_files
move_files
delete_files
```

#### Development

```text
git_status
git_commit
python_env_check
npm_diagnostics
```

#### Network

```text
dns_lookup
ping_host
traceroute
```

---

## 5.6 Progressive Skills System

Structure:

```text
skills/
├── system_diagnostics/
│   ├── skill.md
│   └── port_check.ps1
│
├── file_ops/
│   ├── skill.md
│   └── bulk_archive.ps1
│
├── git_ops/
│   ├── skill.md
│   └── git_health.ps1
```

Skill contents define:

* Intent
* Boundaries
* Procedures
* Allowed tools

---

## 5.7 Provider Abstraction Layer

```python
class LLMProvider
```

Implementations:

```text
OpenAIProvider
AnthropicProvider
AzureOpenAIProvider
LocalProvider
```

Benefits:

* No vendor lock-in
* Air-gapped deployments
* Model routing policies

---

## 5.8 Memory Architecture

### Session Store

SQLite:

```text
Current directory
History
Recent commands
```

### Long-Term Memory

Optional.

Stores:

```text
Preferences
Aliases
Workflow shortcuts
```

### Audit Store

Mandatory.

Records:

```text
Prompt
Plan
Tool
Risk
Approval
Result
```

---

## 5.9 Observability

### Structured Logging

```text
JSON Logs
Trace IDs
Correlation IDs
```

### OpenTelemetry

Export:

```text
Datadog
Honeycomb
Elastic
Splunk
Azure Monitor
```

### Metrics

```text
Execution latency
Approval rate
Tool usage
Failure rate
Fallback rate
```

---

# 6. Security Architecture

## Risk Tiers

### Tier 0

```text
read_only
```

Examples:

```powershell
Get-Process
Get-Service
```

Auto-execute.

---

### Tier 1

```text
mutating_scoped
```

Examples:

```text
Rename files in current directory
```

Execute with notification.

---

### Tier 2

```text
mutating_unscoped
```

Examples:

```text
Delete files recursively
```

Require approval.

---

### Tier 3

```text
destructive
```

Examples:

```text
Registry changes
Disk operations
System-wide deletions
```

Require approval and dry-run preview.

---

## Security Controls

### Prompt Injection Defense

Tool output treated as data.

Never instructions.

---

### Secret Protection

Use:

```text
Windows Credential Manager
macOS Keychain
libsecret
```

Never plaintext config files.

---

### Sandbox Controls

```text
Execution timeout
Resource limits
Working directory restrictions
Environment allowlists
```

---

# 7. Repository Structure

```text
human/
│
├── pyproject.toml
├── config/
│
├── src/human/
│
├── cli/
│   └── main.py
│
├── orchestrator/
│   ├── state_machine.py
│   ├── harness.py
│   └── types.py
│
├── context/
│   ├── manager.py
│   └── subagent.py
│
├── providers/
│   ├── base.py
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   ├── azure_provider.py
│   └── local_provider.py
│
├── mcp/
│   └── broker.py
│
├── tools/
│   ├── registry.py
│   ├── adapters/
│   └── schemas/
│
├── skills/
│   ├── skill_manager.py
│   ├── system_diagnostics/
│   ├── file_ops/
│   └── git_ops/
│
├── safety/
│   ├── risk_classifier.py
│   └── approval_gate.py
│
├── execution/
│   └── sandbox.py
│
├── memory/
│   ├── session_store.py
│   └── audit_store.py
│
├── observability/
│   ├── logging.py
│   └── tracing.py
│
├── config/
│   ├── loader.py
│   └── secrets.py
│
├── evals/
│   ├── golden_prompts.jsonl
│   ├── adversarial_prompts.jsonl
│   └── run_evals.py
│
└── tests/
```

---

# 8. Engineering Delivery Roadmap

## Phase 0 — Foundation

Duration: 1–2 Weeks

Deliverables:

* CLI shell
* Typer integration
* Basic provider
* Read-only tools
* PyInstaller packaging

Goal:

```text
human "show pdf files"
```

working end-to-end.

---

## Phase 1 — Harness MVP

Duration: 4–6 Weeks

Deliverables:

* State machine
* MCP Broker
* Risk classifier
* Approval system
* Audit logging
* Golden prompt evaluations

Outcome:

Internal dogfooding ready.

---

## Phase 2 — Agent Platform

Duration: 6–8 Weeks

Deliverables:

* Progressive Skills
* Context manager
* Sub-agent execution
* SQLite memory
* OpenTelemetry
* Multi-provider routing

Outcome:

Production-ready architecture.

---

## Phase 3 — Enterprise GA

Duration: 8–12 Weeks

Deliverables:

* MSI installer
* RBAC
* Policy management
* SIEM integration
* Air-gapped deployment
* Compliance export
* Signed builds

Outcome:

Enterprise rollout ready.

---

# 9. Success Criteria

The platform is considered successful when:

### Security

* No direct LLM → OS execution path
* 100% destructive actions require approval

### Reliability

* Deterministic orchestration
* Context remains bounded

### Maintainability

* New capabilities added as Skills
* Core harness rarely modified

### Enterprise Readiness

* Auditable
* Observable
* Deployable via enterprise tooling
* Vendor-independent

---

# Final Recommendation

Build **Human** as a **Harness-First Agent Platform**, not as an LLM-powered shell wrapper.

The final architecture should combine:

* **OpenAI Harness Engineering** → explicit orchestration, tool contracts, evaluations, observability
* **Anthropic Progressive Skills** → dynamic skill loading and context efficiency
* **12-Factor Agents** → deterministic control flow and externalized state
* **Enterprise Security Principles** → MCP broker, risk tiers, approval gates, audit trails
* **Modern Platform Engineering** → provider abstraction, telemetry, policy management, and signed distribution

This creates a system that can evolve from a single-user CLI into a secure enterprise agent runtime without requiring a future architectural rewrite.
