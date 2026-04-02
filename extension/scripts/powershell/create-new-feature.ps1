#!/usr/bin/env pwsh
# Create a new feature
[CmdletBinding()]
param(
    [switch]$Json,
    [string]$ShortName,
    [Parameter()]
    [int]$Number = 0,
    [switch]$Timestamp,
    [switch]$Help,
    [Parameter(Position = 0, ValueFromRemainingArguments = $true)]
    [string[]]$FeatureDescription
)
$ErrorActionPreference = 'Stop'

# Show help if requested
if ($Help) {
    Write-Output @"
Usage: ./create-new-feature.ps1 [-Json] [-ShortName <name>] [-Number N] [-Timestamp] <feature description>

Options:
  -Json               Output in JSON format
  -ShortName <name>   Provide a custom short name (2-4 words) for the branch
  -Number N           Specify branch number manually (overrides auto-detection)
  -Timestamp          Use timestamp prefix (YYYYMMDD-HHMMSS) instead of sequential numbering
  -Help               Show this help message

Examples:
  ./create-new-feature.ps1 'Add user authentication system' -ShortName 'user-auth'
  ./create-new-feature.ps1 'Implement OAuth2 integration for API'
  ./create-new-feature.ps1 -Timestamp -ShortName 'user-auth' 'Add user authentication'
"@
    exit 0
}

# Check if feature description provided
if (-not $FeatureDescription -or $FeatureDescription.Count -eq 0) {
    Write-Error "Usage: ./create-new-feature.ps1 [-Json] [-ShortName <name>] [-Number N] [-Timestamp] <feature description>"
    exit 1
}

$featureDesc = ($FeatureDescription -join ' ').Trim()

# Validate description is not empty after trimming (e.g., user passed only whitespace)
if ([string]::IsNullOrWhiteSpace($featureDesc)) {
    Write-Error "Error: Feature description cannot be empty or contain only whitespace"
    exit 1
}

function Get-HighestSpecNumber {
    param([string]$SpecsDir)

    $highest = 0
    if (Test-Path $SpecsDir) {
        Get-ChildItem -Path $SpecsDir -Directory | ForEach-Object {
            if ($_.Name -match '^(\d{3})-') {
                $num = [int]$matches[1]
                if ($num -gt $highest) { $highest = $num }
            }
        }
    }
    return $highest
}

function Get-HighestBranchNumber {
    param()

    $highest = 0
    try {
        $branches = git branch -a 2>$null
        if ($LASTEXITCODE -eq 0) {
            foreach ($branch in $branches) {
                # Clean branch name: remove leading markers and remote prefixes
                $cleanBranch = $branch.Trim() -replace '^\*?\s+', '' -replace '^remotes/[^/]+/', ''

                # Extract feature number if branch matches pattern ###-*
                if ($cleanBranch -match '^(\d{3})-') {
                    $num = [int]$matches[1]
                    if ($num -gt $highest) { $highest = $num }
                }
            }
        }
    } catch {
        # If git command fails, return 0
        Write-Verbose "Could not check Git branches: $_"
    }
    return $highest
}

function Get-NextBranchNumber {
    param(
        [string]$SpecsDir
    )

    # Fetch all remotes to get latest branch info (suppress errors if no remotes)
    try {
        git fetch --all --prune 2>$null | Out-Null
    } catch {
        Write-Verbose "Git fetch failed while calculating next branch number: $_"
    }

    # Get highest number from ALL branches (not just matching short name)
    $highestBranch = Get-HighestBranchNumber

    # Get highest number from ALL specs (not just matching short name)
    $highestSpec = Get-HighestSpecNumber -SpecsDir $SpecsDir

    # Take the maximum of both
    $maxNum = [Math]::Max($highestBranch, $highestSpec)

    # Return next number
    return $maxNum + 1
}

function ConvertTo-CleanBranchName {
    param([string]$Name)

    return $Name.ToLower() -replace '[^a-z0-9]', '-' -replace '-{2,}', '-' -replace '^-', '' -replace '-$', ''
}

function Get-ConfiguredBaseBranch {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ExtensionDir
    )

    $defaultBaseBranch = 'main'
    $configFile = Join-Path $ExtensionDir 'canon-config.yml'
    $extensionFile = Join-Path $ExtensionDir 'extension.yml'
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue

    if (-not $pythonCmd) {
        $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
    }

    if (-not $pythonCmd) {
        return $defaultBaseBranch
    }

    $script = @'
