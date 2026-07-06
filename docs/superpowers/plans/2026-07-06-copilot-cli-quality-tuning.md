# Copilot CLI 品質・検証チューニング Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** claude-code-starter-kit の品質・検証資産（tdd-workflow / security-review / verification-loop）を Copilot CLI（`~/.copilot`、symlink 配備）へ移植し、共通指示に完了条件規範を追加し、設定を現行 CLI 仕様（settings.json）に是正する。

**Architecture:** skill 3 本（`tdd` 新設、`security-checklist` 新設、`verify` 強化 + codex ミラー）+ `copilot-instructions.md` への規範追記 + `copilot/settings.json` の宣言的管理化（`config.json` は管理から外す）。配備は既存の `symlinks.json` + `scripts/apply_symlinks.py` の仕組みに乗せる。

**Tech Stack:** Markdown（SKILL.md / instructions）、JSON（settings.json / symlinks.json）、bash（check-coverage.sh）、Python（apply_symlinks.py は変更しない）

**Spec:** `docs/superpowers/specs/2026-07-06-copilot-cli-quality-tuning-design.md`

## Global Constraints

- コード・コメント・ドキュメントに絵文字を使わない。
- SKILL.md は既存の verify skill に合わせて英語で書く。`copilot-instructions.md` と README は日本語（だ・である調）。
- コミットメッセージは日本語で `copilot: <要約>` 形式（このブランチの既存スタイル）。1 タスク 1 コミット。
- `copilot/skills/.gitignore` はホワイトリスト方式（`*` を全無視）。新 skill は `!<name>` と `!<name>/**` の追記を忘れると git 管理から漏れる。
- `codex/config.toml` に未コミットの変更があるが、本計画とは無関係なので stage しない（`git add` は常にパス指定で行う）。
- `~/.copilot/skills` は repo の `copilot/skills` へのディレクトリ symlink 済み。skill ファイルを repo に置いた瞬間に実機へ反映される（apply_symlinks.py の再実行不要）。
- starter kit 参照元: `/Users/okash1n/ghq/github.com/cloudnative-co/claude-code-starter-kit`（以下 `$KIT` と表記。コマンド中では実パスを使う）。
- 実機確認済みの前提（2026-07-06）: Copilot CLI 1.0.68。`~/.copilot/config.json` は CLI 自動管理の実ファイル（symlink ではなくなっている）。`~/.copilot/settings.json` が実ファイルとして存在し、`model: "claude-opus-4.6-fast"`（現行モデル一覧に無い無効値）、`effortLevel: "high"`、hooks イベント名 `session-end`（docs 上の正式名は `sessionEnd`）を含む。effort の有効値は `none|low|medium|high|xhigh|max`。モデル一覧に `claude-opus-4.8-fast` が存在する。
- 設計からの変更点（実装時判断）: 移植 skill の名前は `security-review` ではなく **`security-checklist`** とする。CLI ビルトインの `/security-review` コマンド（v1.0.51+）とスラッシュ名が衝突するため。自動マッチは description ベースなので機能への影響はない。

---

### Task 1: `tdd` skill の新設

**Files:**
- Create: `copilot/skills/tdd/SKILL.md`
- Create: `copilot/skills/tdd/references/test-templates.md`（starter kit から無改変コピー）
- Create: `copilot/skills/tdd/references/testing-mistakes.md`（starter kit から無改変コピー）
- Create: `copilot/skills/tdd/scripts/check-coverage.sh`（starter kit 版のバグ 2 件を修正）
- Modify: `copilot/skills/.gitignore`

**Interfaces:**
- Consumes: なし（独立タスク）
- Produces: skill 名 `tdd`（`/tdd` で起動可能）。Task 4 の instructions が「TDD の依頼には tdd skill を使う」と参照する。

- [ ] **Step 1: references をコピー**

