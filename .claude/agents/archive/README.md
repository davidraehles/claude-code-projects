# Agent System Archive

This directory contains historical documentation from the agent system development process.

**Archived on**: November 29, 2025

---

## What's Archived Here

This documentation was created during the initial development and iteration of the multi-agent system. It has been superseded by:

- **JSON Agent Registry**: All agents are now defined as `.json` files in the parent directory
- **AGENT-REGISTRY.md**: Comprehensive registry documentation
- **README.md**: Current multi-agent system overview

---

## Archived Files

### Workflow Documentation
- `EXAMPLE-WORKFLOWS.md` - Example workflows (superseded by agent JSON configs)
- `FEATURE-002-WORKFLOWS.md` - Feature 002 specific workflows
- `WORKFLOW-1-LAUNCH.md` - Launch workflow examples
- `REACT-ORCHESTRATION.md` - ReAct orchestration patterns
- `IMPLEMENTATION-CHECKLIST.md` - Implementation checklists
- `IMPLEMENTATION-SUMMARY.md` - Implementation summaries
- `REVIEW-AND-GUIDANCE.md` - Review and guidance docs

### Individual Agent Documentation (Markdown Format)
- `router-agent.md`
- `spec-analyzer-agent.md`
- `frontend-dev-agent.md`
- `backend-dev-agent.md`
- `testing-quality-agent.md`
- `documentation-artifact-agent.md`
- `integration-validation-agent.md`
- `agent-registry-manager.md`

These individual `.md` files were the original documentation format. They have been replaced by:
- `.json` agent configuration files (machine-readable, Claude Code compatible)
- Consolidated `AGENT-REGISTRY.md` (human-readable registry)

---

## Why Archived?

The agent system evolved from markdown-based documentation to a JSON-based configuration system that:

1. **Better Claude Code Integration**: JSON format is natively supported by Claude Code's agent system
2. **Single Source of Truth**: One `.json` file per agent instead of duplicate `.md` and `.json`
3. **Easier Maintenance**: Updates only need to happen in one place
4. **Better Tooling**: JSON can be validated, linted, and processed programmatically

---

## Current Documentation

For current agent system documentation, see:
- [../.claude/agents/README.md](../README.md) - Multi-agent system overview
- [../.claude/agents/AGENT-REGISTRY.md](../AGENT-REGISTRY.md) - Complete agent registry
- Individual `.json` files in parent directory - Agent configurations

---

**Note**: These archived files are kept for historical reference and can be safely deleted if space is needed.
