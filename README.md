# Claude Code Projects

This project is initialized with [Spec-Kit](https://github.com/github/spec-kit), a spec-driven development toolkit from GitHub.

## About Spec-Kit

Spec-Kit provides a structured workflow for building software features using AI coding assistants. It helps teams:

- Define clear project principles and requirements
- Create detailed specifications
- Generate actionable implementation plans
- Track progress with organized task lists

## Available Commands

This project includes the following slash commands for Claude Code:

- `/speckit.constitution` - Establish or update project principles and guidelines
- `/speckit.specify` - Create detailed feature specifications
- `/speckit.plan` - Generate technical implementation plans
- `/speckit.tasks` - Create actionable, dependency-ordered task lists
- `/speckit.implement` - Execute implementation following the plan
- `/speckit.analyze` - Analyze existing code and features
- `/speckit.checklist` - Generate quality checklists
- `/speckit.clarify` - Clarify requirements and resolve ambiguities

## Project Structure

```
.
├── .claude/commands/     # Claude Code slash commands
├── .specify/             # Spec-Kit configuration and documentation
│   ├── memory/          # Templates and reference documents
│   └── README.md        # Spec-Kit documentation
└── scripts/             # Shell scripts for feature management
    └── bash/            # Bash scripts for setup and automation
```

## Getting Started

To create a new feature specification:

```bash
/speckit.specify "Your feature description here"
```

For more information about Spec-Kit, visit: https://github.com/github/spec-kit

## Documentation

- [Spec-Kit README](./.specify/README.md)
- [Spec-Kit Agent Guide](https://github.com/github/spec-kit/blob/main/AGENTS.md)