```bash
mkdir -p copilot/skills/tdd/references copilot/skills/tdd/scripts
cp /Users/okash1n/ghq/github.com/cloudnative-co/claude-code-starter-kit/skills/tdd-workflow/references/test-templates.md copilot/skills/tdd/references/
cp /Users/okash1n/ghq/github.com/cloudnative-co/claude-code-starter-kit/skills/tdd-workflow/references/testing-mistakes.md copilot/skills/tdd/references/
```

- [ ] **Step 2: SKILL.md を作成**

`copilot/skills/tdd/SKILL.md` を以下の内容で作成する。starter kit の `tdd-workflow/SKILL.md` がベース。変更点: frontmatter を Copilot 規約に変換（`when_to_use` 削除、`argument-hint` と `compatibility` 追加）、Claude 固有参照（`/tdd` command・`tdd-guide` agent）を削除、`commands/tdd.md` の 5 ステップを「Quick Mode」節として吸収、`commands/test-coverage.md` を「Coverage Analysis」節として吸収（80% ハードコードは「プロジェクト基準」表現に統一）。

````markdown
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
````

- [ ] **Step 3: check-coverage.sh を修正版で作成**

`copilot/skills/tdd/scripts/check-coverage.sh` を以下の内容で作成する。starter kit 版からの修正点: (1) pytest の `--cov-report=term-summary`（存在しないオプション）を `--cov-report=term` に修正、(2) ヘッダコメントが謳っていた pass/fail 判定を実装（検出できたカバレッジ率が閾値未満なら exit 1。検出不能な場合はその旨を報告して閾値を強制しない）。

````bash
#!/usr/bin/env bash
# check-coverage.sh - Auto-detect test runner and report coverage
# Usage: bash check-coverage.sh [threshold]
# Exits non-zero when a detected coverage percentage is below the threshold.
set -euo pipefail

THRESHOLD="${1:-80}"
COVERAGE=""

if [ -f "package.json" ]; then
    if grep -q '"vitest"' package.json 2>/dev/null; then
        OUTPUT=$(npx vitest run --coverage --reporter=verbose 2>/dev/null | grep -E "Statements|Branches|Functions|Lines|All files" || true)
        if [ -n "$OUTPUT" ]; then echo "$OUTPUT"; else echo "Run: npx vitest run --coverage"; fi
        COVERAGE=$(echo "$OUTPUT" | grep -E "All files" | grep -oE '[0-9]+(\.[0-9]+)?' | head -1 || true)
    elif grep -q '"jest"' package.json 2>/dev/null; then
        OUTPUT=$(npx jest --coverage --coverageReporters=text-summary 2>/dev/null | grep -E "Statements|Branches|Functions|Lines" || true)
        if [ -n "$OUTPUT" ]; then echo "$OUTPUT"; else echo "Run: npx jest --coverage"; fi
        COVERAGE=$(echo "$OUTPUT" | grep -E "Statements" | grep -oE '[0-9]+(\.[0-9]+)?' | head -1 || true)
    else
        echo "No recognized JS test runner found in package.json"
    fi
elif [ -f "go.mod" ]; then
    go test -coverprofile=coverage.out ./... 2>/dev/null
    TOTAL=$(go tool cover -func=coverage.out | tail -1)
    echo "$TOTAL"
    COVERAGE=$(echo "$TOTAL" | grep -oE '[0-9]+(\.[0-9]+)?%' | tr -d '%' | head -1 || true)
    rm -f coverage.out
elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
    OUTPUT=$(python3 -m pytest --cov --cov-report=term 2>/dev/null | grep -E "TOTAL|^Name" || true)
    if [ -n "$OUTPUT" ]; then echo "$OUTPUT"; else echo "Run: pytest --cov"; fi
    COVERAGE=$(echo "$OUTPUT" | grep -E "^TOTAL" | grep -oE '[0-9]+%' | tr -d '%' | head -1 || true)
