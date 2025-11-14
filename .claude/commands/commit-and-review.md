# Commit and Review Skill

Generate smart commits with standardized conventional messages and pre-merge validation.

## Usage

```
/commit-and-review [optional-message]
```

## Parameters

- `optional-message`: Optional custom commit message prefix

## Examples

```
/commit-and-review
/commit-and-review "feat: Add Hero component with animations"
/commit-and-review "fix: Resolve accessibility issues in contact form"
```

## What It Does

1. Analyzes staged changes
2. Categorizes changes (feature, fix, docs, refactor, test, etc.)
3. Generates conventional commit message
4. Runs pre-commit validation:
   - Type checking (TypeScript/Python)
   - Linting (ESLint/pylint)
   - Test execution
   - Coverage verification
5. Creates git commit
6. Prepares merge readiness report
7. Suggests next steps

## Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

Examples:
```
feat(landing-page): Add Hero component with scroll animations
fix(recipe-system): Resolve race condition in agent communication
docs: Update API documentation for new endpoints
test: Add integration tests for meal planning workflow
```

## Output

Returns commit confirmation:
- Commit hash
- Message
- Files changed
- Test results
- Coverage metrics
- Pre-merge validation results
- Merge readiness status

## When to Use

- Committing completed features
- Bug fixes
- Documentation updates
- Regular code commits
- Before pull request creation
