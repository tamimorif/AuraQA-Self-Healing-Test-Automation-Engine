#!/usr/bin/env bash
### scripts/setup.sh
# ──────────────────────────────────────────────────────────────
# AuraQA — Development Environment Setup
# Usage: ./scripts/setup.sh
# ──────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
fail()  { echo -e "${RED}[FAIL]${NC}  $*"; exit 1; }

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║       AuraQA — Development Environment Setup        ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ── 1. Check prerequisites ──────────────────────────────────
info "Checking prerequisites..."

command -v python3 &>/dev/null || fail "python3 is required but not installed."
command -v pip3 &>/dev/null    || fail "pip3 is required but not installed."

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
info "  Python version: $PYTHON_VERSION"

if command -v node &>/dev/null; then
    NODE_VERSION=$(node --version)
    info "  Node.js version: $NODE_VERSION"
else
    warn "Node.js not found. Mock app setup will be skipped."
fi

ok "Prerequisites checked."

# ── 2. Create Python virtual environment ────────────────────
info "Setting up Python virtual environment..."

VENV_DIR="$PROJECT_ROOT/.venv"

if [ -d "$VENV_DIR" ]; then
    warn "Virtual environment already exists at $VENV_DIR — skipping creation."
else
    python3 -m venv "$VENV_DIR"
    ok "Created virtual environment at $VENV_DIR"
fi

# Activate venv
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
ok "Activated virtual environment."

# ── 3. Install Python dependencies ──────────────────────────
info "Installing Python dependencies..."

pip install --upgrade pip --quiet
pip install -r "$PROJECT_ROOT/requirements.txt" --quiet

# Install dev tools
pip install pylint mypy --quiet

ok "Python dependencies installed."

# ── 4. Install Node.js dependencies for mock_app ────────────
MOCK_APP_DIR="$PROJECT_ROOT/mock_app"

if [ -d "$MOCK_APP_DIR" ] && command -v npm &>/dev/null; then
    info "Installing Node.js dependencies for mock_app..."
    cd "$MOCK_APP_DIR"
    npm install --silent
    ok "Node.js dependencies installed."
    cd "$PROJECT_ROOT"
else
    if [ ! -d "$MOCK_APP_DIR" ]; then
        warn "mock_app/ directory not found — skipping Node.js setup."
    else
        warn "npm not found — skipping Node.js setup."
    fi
fi

# ── 5. Copy .env.example → .env ─────────────────────────────
ENV_EXAMPLE="$PROJECT_ROOT/infrastructure/.env.example"
ENV_FILE="$PROJECT_ROOT/.env"

if [ -f "$ENV_FILE" ]; then
    warn ".env file already exists — not overwriting."
else
    if [ -f "$ENV_EXAMPLE" ]; then
        cp "$ENV_EXAMPLE" "$ENV_FILE"
        ok "Copied .env.example → .env"
        info "  Edit .env to set your API keys and secrets."
    else
        warn "infrastructure/.env.example not found — skipping .env creation."
    fi
fi

# ── 6. Summary ──────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║                  Setup Complete ✅                   ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "  Next steps:"
echo "    1. Activate the venv:   source .venv/bin/activate"
echo "    2. Edit secrets:        vim .env"
echo "    3. Run tests:           pytest"
echo "    4. Start backend:       uvicorn backend.main:app --reload"
echo "    5. Start full stack:    cd infrastructure && docker compose up"
echo ""
