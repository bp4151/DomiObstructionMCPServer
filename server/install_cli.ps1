# Installation script for DOMI Obstruction CLI (Windows PowerShell)
# Run with: powershell -ExecutionPolicy Bypass -File install_cli.ps1

Write-Host "DOMI Obstruction CLI Installer (Windows)" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
$pythonCmd = $null
$pipCmd = $null

# Try to find Python
$pythonCommands = @("python", "python3", "py")
foreach ($cmd in $pythonCommands) {
    try {
        $version = & $cmd --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $cmd
            Write-Host "Python found: $version" -ForegroundColor Green
            break
        }
    } catch {
        continue
    }
}

if ($null -eq $pythonCmd) {
    Write-Host "Error: Python 3 is required but not installed." -ForegroundColor Red
    Write-Host "   Please install Python 3.8 or higher from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "   Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    exit 1
}

# Determine pip command
$pipCommands = @("pip", "pip3", "$pythonCmd -m pip")
foreach ($cmd in $pipCommands) {
    try {
        $cmdParts = $cmd -split ' '
        if ($cmdParts.Length -gt 1) {
            $version = & $cmdParts[0] $cmdParts[1..($cmdParts.Length-1)] --version 2>$null
        } else {
            $version = & $cmd --version 2>$null
        }
        if ($LASTEXITCODE -eq 0) {
            $pipCmd = $cmd
            break
        }
    } catch {
        continue
    }
}

if ($null -eq $pipCmd) {
    Write-Host "Warning: pip not found, using: $pythonCmd -m pip" -ForegroundColor Yellow
    $pipCmd = "$pythonCmd -m pip"
}

Write-Host ""

# Check if UV is available (recommended)
$useUv = $false
try {
    $uvVersion = uv --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "UV found: $uvVersion" -ForegroundColor Green
        $useUv = $true
    }
} catch {
    Write-Host "UV not found - will use pip instead" -ForegroundColor Cyan
    Write-Host "   (Install UV for faster dependency management: https://github.com/astral-sh/uv)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
Write-Host ""

# Install dependencies
$dependencies = @("fastmcp", "cyclopts", "rich", "mcp")

if ($useUv) {
    Write-Host "Using UV to install dependencies..." -ForegroundColor Cyan
    foreach ($dep in $dependencies) {
        Write-Host "  Installing $dep..." -ForegroundColor Gray
        uv pip install $dep
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to install $dep" -ForegroundColor Red
            exit 1
        }
    }
} else {
    Write-Host "Using pip to install dependencies..." -ForegroundColor Cyan
    $pipParts = $pipCmd -split ' '
    foreach ($dep in $dependencies) {
        Write-Host "  Installing $dep..." -ForegroundColor Gray
        if ($pipParts.Length -gt 1) {
            & $pipParts[0] $pipParts[1..($pipParts.Length-1)] install $dep
        } else {
            & $pipCmd install $dep
        }
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to install $dep" -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Quick start:" -ForegroundColor Cyan
Write-Host "  $pythonCmd cli.py list-tools" -ForegroundColor White
Write-Host "  $pythonCmd cli.py call-tool obstruction_count" -ForegroundColor White
Write-Host "  $pythonCmd cli.py call-tool search_obstructions --q `"Fifth Avenue`"" -ForegroundColor White
Write-Host "  $pythonCmd cli.py call-tool list_active_entries" -ForegroundColor White
Write-Host ""
Write-Host "For more examples, see CLI_README.md or CLI_USAGE.md" -ForegroundColor Gray
Write-Host ""
Write-Host "Test the installation:" -ForegroundColor Cyan
Write-Host "  powershell -ExecutionPolicy Bypass -File test_cli.ps1" -ForegroundColor White
