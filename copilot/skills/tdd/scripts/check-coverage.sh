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
