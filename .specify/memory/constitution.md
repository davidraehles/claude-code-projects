# claude-code-projects Constitution

## Core Principles

### I. Test-First Development (NON-NEGOTIABLE)
Tests MUST be written and approved before implementation begins. Use Playwright for all end-to-end and integration testing. TDD cycle enforced: Tests fail → Implementation → Tests pass → Refactor. Every feature must have corresponding test coverage. Test results must pass before any commit can be pushed.

### II. Frequent Test-Commit-Push Workflow
Changes MUST follow the test-commit-push cadence: write/modify code → run tests locally → commit with descriptive message → push to remote. Commits should be logical, atomic units of work with clear commit messages following conventional commits. Push frequently to avoid long-lived branches and reduce integration risk.

### III. MCP Tool Extensibility
The project embraces Claude Code MCP tools and skills as first-class integrations. Currently active: Playwright testing. Future integrations planned: GitHub (PR/issue management), Serena (additional testing/validation), PydanticAI (model-driven development). All new tools MUST be documented in tool setup guides and integrated into CI/CD workflow when applicable.

### IV. Spec-Driven Development
All features MUST start with a specification (spec.md) before implementation. Specifications define requirements, scope, acceptance criteria, and design decisions. Implementations MUST align with approved specs. Breaking changes to specs require amendment documentation and stakeholder sign-off.

### V. Integration & Contract Testing
Integration tests MUST cover inter-service communication, shared schemas, and contract boundaries. Playwright tests MUST validate end-to-end workflows. Breaking changes require comprehensive test updates before deployment.

## Technology Stack

- **Frontend/Testing**: Playwright (`@playwright/test` ^1.56.1) for all E2E and integration testing
- **Runtime**: Node.js (types via `@types/node` ^24.10.1)
- **Version Control**: Git with conventional commits
- **Deployment**: Vercel (supported via deployment scripts)
- **Future Integrations**: GitHub MCP, Serena framework, PydanticAI

## Development Workflow

1. **Planning Phase**: Create or review spec.md with acceptance criteria
2. **Testing Phase**: Write Playwright tests for new features; verify tests fail initially
3. **Implementation Phase**: Develop feature until tests pass
4. **Quality Phase**: Run full test suite; ensure no regressions
5. **Commit Phase**: Commit changes with conventional commit message
6. **Push Phase**: Push to remote branch; create/update PR if needed
7. **Integration Phase**: Ensure CI passes; merge only after approval

All steps MUST be completed before moving to the next feature. Skipping the test or commit-push cycle is prohibited.

## Governance

- This Constitution supersedes all other practices and guidelines
- All contributors MUST comply with core principles, especially Test-First Development
- Amendments require: (1) Clear rationale, (2) Documentation, (3) Affected template updates
- Constitution version bumps follow semantic versioning: MAJOR (principle removal/redefinition), MINOR (new principle/guidance), PATCH (clarifications/typos)
- PR reviews MUST verify test coverage and compliance with principles before merge
- Breaking changes to specs, APIs, or tool integrations MUST be captured in amendment documentation

**Version**: 1.0.0 | **Ratified**: 2025-11-18 | **Last Amended**: 2025-11-18
