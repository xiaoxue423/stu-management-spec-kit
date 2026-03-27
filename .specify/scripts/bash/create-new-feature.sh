#!/usr/bin/env bash

set -e

JSON_MODE=false
SHORT_NAME=""
BRANCH_NUMBER=""
ARGS=()
i=1
while [ $i -le $# ]; do
    arg="${!i}"
    case "$arg" in
        --json)
            JSON_MODE=true
            ;;
        --short-name)
            if [ $((i + 1)) -gt $# ]; then
                echo 'Error: --short-name requires a value' >&2
                exit 1
            fi
            i=$((i + 1))
            next_arg="${!i}"
            # Check if the next argument is another option (starts with --)
            if [[ "$next_arg" == --* ]]; then
                echo 'Error: --short-name requires a value' >&2
                exit 1
            fi
            SHORT_NAME="$next_arg"
            ;;
        --number)
            if [ $((i + 1)) -gt $# ]; then
                echo 'Error: --number requires a value' >&2
                exit 1
            fi
            i=$((i + 1))
            next_arg="${!i}"
            if [[ "$next_arg" == --* ]]; then
                echo 'Error: --number requires a value' >&2
                exit 1
            fi
            # Validate that the number is actually a number
            if ! [[ "$next_arg" =~ ^[0-9]+$ ]]; then
                echo "Error: --number requires a numeric value, got '$next_arg'" >&2
                exit 1
            fi
            BRANCH_NUMBER="$next_arg"
            ;;
        --help|-h)
            echo "Usage: $0 [--json] [--short-name <name>] [--number N] <feature_description>"
            echo ""
            echo "Options:"
            echo "  --json              Output in JSON format"
            echo "  --short-name <name> Provide a custom short name (2-4 words) for the branch"
            echo "  --number N          Specify branch number manually (overrides auto-detection)"
            echo "  --help, -h          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 'Add user authentication system' --short-name 'user-auth'"
            echo "  $0 'Implement OAuth2 integration for API' --number 5"
            exit 0
            ;;
        *)
            ARGS+=("$arg")
            ;;
    esac
    i=$((i + 1))
done

FEATURE_DESCRIPTION="${ARGS[*]}"
if [ -z "$FEATURE_DESCRIPTION" ]; then
    echo "Usage: $0 [--json] [--short-name <name>] [--number N] <feature_description>" >&2
    exit 1
fi

# Function to find the repository root by searching for existing project markers
find_repo_root() {
    local dir="$1"
    while [ "$dir" != "/" ]; do
        if [ -d "$dir/.git" ] || [ -d "$dir/.specify" ]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    return 1
}

