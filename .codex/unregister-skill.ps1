[CmdletBinding()]
param(
    [string]$CodexHome = $env:CODEX_HOME,
    [switch]$Force
)

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$sourcePath = (Resolve-Path (Join-Path $repoRoot "skills\\testing-spec-kit-canon-extension")).Path

if ([string]::IsNullOrWhiteSpace($CodexHome)) {
    $CodexHome = Join-Path $HOME ".codex"
}

$targetPath = Join-Path (Join-Path $CodexHome "skills") "testing-spec-kit-canon-extension"

if (Test-Path $targetPath) {
    $item = Get-Item -LiteralPath $targetPath -Force
    $isReparse = ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)

    if ($isReparse -and $item.Target -eq $sourcePath) {
        Remove-Item -LiteralPath $targetPath -Force
        Write-Output "Unregistered Codex skill: $targetPath"
        exit 0
    }
    elseif ($Force) {
        Remove-Item -LiteralPath $targetPath -Recurse -Force
        Write-Output "Removed Codex skill entry with -Force: $targetPath"
        exit 0
    }
    else {
        throw "Refusing to remove $targetPath because it is not the expected repo-linked skill entry. Re-run with -Force to override."
    }
}

Write-Output "Codex skill is not registered: $targetPath"
