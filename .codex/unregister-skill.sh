#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_path="$repo_root/skills/testing-spec-kit-canon-extension"
codex_home="${CODEX_HOME:-$HOME/.codex}"
target_path="$codex_home/skills/testing-spec-kit-canon-extension"

if [[ -L "$target_path" ]] && [[ "$(readlink "$target_path")" == "$source_path" ]]; then
  rm "$target_path"
  echo "Unregistered Codex skill: $target_path"
  exit 0
fi

if [[ -e "$target_path" ]]; then
  echo "Refusing to remove $target_path because it is not the expected repo-linked skill entry." >&2
  exit 1
fi

echo "Codex skill is not registered: $target_path"
