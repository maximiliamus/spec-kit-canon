[CmdletBinding()]
param(
    [string]$CodexHome = $env:CODEX_HOME,
    [switch]$Force
)

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$sourcePath = (Resolve-Path (Join-Path $repoRoot "skills\\test-speckit-canon-extension")).Path

if ([string]::IsNullOrWhiteSpace($CodexHome)) {
    $CodexHome = Join-Path $HOME ".codex"
}

$skillsDir = Join-Path $CodexHome "skills"
$targetPath = Join-Path $skillsDir "test-speckit-canon-extension"

New-Item -ItemType Directory -Path $skillsDir -Force | Out-Null

if (Test-Path $targetPath) {
    $item = Get-Item -LiteralPath $targetPath -Force
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -and $item.Target -eq $sourcePath) {
        Write-Output "Codex skill already registered: $targetPath -> $sourcePath"
        exit 0
    }

    if (-not $Force) {
        throw "Target already exists at $targetPath. Re-run with -Force to replace it."
    }

    Remove-Item -LiteralPath $targetPath -Recurse -Force
}

New-Item -ItemType Junction -Path $targetPath -Target $sourcePath | Out-Null
Write-Output "Registered Codex skill: $targetPath -> $sourcePath"
