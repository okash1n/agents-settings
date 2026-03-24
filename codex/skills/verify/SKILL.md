---
name: verify
description: Run repository verification in a fixed order before commit or PR work. Use when the user asks to verify changes, run pre-commit or pre-PR checks, or produce a concise readiness report.
compatibility: codex,copilot
---

# Verify

Use this skill when the user wants a verification pass on the current repository state.

## Inputs

`$ARGUMENTS` may be omitted or set to one of:

- `quick`: build + type checks only
- `full`: full verification flow (default)
- `pre-commit`: checks relevant before committing
- `pre-pr`: full verification plus a security-oriented scan if the repo has one

If no argument is given, treat it as `full`.

## Workflow

1. Identify the repository's actual verification commands from local context first.
2. Run checks in the required order below.
3. Stop immediately if the build step fails.
4. If a later step fails, continue only when the remaining checks still provide useful signal and are safe to run.
5. Produce the concise report format from this skill instead of dumping raw command output.

## Required Order

### 1. Build Check

- Run the project's build command.
- If it fails, report the failure and stop the workflow.

### 2. Type Check

- Run the repository's type checker when one exists.
- Report errors with file and line when available.
- If the repo has no type checker, say `N/A`.

### 3. Lint Check

- Run the repository's linter when one exists.
- Report warnings and errors briefly.
- If the repo has no linter, say `N/A`.

### 4. Test Suite

- Run the relevant test suite for the requested mode.
- Report pass/fail counts when available.
- Report coverage percentage only if the test tooling exposes it.
- If the repo has no tests, say `N/A`.

### 5. Log Audit

- Search source files for `console.log`.
- If the stack is not JavaScript/TypeScript, also look for the nearest equivalent debug logging pattern only when it is clearly conventional in that repo.
- Report concrete locations briefly.

### 6. Git Status

- Summarize uncommitted changes.
- Summarize files changed since `HEAD`.

### 7. Security Scan

- Only for `pre-pr`, run an existing security-oriented check if the repo already defines one.
- Do not invent new external tooling.
- If none exists, say `N/A`.

## Command Selection Rules

- Prefer existing documented commands from `package.json`, `Makefile`, task runners, repo docs, or CI config.
- Do not invent heavyweight checks that the repo does not already use.
- Keep the scope proportional to the requested mode.
- If multiple alternatives exist, choose the one closest to the repo's normal developer workflow.

## Mode Guidance

### `quick`

- Build
- Types

### `full`

- Build
- Types
- Lint
- Tests
- Log audit
- Git status

### `pre-commit`

- Build
- Types
- Lint
- Targeted tests or the smallest meaningful test set
- Git status

### `pre-pr`

- Full flow
- Add an existing security-oriented check if present

## Output Format

Produce a concise report in this shape:

```text
VERIFICATION: [PASS/FAIL]

Build:    [OK/FAIL/N/A]
Types:    [OK/X errors/N/A]
Lint:     [OK/X issues/N/A]
Tests:    [X/Y passed, Z% coverage/N/A]
Security: [OK/X found/N/A]
Logs:     [OK/X found]

Ready for PR: [YES/NO]
```

After the summary, list only the critical issues with short fix suggestions.

## Compatibility

- Codex: use this as a reusable verification workflow skill rather than a custom prompt.
- Copilot: use the same workflow and report shape so verification behavior stays aligned across agents.
