# DOMI Obstruction CLI - Windows Installation Guide

Quick guide for installing and using the CLI on Windows.

## Installation

### Option 1: Run the Installer (Recommended)

Open PowerShell in the `server` directory and run:

```powershell
powershell -ExecutionPolicy Bypass -File install_cli.ps1
```

This will:
1. Check for Python installation
2. Check for UV (optional but faster)
3. Install all required dependencies
4. Show you quick start commands

### Option 2: Manual Installation with pip

```powershell
# Install dependencies
pip install fastmcp cyclopts rich mcp

# Or using python -m pip
python -m pip install fastmcp cyclopts rich mcp
```

### Option 3: Using UV (Fastest)

If you have UV installed:

```powershell
uv pip install fastmcp cyclopts rich mcp
```

Or run without installation:

```powershell
uv run --with fastmcp python cli.py list-tools
```

## Testing the Installation

Run the test script:

```powershell
powershell -ExecutionPolicy Bypass -File test_cli.ps1
```

Expected output:
```
🧪 Testing DOMI Obstruction CLI (Windows)
==========================================

✅ Python found: Python 3.11.0
✅ list-tools works
✅ obstruction_count works (found 5234 records)
✅ list_active_entries works
✅ search_obstructions works

🎉 All tests passed!
```

## Quick Start

```powershell
# List available tools
python cli.py list-tools

# Get count of obstructions
python cli.py call-tool obstruction_count

# Search for obstructions on Fifth Avenue
python cli.py call-tool search_obstructions --q "Fifth Avenue"

# List active closures
python cli.py call-tool list_active_entries --limit 50
```

## Common Commands (Windows)

### Search by street name
```powershell
python cli.py call-tool search_obstructions --q "Fifth Avenue"
```

### Search with exact filter
```powershell
python cli.py call-tool search_obstructions --filters '{\"primary_street\": \"FIFTH AVE\"}'
```

### Get active closures only
```powershell
python cli.py call-tool list_active_entries --limit 50
```

### Combine search and filter
```powershell
python cli.py call-tool search_obstructions --q "construction" --filters '{\"active\": true}'
```

## Output to File (Windows)

```powershell
# Save results to JSON
python cli.py call-tool list_active_entries > closures.json

# Save with specific encoding
python cli.py call-tool list_active_entries | Out-File -Encoding UTF8 closures.json
```

## Using with PowerShell Pipeline

```powershell
# Get output as JSON
$result = python cli.py call-tool obstruction_count | ConvertFrom-Json

# Access properties
$result.total

# Filter results
$closures = python cli.py call-tool list_active_entries --limit 100 | ConvertFrom-Json
$closures.result.records | Where-Object { $_.primary_street -like "*FIFTH*" }
```

## Scheduling with Task Scheduler

Create a daily report using Windows Task Scheduler:

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., daily at 8 AM)
4. Action: Start a program
   - Program: `powershell.exe`
   - Arguments: `-ExecutionPolicy Bypass -File "C:\path\to\daily_report.ps1"`

Example `daily_report.ps1`:
```powershell
$date = Get-Date -Format "yyyy-MM-dd"
$output = python cli.py call-tool list_active_entries --limit 1000
$output | Out-File "reports\closures_$date.json" -Encoding UTF8

# Optional: Convert to CSV
$data = $output | ConvertFrom-Json
$data.result.records | Export-Csv "reports\closures_$date.csv" -NoTypeInformation
```

## Troubleshooting (Windows)

### "python is not recognized as an internal or external command"

1. Install Python from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Or use `py` command instead: `py cli.py list-tools`

### Execution Policy Error

If you see "cannot be loaded because running scripts is disabled":

```powershell
# Run scripts with bypass (recommended)
powershell -ExecutionPolicy Bypass -File install_cli.ps1

# Or change policy permanently (admin required)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Import Errors (ModuleNotFoundError)

```powershell
# Reinstall dependencies
python -m pip install --upgrade fastmcp cyclopts rich mcp

# Or use the installer
powershell -ExecutionPolicy Bypass -File install_cli.ps1
```

### Connection Errors

If you see "Could not connect to server":

1. Check internet connectivity
2. Verify server URL in `cli.py`:
   ```python
   CLIENT_SPEC = 'https://domi-obstruction.fly.dev/mcp'
   ```
3. Test with curl:
   ```powershell
   curl https://domi-obstruction.fly.dev/mcp
   ```

### JSON Parsing Errors with Filters

Use double quotes inside the JSON string:
```powershell
# Good
--filters '{\"primary_street\": \"FIFTH AVE\"}'

# Or use single quotes outside
--filters '{"primary_street": "FIFTH AVE"}'
```

## PowerShell-Specific Features

### Pretty Print JSON

```powershell
python cli.py call-tool list_active_entries | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### Filter and Sort

```powershell
$closures = python cli.py call-tool list_active_entries --limit 500 | ConvertFrom-Json
$closures.result.records | 
    Where-Object { $_.primary_street -like "*FIFTH*" } |
    Sort-Object start_date |
    Format-Table primary_street, work_description, start_date
```

### Export to Excel

```powershell
# Requires ImportExcel module: Install-Module -Name ImportExcel
$data = python cli.py call-tool list_active_entries --limit 1000 | ConvertFrom-Json
$data.result.records | Export-Excel -Path "closures.xlsx" -AutoSize -TableName "Closures"
```

### Create HTML Report

```powershell
$closures = python cli.py call-tool list_active_entries | ConvertFrom-Json
$html = $closures.result.records | 
    Select-Object primary_street, work_description, start_date, end_date |
    ConvertTo-Html -Title "Active Road Closures" -PreContent "<h1>Pittsburgh Road Closures</h1>"
$html | Out-File "report.html" -Encoding UTF8
```

## Using with Windows Subsystem for Linux (WSL)

If you have WSL installed, you can also use the bash scripts:

```powershell
# From Windows PowerShell, run in WSL
wsl bash install_cli.sh
wsl bash test_cli.sh
wsl python cli.py list-tools
```

## Configuration for Local Development

Edit `cli.py` to use local server:

```python
# For local server
CLIENT_SPEC = 'http://localhost:8000/mcp'

# For production
CLIENT_SPEC = 'https://domi-obstruction.fly.dev/mcp'
```

## Next Steps

- Read `CLI_USAGE.md` for comprehensive examples
- Check `..\QUICK_REFERENCE.md` for quick command reference
- See `..\DOCUMENTATION_INDEX.md` for all available documentation

## Help

```powershell
# Get help
python cli.py --help

# Get help for specific command
python cli.py call-tool --help
python cli.py call-tool search_obstructions --help
```
