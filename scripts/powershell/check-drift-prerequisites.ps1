#!/usr/bin/env pwsh

# Unified prerequisite checking for the drift workflow.
#
# Provides REPO_ROOT, BRANCH, FEATURE_DIR, FEATURE_SPEC, TASKS, TASKS_DRIFT,
# SPEC_DRIFT, and CANONIZATION always.
# Optionally validates drift-specific artifacts and includes canon paths.
#
# Usage: ./check-drift-prerequisites.ps1 [OPTIONS]
#
# OPTIONS:
#   -Json                 Output in JSON format
#   -RequireTasks         Require tasks.md to exist
#   -RequireTasksDrift    Require tasks.drift.md to exist
#   -RequireSpecDrift     Require spec.drift.md to exist
#   -RequireCanonization  Require canonization.md to exist
#   -Canon                Include CANON_ROOT and CANON_TOC in output
#   -Help, -h             Show help message

[CmdletBinding()]
param(
    [switch]$Json,
    [switch]$RequireTasks,
    [switch]$RequireTasksDrift,
    [switch]$RequireSpecDrift,
    [switch]$RequireCanonization,
    [switch]$Canon,
    [Alias('h')]
    [switch]$Help
)

$ErrorActionPreference = 'Stop'

function Write-FailAndExit {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Lines
    )

    foreach ($line in $Lines) {
        [Console]::Error.WriteLine($line)
    }

    exit 1
}

if ($Help) {
    Write-Output @"
Usage: check-drift-prerequisites.ps1 [OPTIONS]

Unified prerequisite checking for the drift workflow.

Always outputs: REPO_ROOT, BRANCH, FEATURE_DIR, FEATURE_SPEC, TASKS,
                TASKS_DRIFT, SPEC_DRIFT, CANONIZATION
With -Canon:    Also outputs CANON_ROOT, CANON_TOC

OPTIONS:
  -Json                 Output in JSON format
  -RequireTasks         Require tasks.md to exist
  -RequireTasksDrift    Require tasks.drift.md to exist
  -RequireSpecDrift     Require spec.drift.md to exist
  -RequireCanonization  Require canonization.md to exist
  -Canon                Include canon paths in output
  -Help, -h             Show this help message

EXAMPLES:
  # drift.reverse: needs tasks.md
  ./check-drift-prerequisites.ps1 -Json -RequireTasks

  # drift.detect: needs tasks.drift.md
  ./check-drift-prerequisites.ps1 -Json -RequireTasksDrift

  # drift.resolve: needs spec.drift.md
  ./check-drift-prerequisites.ps1 -Json -RequireSpecDrift

  # drift.reconcile: needs spec.drift.md + canon paths
  ./check-drift-prerequisites.ps1 -Json -RequireSpecDrift -Canon

  # drift.canonize: needs canonization.md + canon paths
  ./check-drift-prerequisites.ps1 -Json -RequireCanonization -Canon

"@
    exit 0
}

. "$PSScriptRoot/common.ps1"

function Get-CanonRootRelativePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ExtensionDir
    )

    $defaultRoot = 'specs/000-canon'
    $configFile = Join-Path $ExtensionDir 'canon-config.yml'
    $extensionFile = Join-Path $ExtensionDir 'extension.yml'
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue

    if (-not $pythonCmd) {
        $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
    }

    if (-not $pythonCmd) {
        return $defaultRoot
    }

    $script = @'
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
'@

    $env:SPECKIT_CANON_CONFIG = $configFile
    $env:SPECKIT_CANON_EXTENSION = $extensionFile

    try {
        $root = & $pythonCmd.Source -c $script 2>$null
        if ($LASTEXITCODE -eq 0 -and $root) {
            return $root.Trim().TrimEnd('/', '\')
        }
    } finally {
        Remove-Item Env:SPECKIT_CANON_CONFIG -ErrorAction SilentlyContinue
        Remove-Item Env:SPECKIT_CANON_EXTENSION -ErrorAction SilentlyContinue
    }

    return $defaultRoot
}