elif [ -f "Cargo.toml" ]; then
    cargo test 2>/dev/null || echo "Run: cargo test"
else
    echo "No recognized test runner found"
    echo "Supported: vitest, jest (JS/TS), go test, pytest, cargo test"
    exit 1
fi

echo ""
echo "Target coverage threshold: ${THRESHOLD}%"
if [ -n "$COVERAGE" ]; then
    if awk -v c="$COVERAGE" -v t="$THRESHOLD" 'BEGIN { exit !(c >= t) }'; then
        echo "Coverage ${COVERAGE}% meets threshold: PASS"
    else
        echo "Coverage ${COVERAGE}% below threshold: FAIL"
        exit 1
    fi
else
    echo "Coverage percentage not detected; threshold not enforced"
fi
````

- [ ] **Step 4: .gitignore にホワイトリスト追記**

`copilot/skills/.gitignore` の `!ok-uninstall` の行の後（アルファベット順）に以下 2 行を追加する:

```
!tdd
!tdd/**
```

- [ ] **Step 5: 検証**

```bash
shellcheck copilot/skills/tdd/scripts/check-coverage.sh
```
Expected: 指摘ゼロ（または info レベルのみ。warning 以上は修正する）

```bash
copilot skill list 2>&1 | grep -i tdd
```
Expected: `tdd` が Personal skills として表示される

```bash
git status --short copilot/skills/
```
Expected: `copilot/skills/tdd/` 配下 4 ファイルと `.gitignore` が追跡対象として表示される（untracked に skill ファイルが残っていたら .gitignore の追記漏れ）

- [ ] **Step 6: Commit**

```bash
git add copilot/skills/tdd copilot/skills/.gitignore
git commit -m "copilot: tdd skill を starter kit から移植"
```

---

### Task 2: `security-checklist` skill の新設

**Files:**
- Create: `copilot/skills/security-checklist/SKILL.md`
- Create: `copilot/skills/security-checklist/references/vulnerability-patterns.md`（starter kit から無改変コピー）
- Create: `copilot/skills/security-checklist/assets/security-checklist.md`（starter kit から無改変コピー）
- Modify: `copilot/skills/.gitignore`

**Interfaces:**
- Consumes: なし（独立タスク）
- Produces: skill 名 `security-checklist`。Task 3 の verify skill と Task 4 の instructions が参照する。

- [ ] **Step 1: references / assets をコピー**

```bash
mkdir -p copilot/skills/security-checklist/references copilot/skills/security-checklist/assets
cp /Users/okash1n/ghq/github.com/cloudnative-co/claude-code-starter-kit/skills/security-review/references/vulnerability-patterns.md copilot/skills/security-checklist/references/
cp /Users/okash1n/ghq/github.com/cloudnative-co/claude-code-starter-kit/skills/security-review/assets/security-checklist.md copilot/skills/security-checklist/assets/
```

- [ ] **Step 2: SKILL.md を作成**

starter kit の `security-review/SKILL.md` をベースに `copilot/skills/security-checklist/SKILL.md` を作成する。変更点は 3 つだけ: (1) frontmatter の `name` を `security-checklist` に変更・`when_to_use` を削除・`compatibility: copilot` を追加・description 末尾にビルトイン補完の旨を追加、(2) 本文冒頭にビルトイン `/security-review` との関係を 1 文追加、(3) それ以外は原文のまま。

````markdown
---
name: security-checklist
description: Use this skill when adding authentication, handling user input, working with secrets, creating API endpoints, or implementing payment/sensitive features. Provides a comprehensive security checklist and WRONG/CORRECT patterns that complement the built-in /security-review command.
compatibility: copilot
---

# Security Review Skill

Ensures all code follows security best practices and identifies potential vulnerabilities.
Use this alongside the built-in `/security-review` command: the built-in command scans the current changes, while this skill provides the systematic category checklist and remediation patterns.

## When to Activate

