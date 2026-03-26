#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_path="$repo_root/skills/test-speckit-canon-extension"
codex_home="${CODEX_HOME:-$HOME/.codex}"
skills_dir="$codex_home/skills"
target_path="$skills_dir/test-speckit-canon-extension"

mkdir -p "$skills_dir"

if [[ -L "$target_path" ]] && [[ "$(readlink "$target_path")" == "$source_path" ]]; then
  echo "Codex skill already registered: $target_path -> $source_path"
  exit 0
fi

if [[ -e "$target_path" ]]; then
  rm -rf "$target_path"
fi

ln -s "$source_path" "$target_path"
echo "Registered Codex skill: $target_path -> $source_path"