import os
import sys

try:
    import yaml
except Exception:
    sys.exit(1)

DEFAULT_BASE_BRANCH = "main"


def load_yaml(path):
    if not path or not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data if isinstance(data, dict) else {}


config = load_yaml(os.environ.get("SPECKIT_CANON_CONFIG"))
extension = load_yaml(os.environ.get("SPECKIT_CANON_EXTENSION"))

base_branch = (
    ((config.get("branching") or {}).get("base"))
    or ((((extension.get("config") or {}).get("defaults") or {}).get("branching") or {}).get("base"))
    or DEFAULT_BASE_BRANCH
)

if not isinstance(base_branch, str):
    base_branch = DEFAULT_BASE_BRANCH

base_branch = base_branch.strip()
print(base_branch or DEFAULT_BASE_BRANCH)
'@

    $env:SPECKIT_CANON_CONFIG = $configFile
    $env:SPECKIT_CANON_EXTENSION = $extensionFile

    try {
        $baseBranch = & $pythonCmd.Source -c $script 2>$null
        if ($LASTEXITCODE -eq 0 -and $baseBranch) {
            return $baseBranch.Trim()
        }
    } finally {
        Remove-Item Env:SPECKIT_CANON_CONFIG -ErrorAction SilentlyContinue
        Remove-Item Env:SPECKIT_CANON_EXTENSION -ErrorAction SilentlyContinue
    }

    return $defaultBaseBranch
}
# Load common functions (includes Get-RepoRoot, Test-HasGit, Resolve-Template)
. "$PSScriptRoot/common.ps1"

# Use common.ps1 functions which prioritize .specify over git
$repoRoot = Get-RepoRoot

# Check if git is available at this repo root (not a parent)
$hasGit = Test-HasGit

Set-Location $repoRoot

if ($hasGit) {
    $extensionDir = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
    $baseBranch = Get-ConfiguredBaseBranch -ExtensionDir $extensionDir
    $currentBranch = git -C $repoRoot rev-parse --abbrev-ref HEAD 2>$null

    if ($LASTEXITCODE -ne 0 -or -not $currentBranch) {
        Write-Error 'Error: Could not determine the current git branch before starting vibecoding.'
        exit 1
    }

    $currentBranch = $currentBranch.Trim()
    if ($currentBranch -ne $baseBranch) {
        Write-Error "Error: Vibecode sessions must be started from the configured base branch '$baseBranch'. Current branch: '$currentBranch'."
        exit 1
    }
}

$specsDir = Join-Path $repoRoot 'specs'
New-Item -ItemType Directory -Path $specsDir -Force | Out-Null

# Function to generate branch name with stop word filtering and length filtering
function Get-BranchName {
    param([string]$Description)

    # Common stop words to filter out
    $stopWords = @(
        'i', 'a', 'an', 'the', 'to', 'for', 'of', 'in', 'on', 'at', 'by', 'with', 'from',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must', 'shall',
        'this', 'that', 'these', 'those', 'my', 'your', 'our', 'their',
        'want', 'need', 'add', 'get', 'set'
    )

    # Convert to lowercase and extract words (alphanumeric only)
    $cleanName = $Description.ToLower() -replace '[^a-z0-9\s]', ' '
    $words = $cleanName -split '\s+' | Where-Object { $_ }

    # Filter words: remove stop words and words shorter than 3 chars (unless they're uppercase acronyms in original)
    $meaningfulWords = @()
    foreach ($word in $words) {
        # Skip stop words
        if ($stopWords -contains $word) { continue }

        # Keep words that are length >= 3 OR appear as uppercase in original (likely acronyms)
        if ($word.Length -ge 3) {
            $meaningfulWords += $word
        } elseif ($Description -match "\b$($word.ToUpper())\b") {
            # Keep short words if they appear as uppercase in original (likely acronyms)
            $meaningfulWords += $word
        }
    }

    # If we have meaningful words, use first 3-4 of them
    if ($meaningfulWords.Count -gt 0) {
        $maxWords = if ($meaningfulWords.Count -eq 4) { 4 } else { 3 }
        $result = ($meaningfulWords | Select-Object -First $maxWords) -join '-'
        return $result
    } else {
        # Fallback to original logic if no meaningful words found
        $result = ConvertTo-CleanBranchName -Name $Description
        $fallbackWords = ($result -split '-') | Where-Object { $_ } | Select-Object -First 3
        return [string]::Join('-', $fallbackWords)
    }
}