- Implementing authentication or authorization
- Handling user input or file uploads
- Creating new API endpoints
- Working with secrets or credentials
- Implementing payment features
- Storing or transmitting sensitive data
- Integrating third-party APIs

## Security Checklist Categories

Review each category. See `references/vulnerability-patterns.md` for WRONG/CORRECT code examples.

1. **Secrets Management** -- No hardcoded secrets; all in env vars; `.env*` gitignored
2. **Input Validation** -- Schema validation; file upload size/type/extension checks
3. **SQL Injection** -- Parameterized queries only; no string concatenation
4. **Auth & Authorization** -- httpOnly cookies; RBAC; row-level/object-level authorization where needed
5. **XSS Prevention** -- DOMPurify for user HTML; CSP headers configured
6. **CSRF Protection** -- CSRF tokens on state-changing ops; SameSite=Strict cookies
7. **Rate Limiting** -- All endpoints rate-limited; stricter on expensive operations
8. **Data Exposure** -- No secrets in logs; generic error messages to users
9. **High-Risk Integrations** -- Payments, wallets, third-party APIs, and webhooks validated when present
10. **Dependencies** -- `npm audit` clean; lock files committed; Dependabot enabled

Full checkbox checklist: `assets/security-checklist.md`

## Pre-Deployment Checklist

Before ANY production deployment, confirm ALL of the following:

- [ ] No hardcoded secrets, all in env vars
- [ ] All user inputs validated
- [ ] All queries parameterized
- [ ] User content sanitized (XSS)
- [ ] CSRF protection enabled
- [ ] Proper token handling (httpOnly cookies)
- [ ] Authorization role checks in place
- [ ] Rate limiting on all endpoints
- [ ] HTTPS enforced
- [ ] Security headers configured (CSP, X-Frame-Options)
- [ ] No sensitive data in error messages or logs
- [ ] Dependencies up to date, no vulnerabilities
- [ ] CORS properly configured
- [ ] File uploads validated (size, type)

## References

