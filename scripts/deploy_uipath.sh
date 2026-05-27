#!/usr/bin/env bash
## scripts/deploy_uipath.sh
## AuraQA — UiPath Package Build & Deployment Script
## Usage: ./scripts/deploy_uipath.sh [--env staging|production] [--feed <feed-url>] [--dry-run]
set -euo pipefail
IFS=$'\n\t'

# ─────────────────────────────────────────────────────────────
# Configuration defaults (override via env vars or CLI flags)
# ─────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
UIPATH_PROJECT_DIR="${PROJECT_ROOT}/uipath"
PROJECT_JSON="${UIPATH_PROJECT_DIR}/project.json"

ENVIRONMENT="${AURAQA_DEPLOY_ENV:-staging}"
ORCHESTRATOR_URL="${AURAQA_ORCHESTRATOR_URL:-https://cloud.uipath.com/your-org/your-tenant/orchestrator_}"
ORCHESTRATOR_TENANT="${AURAQA_ORCHESTRATOR_TENANT:-DefaultTenant}"
ORCHESTRATOR_FOLDER="${AURAQA_ORCHESTRATOR_FOLDER:-AuraQA}"
FEED_URL="${AURAQA_FEED_URL:-}"
API_KEY="${AURAQA_API_KEY:-}"
OUTPUT_DIR="${PROJECT_ROOT}/dist"
DRY_RUN=false
VERBOSE=false
PACKAGE_VERSION=""

# ─────────────────────────────────────────────────────────────
# Terminal colors
# ─────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

# ─────────────────────────────────────────────────────────────
# Logging helpers
# ─────────────────────────────────────────────────────────────
log_info()  { echo -e "${BLUE}[INFO]${NC}  $(date '+%Y-%m-%d %H:%M:%S') $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $(date '+%Y-%m-%d %H:%M:%S') $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $(date '+%Y-%m-%d %H:%M:%S') $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') $*" >&2; }

# ─────────────────────────────────────────────────────────────
# Parse CLI arguments
# ─────────────────────────────────────────────────────────────
parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --env)         ENVIRONMENT="$2"; shift 2 ;;
      --feed)        FEED_URL="$2"; shift 2 ;;
      --api-key)     API_KEY="$2"; shift 2 ;;
      --folder)      ORCHESTRATOR_FOLDER="$2"; shift 2 ;;
      --tenant)      ORCHESTRATOR_TENANT="$2"; shift 2 ;;
      --url)         ORCHESTRATOR_URL="$2"; shift 2 ;;
      --output)      OUTPUT_DIR="$2"; shift 2 ;;
      --version)     PACKAGE_VERSION="$2"; shift 2 ;;
      --dry-run)     DRY_RUN=true; shift ;;
      --verbose)     VERBOSE=true; shift ;;
      --help|-h)     usage; exit 0 ;;
      *)             log_error "Unknown argument: $1"; usage; exit 1 ;;
    esac
  done
}

usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  --env <staging|production>   Deployment environment (default: staging)
  --feed <url>                 NuGet/Orchestrator feed URL
  --api-key <key>              Orchestrator API key
  --folder <name>              Orchestrator folder (default: AuraQA)
  --tenant <name>              Orchestrator tenant (default: DefaultTenant)
  --url <url>                  Orchestrator URL
  --output <dir>               Output directory for .nupkg (default: dist/)
  --version <semver>           Override package version
  --dry-run                    Pack only, do not deploy
  --verbose                    Enable verbose output
  -h, --help                   Show this help message
EOF
}

# ─────────────────────────────────────────────────────────────
# Pre-flight checks
# ─────────────────────────────────────────────────────────────
preflight_checks() {
  log_info "Running pre-flight checks..."

  # Check uipcli is installed
  if ! command -v uipcli &>/dev/null; then
    if ! command -v uip &>/dev/null; then
      log_error "Neither 'uipcli' nor 'uip' found in PATH."
      log_error "Install UiPath CLI: https://docs.uipath.com/automation-suite/docs/uipath-command-line-interface"
      exit 1
    else
      UIP_CMD="uip"
    fi
  else
    UIP_CMD="uipcli"
  fi
  log_ok "UiPath CLI found: ${UIP_CMD}"

  # Verify project.json exists
  if [[ ! -f "${PROJECT_JSON}" ]]; then
    log_error "project.json not found at: ${PROJECT_JSON}"
    exit 1
  fi
  log_ok "project.json found"

  # Verify Main.xaml exists
  local main_xaml="${UIPATH_PROJECT_DIR}/workflows/Main.xaml"
  if [[ ! -f "${main_xaml}" ]]; then
    log_error "Main.xaml not found at: ${main_xaml}"
    exit 1
  fi
  log_ok "Main.xaml found"

  # Validate environment value
  if [[ "${ENVIRONMENT}" != "staging" && "${ENVIRONMENT}" != "production" ]]; then
    log_error "Invalid environment: ${ENVIRONMENT}. Must be 'staging' or 'production'."
    exit 1
  fi
  log_ok "Environment: ${ENVIRONMENT}"

  # Create output directory
  mkdir -p "${OUTPUT_DIR}"
  log_ok "Output directory ready: ${OUTPUT_DIR}"
}

# ─────────────────────────────────────────────────────────────
# Step 1: Analyze project
# ─────────────────────────────────────────────────────────────
analyze_project() {
  log_info "Analyzing UiPath project..."

  if [[ "${VERBOSE}" == true ]]; then
    ${UIP_CMD} package analyze "${UIPATH_PROJECT_DIR}" --output "${OUTPUT_DIR}/analysis_report.json" || true
  fi

  # Extract version from project.json if not overridden
  if [[ -z "${PACKAGE_VERSION}" ]]; then
    PACKAGE_VERSION=$(python3 -c "import json; print(json.load(open('${PROJECT_JSON}'))['projectVersion'])" 2>/dev/null || echo "1.0.0")
  fi
  log_ok "Package version: ${PACKAGE_VERSION}"
}

