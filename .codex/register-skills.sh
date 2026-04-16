#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
skills_source_dir="$repo_root/skills"
codex_home="${CODEX_HOME:-$HOME/.codex}"
skills_dir="$codex_home/skills"

mkdir -p "$skills_dir"

echo "Unregistering existing Codex skills before re-registering..."
bash "$(dirname "${BASH_SOURCE[0]}")/unregister-skills.sh" || true

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
  target_path="$skills_dir/$skill_name"

  if [[ -L "$target_path" ]] && [[ "$(readlink "$target_path")" == "$source_path" ]]; then
    echo "Codex skill already registered: $target_path -> $source_path"
    continue
  fi

  if [[ -e "$target_path" ]]; then
    rm -rf "$target_path"
  fi

  ln -s "$source_path" "$target_path"
  echo "Registered Codex skill: $target_path -> $source_path"
done
