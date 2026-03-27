[CmdletBinding()]
param(
    [string]$CodexHome = $env:CODEX_HOME,
    [switch]$Force
)

function Get-RepoSkills {
    param([string]$RepoRoot)

    $skillsSourceDir = Join-Path $RepoRoot "skills"
    if (-not (Test-Path -LiteralPath $skillsSourceDir)) {
        return @()
    }

    return Get-ChildItem -LiteralPath $skillsSourceDir -Directory | Sort-Object Name
}

function Get-ItemTargetPath {
    param($Item)

    $target = $Item.Target
    if ($target -is [System.Array]) {
        return $target[0]
    }

    return $target
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if ([string]::IsNullOrWhiteSpace($CodexHome)) {
    $CodexHome = Join-Path $HOME ".codex"
}

$skillsDir = Join-Path $CodexHome "skills"
New-Item -ItemType Directory -Path $skillsDir -Force | Out-Null

$skills = Get-RepoSkills -RepoRoot $repoRoot
if ($skills.Count -eq 0) {
    Write-Output "No repo-local skills found under $(Join-Path $repoRoot 'skills')"
    exit 0
}

if (-not $Force) {
    foreach ($skill in $skills) {
        $sourcePath = $skill.FullName
        $targetPath = Join-Path $skillsDir $skill.Name

        if (-not (Test-Path -LiteralPath $targetPath)) {
            continue
        }

        $item = Get-Item -LiteralPath $targetPath -Force
        $isReparse = ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)
        $target = Get-ItemTargetPath -Item $item

        if (-not ($isReparse -and $target -eq $sourcePath)) {
            throw "Target already exists at $targetPath. Re-run with -Force to replace it."
        }
    }
}

foreach ($skill in $skills) {
    $sourcePath = $skill.FullName
    $targetPath = Join-Path $skillsDir $skill.Name

    if (Test-Path -LiteralPath $targetPath) {
        $item = Get-Item -LiteralPath $targetPath -Force
        $isReparse = ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)
        $target = Get-ItemTargetPath -Item $item

        if ($isReparse -and $target -eq $sourcePath) {
            Write-Output "Codex skill already registered: $targetPath -> $sourcePath"
            continue
        }

        Remove-Item -LiteralPath $targetPath -Recurse -Force
    }

    New-Item -ItemType Junction -Path $targetPath -Target $sourcePath | Out-Null
    Write-Output "Registered Codex skill: $targetPath -> $sourcePath"
}