# ─────────────────────────────────────────────────────────────
# Step 2: Pack the project into .nupkg
# ─────────────────────────────────────────────────────────────
pack_project() {
  log_info "Packing UiPath project → .nupkg ..."

  local pack_args=(
    package pack
    "${UIPATH_PROJECT_DIR}"
    --output "${OUTPUT_DIR}"
    --version "${PACKAGE_VERSION}"
  )

  if [[ "${VERBOSE}" == true ]]; then
    pack_args+=(--verbose)
  fi

  log_info "Running: ${UIP_CMD} ${pack_args[*]}"
  ${UIP_CMD} "${pack_args[@]}"

  # Locate the generated .nupkg
  NUPKG_FILE=$(find "${OUTPUT_DIR}" -name "*.nupkg" -type f -newer "${PROJECT_JSON}" | sort -r | head -1)
  if [[ -z "${NUPKG_FILE}" ]]; then
    log_error "No .nupkg file found in ${OUTPUT_DIR} after packing."
    exit 1
  fi
  log_ok "Package created: ${NUPKG_FILE}"
}

# ─────────────────────────────────────────────────────────────
# Step 3: Deploy to Orchestrator
# ─────────────────────────────────────────────────────────────
deploy_package() {
  if [[ "${DRY_RUN}" == true ]]; then
    log_warn "DRY-RUN mode: Skipping deployment."
    log_info "Package ready for manual deployment: ${NUPKG_FILE}"
    return 0
  fi

  log_info "Deploying to Orchestrator (${ENVIRONMENT})..."

  # Validate required deployment parameters
  if [[ -z "${ORCHESTRATOR_URL}" || "${ORCHESTRATOR_URL}" == *"your-org"* ]]; then
    log_error "ORCHESTRATOR_URL is not configured. Set AURAQA_ORCHESTRATOR_URL or use --url."
    exit 1
  fi

  if [[ -z "${API_KEY}" ]]; then
    log_error "API key is required for deployment. Set AURAQA_API_KEY or use --api-key."
    exit 1
  fi

  local deploy_args=(
    package deploy
    "${NUPKG_FILE}"
    "${ORCHESTRATOR_URL}"
    --organizationUnit "${ORCHESTRATOR_FOLDER}"
  )

  # Add authentication
  if [[ -n "${API_KEY}" ]]; then
    deploy_args+=(--token "${API_KEY}")
  fi

  # Add tenant if specified
  if [[ -n "${ORCHESTRATOR_TENANT}" ]]; then
    deploy_args+=(--tenant "${ORCHESTRATOR_TENANT}")
  fi

  # Add feed URL if specified
  if [[ -n "${FEED_URL}" ]]; then
    deploy_args+=(--feedUrl "${FEED_URL}")
  fi

  if [[ "${VERBOSE}" == true ]]; then
    deploy_args+=(--verbose)
  fi

  log_info "Running: ${UIP_CMD} ${deploy_args[*]}"
  if ${UIP_CMD} "${deploy_args[@]}"; then
    log_ok "Deployment successful!"
  else
    local exit_code=$?
    log_error "Deployment failed with exit code: ${exit_code}"
    log_error "Troubleshooting:"
    log_error "  1. Verify Orchestrator URL: ${ORCHESTRATOR_URL}"
    log_error "  2. Verify API key / token is valid"
    log_error "  3. Verify folder '${ORCHESTRATOR_FOLDER}' exists in Orchestrator"
    log_error "  4. Run with --verbose for detailed output"
    exit ${exit_code}
  fi
}

# ─────────────────────────────────────────────────────────────
# Step 4: Post-deployment verification
# ─────────────────────────────────────────────────────────────
post_deploy_verify() {
  if [[ "${DRY_RUN}" == true ]]; then
    return 0
  fi

  log_info "Running post-deployment verification..."

  # List deployed packages to confirm
  ${UIP_CMD} package list "${ORCHESTRATOR_URL}" \
    --organizationUnit "${ORCHESTRATOR_FOLDER}" \
    --token "${API_KEY}" \
    --tenant "${ORCHESTRATOR_TENANT}" 2>/dev/null | grep -i "AuraQA" && {
    log_ok "Package verified in Orchestrator feed."
  } || {
    log_warn "Could not verify package in feed. Please check Orchestrator manually."
  }
}

# ─────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────
print_summary() {
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  AuraQA UiPath Deployment Summary"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  Project:       AuraQA.SelfHealingEngine"
  echo "  Version:       ${PACKAGE_VERSION}"
  echo "  Environment:   ${ENVIRONMENT}"
  echo "  Package:       ${NUPKG_FILE:-N/A}"
  echo "  Dry Run:       ${DRY_RUN}"
  if [[ "${DRY_RUN}" == false ]]; then
    echo "  Orchestrator:  ${ORCHESTRATOR_URL}"
    echo "  Folder:        ${ORCHESTRATOR_FOLDER}"
  fi
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
}

# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
main() {
  echo ""
  log_info "═══════════════════════════════════════════════════"
  log_info " AuraQA — UiPath Deployment Pipeline"
  log_info "═══════════════════════════════════════════════════"
  echo ""

  parse_args "$@"
  preflight_checks
  analyze_project
  pack_project
  deploy_package
  post_deploy_verify
  print_summary

  log_ok "Pipeline completed successfully."
}

main "$@"
