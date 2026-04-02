#!/usr/bin/env bash

# Unified prerequisite checking for the drift workflow.
#
# Provides REPO_ROOT, BRANCH, FEATURE_DIR, FEATURE_SPEC, TASKS, TASKS_DRIFT,
# TASKS_ALIGNMENT, SPEC_DRIFT, and CANON_DRIFT always.
# Optionally validates drift-specific artifacts and includes canon paths.
#
# Usage: ./check-prerequisites.sh [OPTIONS]
#
# OPTIONS:
#   --json                  Output in JSON format
#   --require-tasks         Require tasks.md to exist
#   --require-tasks-drift   Require tasks.drift.md to exist
#   --require-spec-drift    Require spec.drift.md to exist
#   --require-tasks-alignment Require tasks.alignment.md to exist
#   --require-canon-drift   Require canon.drift.md to exist
#   --canon                 Include CANON_ROOT and CANON_TOC in output
#   --help, -h              Show help message

set -e

# Parse command line arguments
JSON_MODE=false
REQUIRE_TASKS=false
REQUIRE_TASKS_DRIFT=false
REQUIRE_SPEC_DRIFT=false
REQUIRE_TASKS_ALIGNMENT=false
REQUIRE_CANON_DRIFT=false
INCLUDE_CANON=false

for arg in "$@"; do
    case "$arg" in
        --json)
            JSON_MODE=true
            ;;
        --require-tasks)
            REQUIRE_TASKS=true
            ;;
        --require-tasks-drift)
            REQUIRE_TASKS_DRIFT=true
            ;;
        --require-spec-drift)
            REQUIRE_SPEC_DRIFT=true
            ;;
        --require-tasks-alignment)
            REQUIRE_TASKS_ALIGNMENT=true
            ;;
        --require-canon-drift)
            REQUIRE_CANON_DRIFT=true
            ;;
        --canon)
            INCLUDE_CANON=true
            ;;
        --help|-h)
            cat << 'EOF'
Usage: check-prerequisites.sh [OPTIONS]

Unified prerequisite checking for the drift workflow.

Always outputs: REPO_ROOT, BRANCH, FEATURE_DIR, FEATURE_SPEC, TASKS,
                TASKS_DRIFT, TASKS_ALIGNMENT, SPEC_DRIFT, CANON_DRIFT,
                BASE_BRANCH
With --canon:   Also outputs CANON_ROOT, CANON_TOC

OPTIONS:
  --json                  Output in JSON format
  --require-tasks         Require tasks.md to exist
  --require-tasks-drift   Require tasks.drift.md to exist
  --require-spec-drift    Require spec.drift.md to exist
  --require-tasks-alignment Require tasks.alignment.md to exist
  --require-canon-drift   Require canon.drift.md to exist
  --canon                 Include canon paths in output
  --help, -h              Show this help message

EXAMPLES:
  # drift.reverse: needs tasks.md
  ./check-prerequisites.sh --json --require-tasks

  # drift.detect: needs tasks.drift.md
  ./check-prerequisites.sh --json --require-tasks-drift

  # drift.resolve: needs spec.drift.md
  ./check-prerequisites.sh --json --require-spec-drift

  # drift.implement: needs spec.drift.md + tasks.alignment.md
  ./check-prerequisites.sh --json --require-spec-drift --require-tasks-alignment

  # drift.reconcile: needs spec.drift.md + canon paths
  ./check-prerequisites.sh --json --require-spec-drift --canon

  # drift.canonize: needs canon.drift.md + canon paths
  ./check-prerequisites.sh --json --require-canon-drift --canon

EOF
            exit 0
            ;;
        *)
            echo "ERROR: Unknown option '$arg'. Use --help for usage information." >&2
            exit 1
            ;;
    esac
done

# Source common functions
SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