$paths = Get-FeaturePathsEnv
if (-not (Test-FeatureBranch -Branch $paths.CURRENT_BRANCH -HasGit:$paths.HAS_GIT)) {
    exit 1
}

$extensionDir = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$canonRootRelative = Get-CanonRootRelativePath -ExtensionDir $extensionDir
$tasksDrift = Join-Path $paths.FEATURE_DIR 'tasks.drift.md'
$specDrift = Join-Path $paths.FEATURE_DIR 'spec.drift.md'
$canonization = Join-Path $paths.FEATURE_DIR 'canonization.md'
$canonRoot = if ([System.IO.Path]::IsPathRooted($canonRootRelative)) {
    $canonRootRelative
} else {
    Join-Path $paths.REPO_ROOT $canonRootRelative
}
$canonToc = Join-Path $canonRoot '_toc.md'

if (-not (Test-Path -LiteralPath $paths.FEATURE_DIR -PathType Container)) {
    Write-FailAndExit @(
        "ERROR: Feature directory not found: $($paths.FEATURE_DIR)",
        'Run /speckit.specify first to create the feature structure.'
    )
}

if ($RequireTasks -and -not (Test-Path -LiteralPath $paths.TASKS -PathType Leaf)) {
    Write-FailAndExit @(
        "ERROR: tasks.md not found in $($paths.FEATURE_DIR)",
        'This command requires an original tasks.md to compare against.'
    )
}

if ($RequireTasksDrift -and -not (Test-Path -LiteralPath $tasksDrift -PathType Leaf)) {
    Write-FailAndExit @(
        "ERROR: tasks.drift.md not found in $($paths.FEATURE_DIR)",
        'Run /speckit.canon.drift-reverse first to reverse-engineer task drift.'
    )
}

if ($RequireSpecDrift -and -not (Test-Path -LiteralPath $specDrift -PathType Leaf)) {
    Write-FailAndExit @(
        "ERROR: spec.drift.md not found in $($paths.FEATURE_DIR)",
        'Run /speckit.canon.drift-detect first to discover spec-level drift.'
    )
}

if ($RequireCanonization -and -not (Test-Path -LiteralPath $canonization -PathType Leaf)) {
    Write-FailAndExit @(
        "ERROR: canonization.md not found in $($paths.FEATURE_DIR)",
        'Run /speckit.canon.drift-reconcile first to infer canon gaps.'
    )
}

if ($Json) {
    $output = [ordered]@{
        REPO_ROOT = $paths.REPO_ROOT
        BRANCH = $paths.CURRENT_BRANCH
        FEATURE_DIR = $paths.FEATURE_DIR
        FEATURE_SPEC = $paths.FEATURE_SPEC
        TASKS = $paths.TASKS
        TASKS_DRIFT = $tasksDrift
        SPEC_DRIFT = $specDrift
        CANONIZATION = $canonization
    }

    if ($Canon) {
        $output.CANON_ROOT = $canonRoot
        $output.CANON_TOC = $canonToc
    }

    [PSCustomObject]$output | ConvertTo-Json -Compress
    exit 0
}

Write-Output "REPO_ROOT: $($paths.REPO_ROOT)"
Write-Output "BRANCH: $($paths.CURRENT_BRANCH)"
Write-Output "FEATURE_DIR: $($paths.FEATURE_DIR)"
Write-Output "FEATURE_SPEC: $($paths.FEATURE_SPEC)"
Write-Output "TASKS: $($paths.TASKS)"
Write-Output "TASKS_DRIFT: $tasksDrift"
Write-Output "SPEC_DRIFT: $specDrift"
Write-Output "CANONIZATION: $canonization"
if ($Canon) {
    Write-Output "CANON_ROOT: $canonRoot"
    Write-Output "CANON_TOC: $canonToc"
}
