#!/usr/bin/env bash
# Notify SDD workflow status update
# Usage: notify-sdd-status.sh --stage <stage> --status <status> [--taskId <taskId>] [--repo <repo>] [--branch <branch>] [--ext '{"key":"value"}']

set -e

BASE_URL="http://127.0.0.1:17345"

# Parse command line arguments
TASK_ID=""
STAGE=""
STATUS=""
REPO=""
BRANCH=""
EXT=""

usage() {
    echo "Usage: $0 --stage <stage> --status <status> [--taskId <taskId>] [--repo <repo>] [--branch <branch>]"
    echo ""
    echo "  --taskId   ONES task ID (optional. search taskId by branchName when taskId is empty)"
    echo "  --stage    Stage name, e.g. SPEC_DESIGN, CODING (required)"
    echo "  --status   Stage status: start / finished / failed (required)"
    echo "  --repo     Repository path (optional, used for auto-creating task)"
    echo "  --branch   Branch name (optional)"
    echo "  --ext      Extra key-value pairs as JSON object string, e.g. '{\"key\":\"value\"}' (optional)"
    echo "  --help     Show this help message"
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --taskId)
            TASK_ID="$2"
            shift 2
            ;;
        --stage)
            STAGE="$2"
            shift 2
            ;;
        --status)
            STATUS="$2"
            shift 2
            ;;
        --repo)
            REPO="$2"
            shift 2
            ;;
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        --ext)
            EXT="$2"
            shift 2
            ;;
        --help|-h)
            usage
            ;;
        *)
            echo "ERROR: Unknown argument: $1" >&2
            usage
            ;;
    esac
done

# Validate required arguments
if [[ -z "$STAGE" ]]; then
    echo "ERROR: --stage is required" >&2
    exit 1
fi

if [[ -z "$STATUS" ]]; then
    echo "ERROR: --status is required" >&2
    exit 1
fi

# Validate status value
if [[ "$STATUS" != "start" && "$STATUS" != "finished" && "$STATUS" != "failed" ]]; then
    echo "ERROR: --status must be one of: start, finished, failed" >&2
    exit 1
fi

# Auto-detect repo from git if not provided
if [[ -z "$REPO" ]]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    source "$SCRIPT_DIR/common.sh"
    REPO="$(get_repo_root)"
fi

# Auto-detect branch from git if not provided
if [[ -z "$BRANCH" ]]; then
    if git rev-parse --abbrev-ref HEAD >/dev/null 2>&1; then
        BRANCH="$(git rev-parse --abbrev-ref HEAD)"
    fi
fi

# Build JSON payload
build_payload() {
    local payload
    payload=$(printf '{"stage":"%s","status":"%s"' \
        "$STAGE" "$STATUS")

    if [[ -n "$TASK_ID" ]]; then
        payload="{\"taskId\":\"${TASK_ID}\",${payload:1}"
    fi

    if [[ -n "$REPO" ]]; then
        payload="${payload},\"repo\":\"${REPO}\""
    fi

    if [[ -n "$BRANCH" ]]; then
        payload="${payload},\"branch\":\"${BRANCH}\""
    fi

    # Only include ext if it is non-empty and not an empty JSON object {}
    local ext_trimmed
    ext_trimmed="$(echo "$EXT" | tr -d '[:space:]')"
    if [[ -n "$ext_trimmed" && "$ext_trimmed" != "{}" ]]; then
        payload="${payload},\"ext\":${EXT}"
    fi

    payload="${payload}}"
    echo "$payload"
}

PAYLOAD="$(build_payload)"

# Send request
# Use a temp file to capture body separately from status code (macOS-compatible)
HTTP_BODY_FILE=$(mktemp)
HTTP_CODE=$(curl -s \
    -X POST "${BASE_URL}/workflow/update" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" \
    -o "$HTTP_BODY_FILE" -w "%{http_code}" || true)
HTTP_BODY=$(cat "$HTTP_BODY_FILE")
rm -f "$HTTP_BODY_FILE"

if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
    echo "$HTTP_BODY"
    exit 0
else
    echo "ERROR: Request failed with HTTP status $HTTP_CODE" >&2
    echo "$HTTP_BODY" >&2
    exit 1
fi

