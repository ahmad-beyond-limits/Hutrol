# Implementation Phases

The following phases are planned for building the Human CLI Enterprise Agentic Harness Platform, as defined in `plan.md`.

## Phase 0 — Foundation
**Goal:** `human "show pdf files"` working end-to-end.
**Deliverables:**
- CLI shell using Typer
- Basic provider integration (OpenRouter)
- Read-only tools
- PyInstaller packaging

## Phase 1 — Harness MVP
**Goal:** Internal dogfooding ready.
**Deliverables:**
- State machine orchestration
- MCP Broker setup
- Risk classifier & Approval system
- Audit logging
- Golden prompt evaluations

## Phase 2 — Agent Platform
**Goal:** Production-ready architecture.
**Deliverables:**
- Progressive Skills loading
- Context manager
- Sub-agent execution
- SQLite memory implementation
- OpenTelemetry integration
- Multi-provider routing

## Phase 3 — Enterprise GA
**Goal:** Enterprise rollout ready.
**Deliverables:**
- MSI installer
- RBAC (Role-Based Access Control)
- Policy management
- SIEM integration
- Air-gapped deployment support
- Compliance export & Signed builds
