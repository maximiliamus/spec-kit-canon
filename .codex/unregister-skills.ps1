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

$targetRoot = Join-Path $CodexHome "skills"
$skills = Get-RepoSkills -RepoRoot $repoRoot

if ($skills.Count -eq 0) {
    Write-Output "No repo-local skills found under $(Join-Path $repoRoot 'skills')"
    exit 0
}

if (-not $Force) {
    foreach ($skill in $skills) {
        $sourcePath = $skill.FullName
        $targetPath = Join-Path $targetRoot $skill.Name

        if (-not (Test-Path -LiteralPath $targetPath)) {
            continue
        }

        $item = Get-Item -LiteralPath $targetPath -Force
        $isReparse = ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)
        $target = Get-ItemTargetPath -Item $item

        if (-not ($isReparse -and $target -eq $sourcePath)) {
            throw "Refusing to remove $targetPath because it is not the expected repo-linked skill entry. Re-run with -Force to override."
        }
    }
}

foreach ($skill in $skills) {
    $sourcePath = $skill.FullName
    $targetPath = Join-Path $targetRoot $skill.Name

    if (-not (Test-Path -LiteralPath $targetPath)) {
        Write-Output "Codex skill is not registered: $targetPath"
        continue
    }

    $item = Get-Item -LiteralPath $targetPath -Force
    $isReparse = ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)
    $target = Get-ItemTargetPath -Item $item

    if ($isReparse -and $target -eq $sourcePath) {
        Remove-Item -LiteralPath $targetPath -Force
        Write-Output "Unregistered Codex skill: $targetPath"
        continue
    }

    Remove-Item -LiteralPath $targetPath -Recurse -Force
    Write-Output "Removed Codex skill entry with -Force: $targetPath"
}
