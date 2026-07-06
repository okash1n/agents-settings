---
name: tdd
description: Use this skill when the user explicitly asks for TDD or a tests-first workflow, or when developing a new feature with a test coverage requirement. Provides a structured red-green-refactor workflow with unit, integration, and E2E test guidance.
argument-hint: "[behavior-or-bug]"
compatibility: copilot
---

# Test-Driven Development Workflow

This skill provides a structured TDD workflow for projects that adopt tests-first development.

## When to Activate

- The user explicitly asks for TDD or tests-first development
- New feature work where test coverage is a stated requirement
- Adding API endpoints or components under a coverage policy

For routine bug fixes or refactors, add focused tests for the changed behavior instead of invoking this full workflow.

## Quick Mode

When invoked with a specific behavior or bug (e.g., `/tdd <behavior-or-bug>`), keep the session focused on that request:

1. Define the expected behavior or bug regression in one sentence.
2. Add the smallest failing test that proves the contract.
3. Implement the minimum code needed to pass.
4. Refactor only after the test is green.
5. Run the narrow test first, then broader relevant checks.

Report: behavior covered, tests added or changed, implementation files changed, commands run and results, remaining gaps or risks.

## Core Principles

### 1. Tests BEFORE Code
Within this workflow, the default is to write tests first, then implement code to make tests pass.

### 2. Coverage Guidance
- Coverage target follows the project's own standard (e.g., 80% as a common baseline); scale effort with the size of the change
- Cover relevant edge cases
- Test error scenarios
- Verify boundary conditions

### 3. Test Types

**Unit Tests** - Individual functions, utilities, component logic, pure functions, helpers.

**Integration Tests** - API endpoints, database operations, service interactions, external API calls.

**E2E Tests (Playwright)** - Critical user flows, complete workflows, browser automation, UI interactions. Applies to web UI projects only.

## TDD Workflow Steps

### Step 1: Write User Journeys
```
As a [role], I want to [action], so that [benefit]

Example:
As a user, I want to search for markets semantically,
so that I can find relevant markets even without exact keywords.
```

### Step 2: Generate Test Cases
For each user journey, create comprehensive test cases covering happy paths, edge cases, fallback behavior, and sorting/filtering logic.

### Step 3: Run Tests (They Should Fail)
Use the project's test runner. Examples:
```bash
npm test                      # Node.js
pytest                        # Python
bash tests/run-unit-tests.sh  # shell projects
# Tests should fail - we haven't implemented yet
```

### Step 4: Implement Code
Write minimal code to make tests pass.

### Step 5: Run Tests Again
Re-run the same test command (e.g., `npm test`, `pytest`):
```bash
npm test
# Tests should now pass
```

### Step 6: Refactor
Improve code quality while keeping tests green:
- Remove duplication
- Improve naming
- Optimize performance
- Enhance readability

### Step 7: Verify Coverage
Use the project's coverage tooling. Examples:
```bash
npm run test:coverage   # Node.js
pytest --cov            # Python
# Verify coverage meets the project's target
```

## Coverage Analysis

To analyze coverage and close gaps (`scripts/check-coverage.sh` auto-detects the test runner and reports a summary):

1. Identify the project's test tooling and run tests with coverage (e.g. `npm test -- --coverage`, `pytest --cov`, `go test -cover`)
2. Analyze the coverage report the test runner produces (e.g. `coverage/coverage-summary.json` for JS)
3. Identify files below the project's coverage target
4. For each under-covered file, analyze untested code paths, then generate unit tests for functions, integration tests for APIs, and E2E tests for critical flows
5. Verify new tests pass and show before/after coverage metrics

Focus on happy paths, error handling, edge cases (null / missing / empty values), and boundary conditions.

## Best Practices

1. **Write Tests First** - Always TDD
2. **One Assert Per Test** - Focus on single behavior
3. **Descriptive Test Names** - Explain what's tested
4. **Arrange-Act-Assert** - Clear test structure
5. **Mock External Dependencies** - Isolate unit tests
6. **Test Edge Cases** - Null, undefined, empty, large
7. **Test Error Paths** - Not just happy paths
8. **Keep Tests Fast** - Unit tests < 50ms each
9. **Clean Up After Tests** - No side effects
10. **Review Coverage Reports** - Identify gaps

## Success Metrics

- Coverage target met (per project standard, e.g., 80%)
- All tests passing (green)
- No skipped or disabled tests
- Fast test execution (< 30s for unit tests)
- E2E tests cover critical user flows
- Tests catch bugs before production

## References

These templates target JavaScript/TypeScript stacks; adapt the structure for other languages.

- `references/test-templates.md` - Unit, integration, E2E, and mocking code templates (JS/TS)
- `references/testing-mistakes.md` - Common pitfalls, file organization, coverage config, CI setup (JS/TS)

---

**Remember**: Give changed behavior a focused test. Tests are the safety net that enables confident refactoring, rapid development, and production reliability.
