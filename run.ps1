# Prefer installed Python, then the runtime bundled with Codex on this machine.
$ErrorActionPreference = 'Stop'
$pythonCandidates = @(
    (Join-Path $PSScriptRoot '.venv\Scripts\python.exe'),
    'C:\Program Files\WindowsApps\OpenAI.CodexPrimaryRuntime.v26-1104-2876-0_26.1104.2876.0_x64__3k8sg7r9htsxt\dependencies\python\python.exe'
)
$pythonExecutable = $pythonCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $pythonExecutable) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCommand) { throw 'Install Python 3.10+ and add it to PATH.' }
    $pythonExecutable = $pythonCommand.Source
}
& $pythonExecutable (Join-Path $PSScriptRoot 'rag.py') @args
exit $LASTEXITCODE
