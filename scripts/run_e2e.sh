#!/usr/bin/env bash
### scripts/run_e2e.sh
# ──────────────────────────────────────────────────────────────
# AuraQA — End-to-End Test Runner
# Usage: ./scripts/run_e2e.sh
# ──────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
INFRA_DIR="$PROJECT_ROOT/infrastructure"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
fail()  { echo -e "${RED}[FAIL]${NC}  $*"; }

# Track exit code for teardown
EXIT_CODE=0

# ── Teardown on exit ─────────────────────────────────────────
cleanup() {
    echo ""
    info "Tearing down services..."
    cd "$INFRA_DIR"
    docker compose down --volumes --remove-orphans 2>/dev/null || true
    ok "Services stopped and cleaned up."

    if [ "$EXIT_CODE" -eq 0 ]; then
        echo -e "\n${GREEN}═══════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}  E2E Tests PASSED ✅${NC}"
        echo -e "${GREEN}═══════════════════════════════════════════════════${NC}\n"
    else
        echo -e "\n${RED}═══════════════════════════════════════════════════${NC}"
        echo -e "${RED}  E2E Tests FAILED ❌  (exit code: $EXIT_CODE)${NC}"
        echo -e "${RED}═══════════════════════════════════════════════════${NC}\n"
    fi

    exit "$EXIT_CODE"
}
trap cleanup EXIT

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║          AuraQA — End-to-End Test Runner            ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ── 1. Verify Docker ────────────────────────────────────────
info "Checking Docker..."
command -v docker &>/dev/null || { fail "Docker is required but not installed."; EXIT_CODE=1; exit 1; }
docker info &>/dev/null       || { fail "Docker daemon is not running."; EXIT_CODE=1; exit 1; }
ok "Docker is available."

# ── 2. Build & start services ───────────────────────────────
info "Building and starting services..."
cd "$INFRA_DIR"
docker compose build --quiet
docker compose up -d
ok "Services started."

# ── 3. Wait for health checks ───────────────────────────────
info "Waiting for services to become healthy..."

MAX_WAIT=120
INTERVAL=5
ELAPSED=0

wait_for_service() {
    local name="$1"
    local url="$2"
    local elapsed=0

    while [ "$elapsed" -lt "$MAX_WAIT" ]; do
        if curl -sf "$url" &>/dev/null; then
            ok "  $name is healthy (${elapsed}s)"
            return 0
        fi
        sleep "$INTERVAL"
        elapsed=$((elapsed + INTERVAL))
    done

    fail "  $name did not become healthy after ${MAX_WAIT}s"
    return 1
}

wait_for_service "Backend API" "http://localhost:8000/health" || { EXIT_CODE=1; exit 1; }
wait_for_service "Mock App"    "http://localhost:5173"        || { EXIT_CODE=1; exit 1; }
wait_for_service "Nginx Proxy" "http://localhost:80"          || { EXIT_CODE=1; exit 1; }

ok "All services healthy."

# ── 4. Run E2E tests ────────────────────────────────────────
info "Running E2E tests with pytest..."
cd "$PROJECT_ROOT"

# Activate venv if available
if [ -d "$PROJECT_ROOT/.venv" ]; then
    # shellcheck disable=SC1091
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

pytest \
    backend/tests/ \
    -m "e2e" \
    -v \
    --tb=long \
    --junitxml=reports/e2e-results.xml \
    --cov=backend \
    --cov-report=term-missing \
    || EXIT_CODE=$?

ok "E2E test run complete."
