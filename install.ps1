param(
    [ValidateSet('codex', 'claude', 'both')][string]$Target = 'both',
    [string]$SkillsDir,
    [string]$Python,
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
$installArgs = @((Join-Path $PSScriptRoot 'install.py'), '--target', $Target)
if ($SkillsDir) { $installArgs += @('--skills-dir', $SkillsDir) }
if ($DryRun) { $installArgs += '--dry-run' }
if ($Python) { & $Python @installArgs }
else {
    $foundPython = $false
    foreach ($candidate in @('python', 'python3', 'py')) {
        if (-not (Get-Command $candidate -ErrorAction SilentlyContinue)) { continue }
        $probeArgs = @('--version')
        if ($candidate -eq 'py') { $probeArgs = @('-3', '--version') }
        & $candidate @probeArgs 2>$null | Out-Null
        if ($LASTEXITCODE -ne 0) { continue }
        $foundPython = $true
        if ($candidate -eq 'py') { & $candidate -3 @installArgs }
        else { & $candidate @installArgs }
        break
    }
    if (-not $foundPython) { throw 'Python 3.8+ is required. Use -Python PATH to select an installed Python executable.' }
}
if ($LASTEXITCODE -ne 0) { throw "Installation failed (exit $LASTEXITCODE)." }
