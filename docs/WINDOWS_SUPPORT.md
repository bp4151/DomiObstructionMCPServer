# Windows PowerShell Support Added ✅

## What Was Added

Your DOMI Obstruction CLI now has full Windows PowerShell support!

### New Files Created

1. **`../server/install_cli.ps1`** - PowerShell installer script
   - Auto-detects Python (python, python3, or py)
   - Checks for UV (optional faster installation)
   - Installs all dependencies (fastmcp, cyclopts, rich, mcp)
   - Provides helpful error messages and next steps

2. **`../server/test_cli.ps1`** - PowerShell test script
   - Runs all 4 test cases
   - Validates CLI functionality
   - Shows success/failure with color-coded output
   - Provides quick start commands after tests

3. **`../server/WINDOWS_INSTALL.md`** - Windows-specific guide
   - Installation instructions for Windows
   - PowerShell-specific commands and examples
   - Troubleshooting for Windows issues
   - PowerShell pipeline integration examples
   - Task Scheduler setup guide
   - Excel/HTML export examples

## How to Use on Windows

### Quick Start

Open PowerShell in the `server` directory:

```powershell
# Install
powershell -ExecutionPolicy Bypass -File install_cli.ps1

# Test
powershell -ExecutionPolicy Bypass -File test_cli.ps1

# Use
python cli.py list-tools
python cli.py call-tool search_obstructions --q "Fifth Avenue"
```

### Features Included

✅ **Auto Python Detection** - Works with python, python3, or py  
✅ **UV Support** - Uses UV if available for faster installation  
✅ **Colored Output** - Success/error messages in colors  
✅ **Error Handling** - Helpful error messages for common issues  
✅ **Test Suite** - Validates all functionality  
✅ **Documentation** - Complete Windows-specific guide  

## Documentation Updates

Updated to include Windows support:
- `SUMMARY.md` - Now shows Windows installation steps
- `QUICK_REFERENCE.md` - Includes PowerShell commands
- `DOCUMENTATION_INDEX.md` - Lists Windows files
- `../server/CLI_README.md` - Shows both Linux and Windows installation

## Platform Support

Your CLI now works on:
- ✅ Linux
- ✅ macOS  
- ✅ Windows Subsystem for Linux (WSL)
- ✅ Windows PowerShell
- ✅ Windows Command Prompt (via python cli.py)

## Example Windows Usage

### Basic Commands
```powershell
python cli.py call-tool obstruction_count
python cli.py call-tool list_active_entries
python cli.py call-tool search_obstructions --q "Forbes"
```

### PowerShell Integration
```powershell
# Convert to PowerShell objects
$result = python cli.py call-tool list_active_entries | ConvertFrom-Json

# Filter with PowerShell
$result.result.records | Where-Object { $_.primary_street -like "*FIFTH*" }

# Export to CSV
$result.result.records | Export-Csv closures.csv -NoTypeInformation
```

### Scheduled Tasks
```powershell
# Create daily_report.ps1
$date = Get-Date -Format "yyyy-MM-dd"
python cli.py call-tool list_active_entries | Out-File "report_$date.json"
```

Then schedule with Windows Task Scheduler.

## Testing

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

## Cross-Platform Development

You can now:
1. Develop on Windows with PowerShell
2. Test on WSL with bash scripts
3. Deploy on Linux servers
4. Share with team members on any platform

All using the **same CLI code** (`cli.py`)!

## Documentation

See `../server/WINDOWS_INSTALL.md` for:
- Detailed installation instructions
- PowerShell-specific examples
- Troubleshooting Windows issues
- Integration with PowerShell pipeline
- Task Scheduler configuration
- Excel/HTML export examples

## Summary

✅ **3 new files** for Windows support  
✅ **Full PowerShell integration**  
✅ **Comprehensive Windows documentation**  
✅ **Same functionality as Linux/macOS**  
✅ **PowerShell-native features** (pipelines, objects, scheduling)  

Your CLI now works seamlessly on Windows! 🎉