- `references/vulnerability-patterns.md` -- All WRONG/CORRECT code examples by vulnerability type
- `assets/security-checklist.md` -- Full security review checklist (markdown checkboxes)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Next.js Security](https://nextjs.org/docs/security)
- [Web Security Academy](https://portswigger.net/web-security)

---

**Security is not optional.** One vulnerability can compromise the entire platform. When in doubt, err on the side of caution.
````

- [ ] **Step 3: .gitignore にホワイトリスト追記**

`copilot/skills/.gitignore` の `!ok-uninstall` の後・`!tdd` の前（アルファベット順）に以下 2 行を追加する:

```
!security-checklist
!security-checklist/**
```

- [ ] **Step 4: 検証**

```bash
copilot skill list 2>&1 | grep -i security-checklist
git status --short copilot/skills/
```
Expected: `security-checklist` が Personal skills として表示され、3 ファイルが追跡対象になる

- [ ] **Step 5: Commit**

```bash
git add copilot/skills/security-checklist copilot/skills/.gitignore
git commit -m "copilot: security-checklist skill を starter kit から移植"
```

---

### Task 3: `verify` skill の強化と codex ミラー反映

**Files:**
- Modify: `copilot/skills/verify/SKILL.md`
- Modify: `codex/skills/verify/SKILL.md`（末尾 Compatibility 節以外は copilot 版と同一に保つ）

**Interfaces:**
- Consumes: Task 2 の skill 名 `security-checklist`（Compatibility 節から参照）
- Produces: `/verify [quick|full|pre-commit|pre-pr]`。Task 4 の instructions が参照する。

- [ ] **Step 1: copilot 版 SKILL.md を改訂**

`copilot/skills/verify/SKILL.md` に次の変更を加える（既存の構造・文体は維持）:

1. frontmatter に `argument-hint: "[quick|full|pre-commit|pre-pr]"` を `description` の次の行に追加
2. Required Order を 7 ステップから 9 ステップに拡張: 既存 5（Log Audit）の後に新規「6. Secrets Scan」を挿入、既存 6（Git Status）は 7 に、その後に新規「8. Diff Review」を挿入、既存 7（Security Scan）は 9 に繰り下げ
3. Mode Guidance の `full` に `Secrets scan` と `Diff review` を、`pre-commit` に `Secrets scan` を追加
4. Output Format に `Secrets` と `Diff` の行を追加
5. Compatibility 節の Copilot 行にビルトイン・skill 参照を追記

新規セクションの本文:

````markdown
### 6. Secrets Scan

- If a dedicated scanner is available in the repo or on PATH (gitleaks, trufflehog), run it against the changes.
- Otherwise, review the added lines of `git diff` for credentials, tokens, and keys. Do not report PASS based on a repository-wide grep.
- For deeper guidance on sensitive surfaces, follow the security-checklist skill when it is available.
````

````markdown
### 8. Diff Review

- Show the change surface with `git diff --stat` (and `git diff HEAD~1 --name-only` when reviewing a commit).
- Review each changed file for unintended changes, missing error handling, and potential edge cases.
````

Mode Guidance の変更後の姿:

````markdown
### `quick`

- Build
- Types

### `full`

- Build
- Types
- Lint
- Tests
- Log audit
- Secrets scan
- Git status
- Diff review

### `pre-commit`

- Build
- Types
- Lint
- Targeted tests or the smallest meaningful test set
- Secrets scan
- Git status

### `pre-pr`

- Full flow
- Add an existing security-oriented check if present
````

Output Format の変更後の姿:

````markdown
```text
VERIFICATION: [PASS/FAIL]

Build:    [OK/FAIL/N/A]
Types:    [OK/X errors/N/A]
Lint:     [OK/X issues/N/A]
Tests:    [X/Y passed, Z% coverage/N/A]
Secrets:  [OK/X found/N/A]
Security: [OK/X found/N/A]
Logs:     [OK/X found]
Diff:     [X files changed]

Ready for PR: [YES/NO]
```
````

copilot 版の Compatibility 節の変更後の姿:

````markdown
## Compatibility

- Codex: use the same workflow so verification stays aligned with Copilot.
- Copilot: keep this as a skill instead of relying on `.claude/commands`, so starter-kit managed Claude commands stay untouched. The built-in `/security-review` command and the security-checklist skill can serve as the security-oriented check in `pre-pr`.
````

- [ ] **Step 2: codex 版へミラー反映**

`codex/skills/verify/SKILL.md` に Step 1 と同一の変更（frontmatter の argument-hint、Required Order 9 ステップ化、Mode Guidance、Output Format）を適用する。Compatibility 節のみ codex 版の既存文言を維持する:

````markdown
## Compatibility

- Codex: use this as a reusable verification workflow skill rather than a custom prompt.
- Copilot: use the same workflow and report shape so verification behavior stays aligned across agents.
````

- [ ] **Step 3: 差分が Compatibility 節のみであることを確認**

```bash
diff codex/skills/verify/SKILL.md copilot/skills/verify/SKILL.md
```
Expected: 末尾 Compatibility 節の数行のみが差分として表示される

- [ ] **Step 4: Commit**

```bash
git add copilot/skills/verify/SKILL.md codex/skills/verify/SKILL.md
git commit -m "copilot: verify skill に secrets スキャンと diff レビューを追加（codex ミラー含む）"
```

---

### Task 4: `copilot-instructions.md` に検証と完了条件の規範を追記

**Files:**
- Modify: `copilot/copilot-instructions.md`（`## コーディング規約` と `## Git` の間に新セクション挿入）

**Interfaces:**
- Consumes: Task 1 の `tdd`、Task 2 の `security-checklist`、Task 3 の `verify`（skill 名で参照）
- Produces: 全セッションに適用される完了条件規範

- [ ] **Step 1: セクションを挿入**

`## Git` セクションの直前に以下を挿入する:

````markdown
## 検証と完了条件

- 必要なテスト・チェックが実際に通るまで、完了と主張しない。
- 最小の関連チェックを先に実行し、完了報告の前に広い検証を行う。
- skip したチェックや失敗したチェックは、理由と残リスク付きで報告する。
- コミット前・PR 前の検証には verify skill を使う。TDD の依頼には tdd skill を使い、認証・ユーザー入力・secrets などに触れる変更では security-checklist skill を参照する。
- API・コマンド・import・ファイルパスは使用前に実在確認する。
- 同じアプローチが繰り返し失敗したら、止まって別アプローチかブロッカー報告に切り替える。
````

- [ ] **Step 2: 検証と Commit**

```bash
grep -n "検証と完了条件" copilot/copilot-instructions.md
git add copilot/copilot-instructions.md
git commit -m "copilot: 共通指示に検証と完了条件の規範を追加"
```

---

### Task 5: `settings.json` の宣言的管理化と `config.json` の管理外し

**Files:**
- Create: `copilot/settings.json`
- Modify: `symlinks.json`（config.json エントリ削除、settings.json エントリ追加）
- Delete: `copilot/config.json`
- Modify: `docs/superpowers/specs/2026-07-06-copilot-cli-quality-tuning-design.md`（前提の現実差分を追記）

**Interfaces:**
- Consumes: なし
- Produces: `~/.copilot/settings.json` → `copilot/settings.json` の symlink。model / effortLevel / hooks の正式値。

- [ ] **Step 1: `copilot/settings.json` を作成**

実機 `~/.copilot/settings.json`（CLI が自動移行で生成済み）をベースに、次の是正を加えた内容で作成する: model を実在する `claude-opus-4.8-fast` に更新、effortLevel を `xhigh` に引き上げ、hooks イベント名を docs 正式表記 `sessionEnd` に修正（`type: "command"` を明示）、移行で欠落した `banner: "never"` を復元。

````json
{
  "autoUpdate": false,
  "autoUpdatesChannel": "stable",
  "banner": "never",
  "includeCoAuthoredBy": false,
  "model": "claude-opus-4.8-fast",
  "effortLevel": "xhigh",
  "hooks": {
    "sessionEnd": [
      {
        "type": "command",
        "bash": "KB_JUDGE_FASTPATH_COMMAND=\"/Users/okash1n/.local/lib/kb-mcp/hooks/heuristic-fastpath.py\" /Users/okash1n/.local/lib/kb-mcp/hooks/copilot-session-end.sh"
      }
    ]
  }
}
````

- [ ] **Step 2: `symlinks.json` を更新**

`home_symlinks` から `copilot/config.json` のエントリ（target `~/.copilot/config.json`）を削除し、同じ位置に以下を追加する:

````json
{
  "target": "~/.copilot/settings.json",
  "source": "copilot/settings.json",
  "kind": "file"
}
````

- [ ] **Step 3: repo の `copilot/config.json` を削除**

```bash
git rm copilot/config.json
```

実機 `~/.copilot/config.json` は既に CLI 自動管理の実ファイル（trusted_folders 等の runtime 値のみ保持）なので何もしない。

- [ ] **Step 4: 実機の settings.json を symlink に置換**

`apply_symlinks.py` の `ensure_symlink` は非 symlink の既存ファイルを `[skip]` するため、既存実ファイルを退避してから適用する:

```bash
cp ~/.copilot/settings.json ~/.copilot/settings.json.bak-$(date +%Y%m%d-%H%M%S)
rm ~/.copilot/settings.json
python3 scripts/apply_symlinks.py
readlink ~/.copilot/settings.json
```
Expected: `apply_symlinks.py` が `[link] ~/.copilot/settings.json -> .../copilot/settings.json` を出力し、`readlink` が repo パスを返す

- [ ] **Step 5: JSON 妥当性と設定反映を検証**

```bash
python3 -c "import json; json.load(open('copilot/settings.json')); json.load(open('symlinks.json')); print('json ok')"
copilot --list-env 2>&1 | head -40
```
Expected: `json ok`。`--list-env` の出力に settings / instructions / skills のロード状態が表示され、エラーが出ない（model 名が無効な場合はここで検出する）

- [ ] **Step 6: スペックへ現実差分を追記**

`docs/superpowers/specs/2026-07-06-copilot-cli-quality-tuning-design.md` の「C. 設定基盤の是正」節の末尾に以下を追記する:

````markdown
> 実装時追記（2026-07-06）: 実装開始時点で CLI 自身が移行を完了しており、`~/.copilot/config.json` は既に自動管理の実ファイル、`~/.copilot/settings.json` は CLI 生成の実ファイルになっていた（設計時の「settings.json 不在」から状況が変化）。このため本節の実作業は「CLI 生成の settings.json を是正した上で宣言的管理（symlink）に置き換え、repo 側 config.json を削除する」となった。また移植 skill 名はビルトイン `/security-review` コマンドとの衝突を避けるため `security-checklist` に変更した。
````

- [ ] **Step 7: Commit**

```bash
git add copilot/settings.json symlinks.json docs/superpowers/specs/2026-07-06-copilot-cli-quality-tuning-design.md
git commit -m "copilot: settings.json を宣言的管理に移行し config.json を管理から外す"
```

（`git rm` 済みの `copilot/config.json` は自動で stage されている。`git status` で `codex/config.toml` が含まれていないことを確認してからコミットする）

---

### Task 6: README 更新と総合検証

**Files:**
- Modify: `README.md`（管理境界の記述に config.json / settings.json の扱いを追記）

**Interfaces:**
- Consumes: Task 1〜5 の成果すべて
- Produces: 最終検証レポート

- [ ] **Step 1: README の管理境界に 1 行追記**

`README.md` の「管理境界:」リストの末尾に以下を追加する:

````markdown
- `~/.copilot/config.json` は CLI が自動管理する内部状態のため repo 管理しない（ユーザー設定は `copilot/settings.json` で管理する）
````

- [ ] **Step 2: skill 認識の総合確認**

```bash
copilot skill list 2>&1
```
Expected: Personal skills に `ok-*` 7 個 + `verify` + `tdd` + `security-checklist` が表示される

- [ ] **Step 3: 非対話スモーク（model / effort / instructions の反映確認）**

```bash
copilot -p "Reply with exactly: ok" 2>&1 | tail -5
```
Expected: エラーなく応答が返る（無効な model 値ならここでエラーになる）

- [ ] **Step 4: sessionEnd hook の発火確認**

Step 3 のセッション終了後に kb-mcp hook が走ったことをログで確認する:

```bash
ls -t ~/.copilot/logs/ | head -3
grep -ril "hook" ~/.copilot/logs/$(ls -t ~/.copilot/logs/ | head -1) 2>/dev/null || echo "no hook mention in latest log"
```

ログで確認できない場合のフォールバック: `copilot/settings.json` の `sessionEnd` 配列に一時的に `{"type": "command", "bash": "touch /tmp/copilot-hook-fired"}` を追加し、`copilot -p "Reply with exactly: ok"` 実行後に `/tmp/copilot-hook-fired` の存在を確認し、確認後は一時 hook を削除して元に戻す（diff が残らないことを `git diff copilot/settings.json` で確認）。

Expected: hook の実行痕跡が確認できる。確認できない場合は完了と主張せず、残課題として報告する

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "docs: copilot 設定の管理境界を README に追記"
```

---

## 実行後の全体レビュー

全タスク完了後、多観点レビュー（正確性 / スペック準拠 / 単純化 / セキュリティ）を行い、指摘を severity 順に修正してから完了報告する。