resolve_canon_settings() {
    local default_root="specs/000-canon"
    local default_base_branch="main"
    local extension_dir=""
    local config_file=""
    local extension_file=""
    local python_cmd=""
    local canon_settings=""

    extension_dir="$(CDPATH="" cd "$SCRIPT_DIR/../.." 2>/dev/null && pwd)" || {
        printf '%s\n%s\n' "$default_root" "$default_base_branch"
        return
    }

    config_file="$extension_dir/canon-config.yml"
    extension_file="$extension_dir/extension.yml"

    if command -v python3 >/dev/null 2>&1; then
        python_cmd="python3"
    elif command -v python >/dev/null 2>&1; then
        python_cmd="python"
    else
        printf '%s\n%s\n' "$default_root" "$default_base_branch"
        return
    fi

    if canon_settings=$(SPECKIT_CANON_CONFIG="$config_file" SPECKIT_CANON_EXTENSION="$extension_file" "$python_cmd" - <<'PY' 2>/dev/null
import os
import sys

try:
    import yaml
except Exception:
    sys.exit(1)

DEFAULT_ROOT = "specs/000-canon"
DEFAULT_BASE_BRANCH = "main"


def load_yaml(path):
    if not path or not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data if isinstance(data, dict) else {}


config = load_yaml(os.environ.get("SPECKIT_CANON_CONFIG"))
extension = load_yaml(os.environ.get("SPECKIT_CANON_EXTENSION"))

root = (
    ((config.get("canon") or {}).get("root"))
    or ((((extension.get("config") or {}).get("defaults") or {}).get("canon") or {}).get("root"))
    or DEFAULT_ROOT
)

base_branch = (
    ((config.get("branching") or {}).get("base"))
    or ((((extension.get("config") or {}).get("defaults") or {}).get("branching") or {}).get("base"))
    or DEFAULT_BASE_BRANCH
)

if not isinstance(root, str):
    root = DEFAULT_ROOT

if not isinstance(base_branch, str):
    base_branch = DEFAULT_BASE_BRANCH

root = root.strip().replace("\\", "/").rstrip("/")
base_branch = base_branch.strip()

print(root or DEFAULT_ROOT)
print(base_branch or DEFAULT_BASE_BRANCH)
PY
    ); then
        local canon_root=""
        local base_branch=""
        mapfile -t canon_settings_lines <<< "$canon_settings"
        canon_root="${canon_settings_lines[0]//$'\r'/}"
        base_branch="${canon_settings_lines[1]//$'\r'/}"
        canon_root="${canon_root//$'\r'/}"
        canon_root="${canon_root//\\//}"
        canon_root="${canon_root%/}"
        if [[ -z "$canon_root" ]]; then
            canon_root="$default_root"
        fi
        if [[ -z "$base_branch" ]]; then
            base_branch="$default_base_branch"
        fi
        if [[ -n "$canon_root" && -n "$base_branch" ]]; then
            printf '%s\n%s\n' "$canon_root" "$base_branch"
            return
        fi
    fi

    printf '%s\n%s\n' "$default_root" "$default_base_branch"
}

# Get paths and validate branch
eval $(get_feature_paths)
check_feature_branch "$CURRENT_BRANCH" "$HAS_GIT" || exit 1