# Generate branch name
if ($ShortName) {
    # Use provided short name, just clean it up
    $branchSuffix = ConvertTo-CleanBranchName -Name $ShortName
} else {
    # Generate from description with smart filtering
    $branchSuffix = Get-BranchName -Description $featureDesc
}

# Warn if -Number and -Timestamp are both specified
if ($Timestamp -and $Number -ne 0) {
    Write-Warning "[specify] Warning: -Number is ignored when -Timestamp is used"
    $Number = 0
}

# Determine branch prefix
if ($Timestamp) {
    $featureNum = Get-Date -Format 'yyyyMMdd-HHmmss'
    $branchName = "$featureNum-$branchSuffix"
} else {
    # Determine branch number
    if ($Number -eq 0) {
        if ($hasGit) {
            # Check existing branches on remotes
            $Number = Get-NextBranchNumber -SpecsDir $specsDir
        } else {
            # Fall back to local directory check
            $Number = (Get-HighestSpecNumber -SpecsDir $specsDir) + 1
        }
    }

    $featureNum = ('{0:000}' -f $Number)
    $branchName = "$featureNum-$branchSuffix"
}

# GitHub enforces a 244-byte limit on branch names
# Validate and truncate if necessary
$maxBranchLength = 244
if ($branchName.Length -gt $maxBranchLength) {
    # Calculate how much we need to trim from suffix
    # Account for prefix length: timestamp (15) + hyphen (1) = 16, or sequential (3) + hyphen (1) = 4
    $prefixLength = $featureNum.Length + 1
    $maxSuffixLength = $maxBranchLength - $prefixLength

    # Truncate suffix
    $truncatedSuffix = $branchSuffix.Substring(0, [Math]::Min($branchSuffix.Length, $maxSuffixLength))
    # Remove trailing hyphen if truncation created one
    $truncatedSuffix = $truncatedSuffix -replace '-$', ''

    $originalBranchName = $branchName
    $branchName = "$featureNum-$truncatedSuffix"

    Write-Warning "[specify] Branch name exceeded GitHub's 244-byte limit"
    Write-Warning "[specify] Original: $originalBranchName ($($originalBranchName.Length) bytes)"
    Write-Warning "[specify] Truncated to: $branchName ($($branchName.Length) bytes)"
}

if ($hasGit) {
    $branchCreated = $false
    try {
        git checkout -q -b $branchName 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $branchCreated = $true
        }
    } catch {
        Write-Verbose "Git branch creation threw an exception for '$branchName': $_"
    }

    if (-not $branchCreated) {
        # Check if branch already exists
        $existingBranch = git branch --list $branchName 2>$null
        if ($existingBranch) {
            if ($Timestamp) {
                Write-Error "Error: Branch '$branchName' already exists. Rerun to get a new timestamp or use a different -ShortName."
            } else {
                Write-Error "Error: Branch '$branchName' already exists. Please use a different feature name or specify a different number with -Number."
            }
            exit 1
        } else {
            Write-Error "Error: Failed to create git branch '$branchName'. Please check your git configuration and try again."
            exit 1
        }
    }
} else {
    Write-Warning "[specify] Warning: Git repository not detected; skipped branch creation for $branchName"
}

$featureDir = Join-Path $specsDir $branchName
New-Item -ItemType Directory -Path $featureDir -Force | Out-Null

$template = Resolve-Template -TemplateName 'spec-template' -RepoRoot $repoRoot
$specFile = Join-Path $featureDir 'spec.md'
if ($template -and (Test-Path $template)) {
    Copy-Item $template $specFile -Force
} else {
    New-Item -ItemType File -Path $specFile | Out-Null
}

# Set the SPECIFY_FEATURE environment variable for the current session
$env:SPECIFY_FEATURE = $branchName

if ($Json) {
    $obj = [PSCustomObject]@{
        BRANCH_NAME = $branchName
        SPEC_FILE = $specFile
        FEATURE_NUM = $featureNum
        HAS_GIT = $hasGit
    }
    $obj | ConvertTo-Json -Compress
} else {
    Write-Output "BRANCH_NAME: $branchName"
    Write-Output "SPEC_FILE: $specFile"
    Write-Output "FEATURE_NUM: $featureNum"
    Write-Output "HAS_GIT: $hasGit"
    Write-Output "SPECIFY_FEATURE environment variable set to: $branchName"
}
