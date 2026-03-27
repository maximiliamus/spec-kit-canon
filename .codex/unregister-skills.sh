#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
skills_source_dir="$repo_root/skills"
codex_home="${CODEX_HOME:-$HOME/.codex}"
target_root="$codex_home/skills"

shopt -s nullglob
source_paths=("$skills_source_dir"/*)
shopt -u nullglob

if [[ ${#source_paths[@]} -eq 0 ]]; then
  echo "No repo-local skills found under $skills_source_dir"
  exit 0
fi

for source_path in "${source_paths[@]}"; do
  [[ -d "$source_path" ]] || continue

  skill_name="$(basename "$source_path")"
  target_path="$target_root/$skill_name"

  if [[ -L "$target_path" ]] && [[ "$(readlink "$target_path")" == "$source_path" ]]; then
    rm "$target_path"
    echo "Unregistered Codex skill: $target_path"
    continue
  fi

  if [[ -e "$target_path" ]]; then
    echo "Refusing to remove $target_path because it is not the expected repo-linked skill entry." >&2
    exit 1
  fi

  echo "Codex skill is not registered: $target_path"
done
