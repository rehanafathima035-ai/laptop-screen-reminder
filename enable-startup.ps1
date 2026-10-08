$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path $PSScriptRoot 'pond-water-reminder.py'

# Prefer the active interpreter if it can import Pillow. If PowerShell is using
# a venv without Pillow, use the Python launcher to find the regular Python.
$python = (Get-Command python.exe -ErrorAction Stop).Source
& $python -c 'from PIL import Image' *> $null
if ($LASTEXITCODE -ne 0) {
    $pyLauncher = (Get-Command py.exe -ErrorAction Stop).Source
    $python = (& $pyLauncher -3 -c 'import sys; print(sys.executable)').Trim()
    if (-not $python) { throw 'Could not locate the regular Python installation.' }
    & $python -c 'from PIL import Image'
    if ($LASTEXITCODE -ne 0) { throw 'Pillow is not available in the selected Python installation.' }
}

$pythonw = Join-Path (Split-Path $python) 'pythonw.exe'
if (-not (Test-Path -LiteralPath $pythonw)) {
    throw "Could not find pythonw.exe beside $python"
}

$startup = [Environment]::GetFolderPath('Startup')
$shortcutPath = Join-Path $startup 'Pond Water Reminder.lnk'
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $pythonw
$shortcut.Arguments = ('"{0}"' -f $scriptPath)
$shortcut.WorkingDirectory = $PSScriptRoot
$shortcut.Description = 'Show Pond water reminders after sign-in'
$shortcut.Save()
Write-Host "Startup shortcut created: $shortcutPath"
