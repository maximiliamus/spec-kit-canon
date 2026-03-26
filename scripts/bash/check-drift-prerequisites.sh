#!/usr/bin/env bash

# Unified prerequisite checking for the drift workflow.
#
# Provides REPO_ROOT, BRANCH, FEATURE_DIR, FEATURE_SPEC, TASKS, TASKS_DRIFT,
# SPEC_DRIFT, and CANONIZATION always.
# Optionally validates drift-specific artifacts and includes canon paths.
#
# Usage: ./check-drift-prerequisites.sh [OPTIONS]
#
# OPTIONS:
#   --json                  Output in JSON format
#   --require-tasks         Require tasks.md to exist
#   --require-tasks-drift   Require tasks.drift.md to exist
#   --require-spec-drift    Require spec.drift.md to exist
#   --require-canonization  Require canonization.md to exist
#   --canon                 Include CANON_ROOT and CANON_TOC in output
#   --help, -h              Show help message

set -e

# Parse command line arguments
JSON_MODE=false
REQUIRE_TASKS=false
REQUIRE_TASKS_DRIFT=false
REQUIRE_SPEC_DRIFT=false
REQUIRE_CANONIZATION=false
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
        --require-canonization)
            REQUIRE_CANONIZATION=true
            ;;
        --canon)
            INCLUDE_CANON=true
            ;;
        --help|-h)
            cat << 'EOF'
Usage: check-drift-prerequisites.sh [OPTIONS]

Unified prerequisite checking for the drift workflow.

Always outputs: REPO_ROOT, BRANCH, FEATURE_DIR, FEATURE_SPEC, TASKS,
                TASKS_DRIFT, SPEC_DRIFT, CANONIZATION
With --canon:   Also outputs CANON_ROOT, CANON_TOC

OPTIONS:
  --json                  Output in JSON format
  --require-tasks         Require tasks.md to exist
  --require-tasks-drift   Require tasks.drift.md to exist
  --require-spec-drift    Require spec.drift.md to exist
  --require-canonization  Require canonization.md to exist
  --canon                 Include canon paths in output
  --help, -h              Show this help message

EXAMPLES:
  # drift.reverse: needs tasks.md
  ./check-drift-prerequisites.sh --json --require-tasks

  # drift.detect: needs tasks.drift.md
  ./check-drift-prerequisites.sh --json --require-tasks-drift

  # drift.resolve: needs spec.drift.md
  ./check-drift-prerequisites.sh --json --require-spec-drift

  # drift.reconcile: needs spec.drift.md + canon paths
  ./check-drift-prerequisites.sh --json --require-spec-drift --canon

  # drift.canonize: needs canonization.md + canon paths
  ./check-drift-prerequisites.sh --json --require-canonization --canon

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

resolve_canon_root_rel() {
    local default_root="specs/000-canon"
    local extension_dir=""
    local config_file=""
    local extension_file=""
    local python_cmd=""
    local canon_root=""

    extension_dir="$(CDPATH="" cd "$SCRIPT_DIR/../.." 2>/dev/null && pwd)" || {
        echo "$default_root"
        return
    }

    config_file="$extension_dir/canon-config.yml"
    extension_file="$extension_dir/extension.yml"

    if command -v python3 >/dev/null 2>&1; then
        python_cmd="python3"
    elif command -v python >/dev/null 2>&1; then
        python_cmd="python"
    else
        echo "$default_root"
        return
    fi

    if canon_root=$(SPECKIT_CANON_CONFIG="$config_file" SPECKIT_CANON_EXTENSION="$extension_file" "$python_cmd" - <<'PY' 2>/dev/null
import os
import sys

try:
    import yaml
except Exception:
    sys.exit(1)

DEFAULT_ROOT = "specs/000-canon"


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

if not isinstance(root, str):
    root = DEFAULT_ROOT

root = root.strip().replace("\\", "/").rstrip("/")
print(root or DEFAULT_ROOT)
PY
    ); then
        canon_root="${canon_root//$'\r'/}"
        canon_root="${canon_root//\\//}"
        canon_root="${canon_root%/}"
        if [[ -n "$canon_root" ]]; then
            echo "$canon_root"
            return
        fi
    fi

    echo "$default_root"
}

# Get paths and validate branch
eval $(get_feature_paths)
check_feature_branch "$CURRENT_BRANCH" "$HAS_GIT" || exit 1

# Derive drift-specific paths
TASKS_DRIFT="$FEATURE_DIR/tasks.drift.md"
SPEC_DRIFT="$FEATURE_DIR/spec.drift.md"
CANONIZATION="$FEATURE_DIR/canonization.md"
CANON_ROOT_REL="$(resolve_canon_root_rel)"
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
    echo "Run /speckit.drift.reverse first to reverse-engineer task drift." >&2
    exit 1
fi

if $REQUIRE_SPEC_DRIFT && [[ ! -f "$SPEC_DRIFT" ]]; then
    echo "ERROR: spec.drift.md not found in $FEATURE_DIR" >&2
    echo "Run /speckit.drift.detect first to discover spec-level drift." >&2
    exit 1
fi

if $REQUIRE_CANONIZATION && [[ ! -f "$CANONIZATION" ]]; then
    echo "ERROR: canonization.md not found in $FEATURE_DIR" >&2
    echo "Run /speckit.drift.reconcile first to infer canon gaps." >&2
    exit 1
fi

# Output results
if $JSON_MODE; then
    json_output=$(printf '{"REPO_ROOT":"%s","BRANCH":"%s","FEATURE_DIR":"%s","FEATURE_SPEC":"%s","TASKS":"%s","TASKS_DRIFT":"%s","SPEC_DRIFT":"%s","CANONIZATION":"%s"' \
        "$REPO_ROOT" "$CURRENT_BRANCH" "$FEATURE_DIR" "$FEATURE_SPEC" "$TASKS" "$TASKS_DRIFT" "$SPEC_DRIFT" "$CANONIZATION")

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
    echo "SPEC_DRIFT: $SPEC_DRIFT"
    echo "CANONIZATION: $CANONIZATION"
    if $INCLUDE_CANON; then
        echo "CANON_ROOT: $CANON_ROOT"
        echo "CANON_TOC: $CANON_TOC"
    fi
fi