# Function to check existing branches (local and remote) and return next available number
# Branch format: feature/SPEC-YYYYMMDDHHmm/NNN-suffix
check_existing_branches() {
    # Fetch all remotes to get latest branch info (suppress errors if no remotes)
    git fetch --all --prune >/dev/null 2>&1 || true

    # --- Remote branches ---
    local all_remote
    all_remote=$(git ls-remote --heads origin 2>/dev/null || true)

    # Format: feature/SPEC-YYYYMMDDHHmm/NNN-*
    local remote_new
    remote_new=$(echo "$all_remote" \
        | grep -E "refs/heads/feature/SPEC-[0-9]{12}/[0-9]+-" \
        | sed 's|.*refs/heads/feature/SPEC-[0-9]*/\([0-9]*\)-.*|\1|' \
        || true)

    # --- Local branches ---
    local all_local
    all_local=$(git branch 2>/dev/null || true)

    # Format: feature/SPEC-YYYYMMDDHHmm/NNN-*
    local local_new
    local_new=$(echo "$all_local" \
        | grep -E "^[* ]*feature/SPEC-[0-9]{12}/[0-9]+-" \
        | sed 's/^[* ]*//' \
        | sed 's|feature/SPEC-[0-9]*/\([0-9]*\)-.*|\1|' \
        || true)

    # --- specs/ directory (covers manually created dirs or orphaned specs) ---
    local spec_dirs
    spec_dirs=""
    if [ -d "$SPECS_DIR" ]; then
        spec_dirs=$(find "$SPECS_DIR" -maxdepth 1 -mindepth 1 -type d \
            | xargs -n1 basename 2>/dev/null \
            | grep -E "^[0-9]+-" \
            | sed 's/^\([0-9]*\)-.*/\1/' \
            || true)
    fi

    # Take the global maximum across all sources, then +1
    local max_num=0
    for num in $remote_new $local_new $spec_dirs; do
        [ -z "$num" ] && continue
        if [[ "$num" =~ ^[0-9]+$ ]]; then
            num=$((10#$num))
            if [ "$num" -gt "$max_num" ]; then
                max_num=$num
            fi
        fi
    done

    echo $((max_num + 1))
}

# Function to clean and format a branch name
clean_branch_name() {
    local name="$1"
    echo "$name" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//' | sed 's/-$//'
}

# Resolve repository root. Prefer git information when available, but fall back
# to searching for repository markers so the workflow still functions in repositories that
# were initialised with --no-git.
SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if git rev-parse --show-toplevel >/dev/null 2>&1; then
    REPO_ROOT=$(git rev-parse --show-toplevel)
    HAS_GIT=true
else
    REPO_ROOT="$(find_repo_root "$SCRIPT_DIR")"
    if [ -z "$REPO_ROOT" ]; then
        echo "Error: Could not determine repository root. Please run this script from within the repository." >&2
        exit 1
    fi
    HAS_GIT=false
fi

cd "$REPO_ROOT"

SPECS_DIR="$REPO_ROOT/specs"
mkdir -p "$SPECS_DIR"

# Function to generate branch name with stop word filtering and length filtering
generate_branch_name() {
    local description="$1"

    # Common stop words to filter out
    local stop_words="^(i|a|an|the|to|for|of|in|on|at|by|with|from|is|are|was|were|be|been|being|have|has|had|do|does|did|will|would|should|could|can|may|might|must|shall|this|that|these|those|my|your|our|their|want|need|add|get|set)$"

    # Convert to lowercase and split into words
    local clean_name=$(echo "$description" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/ /g')

    # Filter words: remove stop words and words shorter than 3 chars (unless they're uppercase acronyms in original)
    local meaningful_words=()
    for word in $clean_name; do
        # Skip empty words
        [ -z "$word" ] && continue

        # Keep words that are NOT stop words AND (length >= 3 OR are potential acronyms)
        if ! echo "$word" | grep -qiE "$stop_words"; then
            if [ ${#word} -ge 3 ]; then
                meaningful_words+=("$word")
            else
                # Keep short words if they appear as uppercase in original (likely acronyms)
                # Use tr for better compatibility instead of ${word^^}
                word_upper=$(echo "$word" | tr '[:lower:]' '[:upper:]')
                if echo "$description" | grep -q "\b$word_upper\b"; then
                    meaningful_words+=("$word")
                fi
            fi
        fi
    done

    # If we have meaningful words, use first 3-4 of them
    if [ ${#meaningful_words[@]} -gt 0 ]; then
        local max_words=3
        if [ ${#meaningful_words[@]} -ge 4 ]; then max_words=4; fi

        local result=""
        local count=0
        for word in "${meaningful_words[@]}"; do
            if [ $count -ge $max_words ]; then break; fi
            if [ -n "$result" ]; then result="$result-"; fi
            result="$result$word"
            count=$((count + 1))
        done
        echo "$result"
    else
        # Fallback to original logic if no meaningful words found
        local cleaned=$(clean_branch_name "$description")
        echo "$cleaned" | tr '-' '\n' | grep -v '^$' | head -3 | tr '\n' '-' | sed 's/-$//'
    fi
}

# Generate branch name
if [ -n "$SHORT_NAME" ]; then
    # Use provided short name, just clean it up
    BRANCH_SUFFIX=$(clean_branch_name "$SHORT_NAME")
else
    # Generate from description with smart filtering
    BRANCH_SUFFIX=$(generate_branch_name "$FEATURE_DESCRIPTION")
fi

# Validate that we have a non-empty branch suffix
if [ -z "$BRANCH_SUFFIX" ]; then
    echo "Error: Could not generate a branch name from the provided description or short name" >&2
    exit 1
fi

# Determine branch number
if [ -z "$BRANCH_NUMBER" ]; then
    if [ "$HAS_GIT" = true ]; then
        # Check existing branches on remotes
        BRANCH_NUMBER=$(check_existing_branches)
    else
        # No git available, start from 1
        BRANCH_NUMBER=1
    fi
fi

# Validate that BRANCH_NUMBER is a valid number
if ! [[ "$BRANCH_NUMBER" =~ ^[0-9]+$ ]]; then
    echo "Error: Invalid branch number '$BRANCH_NUMBER'. Expected a positive integer." >&2
    exit 1
fi

SPEC_TIMESTAMP=$(date +%Y%m%d%H%M)
FEATURE_NUM=$(printf "%03d" "$BRANCH_NUMBER")
FOLDER_NAME="${FEATURE_NUM}-${BRANCH_SUFFIX}"
BRANCH_NAME="feature/SPEC-${SPEC_TIMESTAMP}/${FOLDER_NAME}"

# GitHub enforces a 244-byte limit on branch names
# Validate and truncate if necessary
MAX_BRANCH_LENGTH=244
if [ ${#BRANCH_NAME} -gt $MAX_BRANCH_LENGTH ]; then
    # Calculate how much we need to trim from suffix
    # Account for: "feature/SPEC-" (13) + timestamp (12) + "/" (1) + number (3) + hyphen (1) = 30 chars
    MAX_SUFFIX_LENGTH=$((MAX_BRANCH_LENGTH - 30))

    # Truncate suffix at word boundary if possible
    TRUNCATED_SUFFIX=$(echo "$BRANCH_SUFFIX" | cut -c1-$MAX_SUFFIX_LENGTH)
    # Remove trailing hyphen if truncation created one
    TRUNCATED_SUFFIX=$(echo "$TRUNCATED_SUFFIX" | sed 's/-$//')

    ORIGINAL_BRANCH_NAME="$BRANCH_NAME"
    FOLDER_NAME="${FEATURE_NUM}-${TRUNCATED_SUFFIX}"
    BRANCH_NAME="feature/SPEC-${SPEC_TIMESTAMP}/${FOLDER_NAME}"

    >&2 echo "[specify] Warning: Branch name exceeded GitHub's 244-byte limit"
    >&2 echo "[specify] Original: $ORIGINAL_BRANCH_NAME (${#ORIGINAL_BRANCH_NAME} bytes)"
    >&2 echo "[specify] Truncated to: $BRANCH_NAME (${#BRANCH_NAME} bytes)"
fi

if [ "$HAS_GIT" = true ]; then
    git checkout -b "$BRANCH_NAME"
else
    >&2 echo "[specify] Warning: Git repository not detected; skipped branch creation for $BRANCH_NAME"
fi

FEATURE_DIR="$SPECS_DIR/$FOLDER_NAME"
mkdir -p "$FEATURE_DIR"

TEMPLATE="$REPO_ROOT/.specify/templates/spec-template.md"
SPEC_FILE="$FEATURE_DIR/spec.md"
if [ -f "$TEMPLATE" ]; then cp -f "$TEMPLATE" "$SPEC_FILE"; else touch "$SPEC_FILE"; fi

# Set the SPECIFY_FEATURE environment variable for the current session
export SPECIFY_FEATURE="$BRANCH_NAME"

if $JSON_MODE; then
    # Escape special characters for JSON output
    BRANCH_NAME_JSON=$(printf '%s\n' "$BRANCH_NAME" | sed 's/\\/\\\\/g; s/"/\\"/g')
    SPEC_FILE_JSON=$(printf '%s\n' "$SPEC_FILE" | sed 's/\\/\\\\/g; s/"/\\"/g')
    FEATURE_NUM_JSON=$(printf '%s\n' "$FEATURE_NUM" | sed 's/\\/\\\\/g; s/"/\\"/g')
    printf '{"BRANCH_NAME":"%s","SPEC_FILE":"%s","FEATURE_NUM":"%s"}\n' "$BRANCH_NAME_JSON" "$SPEC_FILE_JSON" "$FEATURE_NUM_JSON"
else
    echo "BRANCH_NAME: $BRANCH_NAME"
    echo "SPEC_FILE: $SPEC_FILE"
    echo "FEATURE_NUM: $FEATURE_NUM"
    echo "SPECIFY_FEATURE environment variable set to: $BRANCH_NAME"
fi