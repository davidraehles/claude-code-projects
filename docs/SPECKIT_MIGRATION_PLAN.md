# Migration Plan: `.claude` to `speckit` for KiloCode

## Objective
Migrate the existing agent definitions, custom commands, and project memory from the Claude Code-specific `.claude` directory to the tool-agnostic `speckit` structure (`.specify`). This ensures that KiloCode (and other agents supported by `speckit`) can leverage the established workflows, specialized agents, and project context.

## Current State Analysis

### `.claude` Directory
*   **Agents (`.claude/agents/`)**: Contains definitions for a 7-agent ReAct system (Router, Spec Analyzer, Frontend Dev, Backend Dev, etc.). These are rich markdown files describing capabilities, workflows, and prompts.
*   **Commands (`.claude/commands/`)**: Contains markdown files defining slash commands. Many are already `speckit.*` commands, but there are custom ones like `/gen-component`, `/check-types`, `/monitor-deployment`.
*   **Memory (`.claude/memory/`)**: Contains `deployment-monitoring.md`, capturing specific project context and procedures.

### `.specify` Directory
*   **Root**: Contains `README.md` (Speckit documentation).
*   **Memory (`.specify/memory/`)**: Contains `constitution.md` and templates (`spec-template.md`, etc.).
*   **Templates (`.specify/templates/`)**: Contains templates for new files.

## Migration Strategy

The goal is to consolidate everything into `.specify` to make it the single source of truth for agent configuration and project context.

### 1. Agents Migration
**Source:** `.claude/agents/*.md`
**Target:** `.specify/agents/` (New Directory)

*   Create a new directory `.specify/agents/` to store agent definitions.
*   Move all agent markdown files from `.claude/agents/` to `.specify/agents/`.
*   **Action:** Update the `README.md` or a new `AGENTS.md` in `.specify/` to index these agents.
*   **KiloCode Integration:** KiloCode can be instructed to "load agent context from `.specify/agents/[agent-name].md`" when switching roles.

### 2. Commands Migration
**Source:** `.claude/commands/*.md`
**Target:** `.specify/commands/` (New Directory)

*   Create `.specify/commands/` to store custom command definitions.
*   Move non-speckit commands (e.g., `gen-component.md`, `check-types.md`) to this new directory.
*   **Note:** The `speckit.*` commands in `.claude/commands/` might be redundant if `speckit` CLI handles them natively, but keeping them as documentation or custom overrides in `.specify/commands/` is safe.
*   **Refinement:** Review command scripts referenced in these files to ensure they work with KiloCode's environment (standard bash/powershell).

### 3. Memory Migration
**Source:** `.claude/memory/*.md`
**Target:** `.specify/memory/`

*   Move `deployment-monitoring.md` from `.claude/memory/` to `.specify/memory/`.
*   Ensure `constitution.md` remains the central governance document.
*   Any other context files should be moved here.

## Detailed Execution Plan

### Phase 1: Structure Setup
1.  Create `.specify/agents/` directory.
2.  Create `.specify/commands/` directory.

### Phase 2: Content Transfer
1.  **Agents:**
    *   Copy `.claude/agents/README.md` -> `.specify/agents/README.md` (Update references).
    *   Copy `.claude/agents/*.md` -> `.specify/agents/`.
2.  **Commands:**
    *   Copy `.claude/commands/*.md` -> `.specify/commands/`.
    *   *Filter:* Check if `speckit.*` commands need to be copied or if they are built-in. For now, copy to preserve custom behavior if any.
3.  **Memory:**
    *   Copy `.claude/memory/*.md` -> `.specify/memory/`.

### Phase 3: KiloCode Configuration
1.  Create a `.specify/kilocode.md` (or similar context file) that instructs KiloCode on how to use this structure.
    *   *Instruction:* "When asked to perform a task, check `.specify/agents/` for a specialized agent that matches the task. Read that agent's file to adopt its persona and capabilities."
    *   *Instruction:* "Custom commands are defined in `.specify/commands/`. If a user uses a slash command, look there for definition."

### Phase 4: Cleanup (Optional)
1.  Once verified, the `.claude` directory can be archived or removed to avoid confusion, OR kept as a symlink/reference if Claude Code is still used alongside KiloCode.

## Deliverables
*   Updated `.specify` directory structure.
*   `docs/SPECKIT_MIGRATION_PLAN.md` (This document).
*   Verification that KiloCode can read and understand the migrated agents.