# Derive drift-specific paths
TASKS_DRIFT="$FEATURE_DIR/tasks.drift.md"
TASKS_ALIGNMENT="$FEATURE_DIR/tasks.alignment.md"
SPEC_DRIFT="$FEATURE_DIR/spec.drift.md"
CANON_DRIFT="$FEATURE_DIR/canon.drift.md"
mapfile -t CANON_SETTINGS < <(resolve_canon_settings)
CANON_ROOT_REL="${CANON_SETTINGS[0]:-specs/000-canon}"
BASE_BRANCH="${CANON_SETTINGS[1]:-main}"
if [[ "$CANON_ROOT_REL" =~ ^[A-Za-z]:[\\/].* ]] || [[ "$CANON_ROOT_REL" == /* ]]; then
    CANON_ROOT="$CANON_ROOT_REL"
else
    CANON_ROOT="$REPO_ROOT/$CANON_ROOT_REL"
fi
CANON_ROOT="${CANON_ROOT%/}"
CANON_TOC="$CANON_ROOT/_toc.md"

# Validate feature directory exists
if [[ ! -d "$FEATURE_DIR" ]]; then
    echo "ERROR: Feature directory not found: $FEATURE_DIR" >&2
    echo "Run /speckit.specify first to create the feature structure." >&2
    exit 1
fi

# Validate required artifacts
if $REQUIRE_TASKS && [[ ! -f "$TASKS" ]]; then
    echo "ERROR: tasks.md not found in $FEATURE_DIR" >&2
    echo "This command requires an original tasks.md to compare against." >&2
    exit 1
fi

if $REQUIRE_TASKS_DRIFT && [[ ! -f "$TASKS_DRIFT" ]]; then
    echo "ERROR: tasks.drift.md not found in $FEATURE_DIR" >&2
    echo "Run /speckit.canon.drift-reverse first to reverse-engineer task drift." >&2
    exit 1
fi

if $REQUIRE_SPEC_DRIFT && [[ ! -f "$SPEC_DRIFT" ]]; then
    echo "ERROR: spec.drift.md not found in $FEATURE_DIR" >&2
    echo "Run /speckit.canon.drift-detect first to discover spec-level drift." >&2
    exit 1
fi

if $REQUIRE_TASKS_ALIGNMENT && [[ ! -f "$TASKS_ALIGNMENT" ]]; then
    echo "ERROR: tasks.alignment.md not found in $FEATURE_DIR" >&2
    echo "Run /speckit.canon.drift-resolve first and defer implementation work to create the alignment queue." >&2
    exit 1
fi

if $REQUIRE_CANON_DRIFT && [[ ! -f "$CANON_DRIFT" ]]; then
    echo "ERROR: canon.drift.md not found in $FEATURE_DIR" >&2
    echo "Run /speckit.canon.drift-reconcile first to infer canon gaps." >&2
    exit 1
fi

# Output results
if $JSON_MODE; then
    json_output=$(printf '{"REPO_ROOT":"%s","BRANCH":"%s","FEATURE_DIR":"%s","FEATURE_SPEC":"%s","TASKS":"%s","TASKS_DRIFT":"%s","TASKS_ALIGNMENT":"%s","SPEC_DRIFT":"%s","CANON_DRIFT":"%s","BASE_BRANCH":"%s"' \
        "$REPO_ROOT" "$CURRENT_BRANCH" "$FEATURE_DIR" "$FEATURE_SPEC" "$TASKS" "$TASKS_DRIFT" "$TASKS_ALIGNMENT" "$SPEC_DRIFT" "$CANON_DRIFT" "$BASE_BRANCH")

    if $INCLUDE_CANON; then
        json_output+=$(printf ',"CANON_ROOT":"%s","CANON_TOC":"%s"' "$CANON_ROOT" "$CANON_TOC")
    fi

    json_output+='}'
    echo "$json_output"
else
    echo "REPO_ROOT: $REPO_ROOT"
    echo "BRANCH: $CURRENT_BRANCH"
    echo "FEATURE_DIR: $FEATURE_DIR"
    echo "FEATURE_SPEC: $FEATURE_SPEC"
    echo "TASKS: $TASKS"
    echo "TASKS_DRIFT: $TASKS_DRIFT"
    echo "TASKS_ALIGNMENT: $TASKS_ALIGNMENT"
    echo "SPEC_DRIFT: $SPEC_DRIFT"
    echo "CANON_DRIFT: $CANON_DRIFT"
    echo "BASE_BRANCH: $BASE_BRANCH"
    if $INCLUDE_CANON; then
        echo "CANON_ROOT: $CANON_ROOT"
        echo "CANON_TOC: $CANON_TOC"
    fi
fi
