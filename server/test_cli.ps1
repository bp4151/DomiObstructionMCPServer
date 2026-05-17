# Test script for DOMI Obstruction CLI (Windows PowerShell)
# Run with: powershell -ExecutionPolicy Bypass -File test_cli.ps1

Write-Host "Testing DOMI Obstruction CLI (Windows)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Find Python command
$pythonCmd = $null
$pythonCommands = @("python", "python3", "py")
foreach ($cmd in $pythonCommands) {
    try {
        $version = & $cmd --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $cmd
            break
        }
    } catch {
        continue
    }
}

if ($null -eq $pythonCmd) {
    Write-Host "Python 3 not found" -ForegroundColor Red
    exit 1
}

$version = & $pythonCmd --version
Write-Host "Python found: $version" -ForegroundColor Green
Write-Host ""

# Test 1: List tools
Write-Host "Test 1: List tools..." -ForegroundColor Yellow
try {
    & $pythonCmd cli.py list-tools > $null 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "list-tools works" -ForegroundColor Green
    } else {
        Write-Host "list-tools failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "list-tools failed: $_" -ForegroundColor Red
    exit 1
}

# Test 2: Get count
Write-Host "Test 2: Get obstruction count..." -ForegroundColor Yellow
try {
    $output = & $pythonCmd cli.py call-tool obstruction_count 2>&1 | Out-String
    if ($output -match '"total"') {
        if ($output -match '"total":\s*(\d+)') {
            $count = $matches[1]
            Write-Host "obstruction_count works (found $count records)" -ForegroundColor Green
        } else {
            Write-Host "obstruction_count works" -ForegroundColor Green
        }
    } else {
        Write-Host "obstruction_count failed" -ForegroundColor Red
        Write-Host $output -ForegroundColor Gray
        exit 1
    }
} catch {
    Write-Host "obstruction_count failed: $_" -ForegroundColor Red
    exit 1
}

# Test 3: List active entries
Write-Host "Test 3: List active entries..." -ForegroundColor Yellow
try {
    $output = & $pythonCmd cli.py call-tool list_active_entries --limit 10 2>&1 | Out-String
    if ($output -match 'success') {
        Write-Host "list_active_entries works" -ForegroundColor Green
    } else {
        Write-Host "list_active_entries failed" -ForegroundColor Red
        Write-Host $output -ForegroundColor Gray
        exit 1
    }
} catch {
    Write-Host "list_active_entries failed: $_" -ForegroundColor Red
    exit 1
}

# Test 4: Search
Write-Host "Test 4: Search obstructions..." -ForegroundColor Yellow
try {
    $output = & $pythonCmd cli.py call-tool search_obstructions --q "Avenue" --limit 5 2>&1 | Out-String
    if ($output -match 'records') {
        Write-Host "search_obstructions works" -ForegroundColor Green
    } else {
        Write-Host "search_obstructions failed" -ForegroundColor Red
        Write-Host $output -ForegroundColor Gray
        exit 1
    }
} catch {
    Write-Host "search_obstructions failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "All tests passed!" -ForegroundColor Green
Write-Host ""
Write-Host "Quick start:" -ForegroundColor Cyan
Write-Host "  $pythonCmd cli.py list-tools" -ForegroundColor White
Write-Host "  $pythonCmd cli.py call-tool search_obstructions --q `"Fifth Avenue`"" -ForegroundColor White
Write-Host "  $pythonCmd cli.py call-tool list_active_entries" -ForegroundColor White
Write-Host ""
Write-Host "For more examples, see:" -ForegroundColor Cyan
Write-Host "  - CLI_README.md (quick start)" -ForegroundColor Gray
Write-Host "  - CLI_USAGE.md (comprehensive guide)" -ForegroundColor Gray
Write-Host "  - ..\QUICK_REFERENCE.md (cheat sheet)" -ForegroundColor Gray
