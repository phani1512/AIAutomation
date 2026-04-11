# Automated Folder Structure Migration Script
# Run from: C:\Users\valaboph\AIAutomation\
#
# WORKFLOW NOTES:
# - test_cases/builder/   → AI-generated tests (permanent, Git tracked)
# - test_cases/recorder/  → Saved recorded tests (permanent, Git tracked)
# - test_sessions/        → TEMPORARY in-progress recordings
#                         → Moved to test_cases/recorder/ when user saves
#                         → Deleted from test_sessions/ after save (cleanup)
#                         → Can execute tests in sessions before saving

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  FOLDER STRUCTURE MIGRATION SCRIPT                         ║" -ForegroundColor Cyan
Write-Host "║  Moving test data from src/resources/ to root level        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if running from correct directory
if (-not (Test-Path "src\resources")) {
    Write-Host "❌ ERROR: Please run this script from AIAutomation root directory" -ForegroundColor Red
    Write-Host "   Current directory: $PWD" -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/5] Checking existing folder structure..." -ForegroundColor Yellow
Write-Host ""

# Function to safely move folder contents
function Move-FolderContents {
    param (
        [string]$Source,
        [string]$Destination,
        [string]$FolderName
    )
    
    if (Test-Path $Source) {
        Write-Host "  📂 Found: $Source" -ForegroundColor Green
        
        # Create destination if it doesn't exist
        if (-not (Test-Path $Destination)) {
            New-Item -ItemType Directory -Path $Destination -Force | Out-Null
            Write-Host "  ✅ Created: $Destination" -ForegroundColor Green
        }
        
        # Count items to move
        $items = Get-ChildItem $Source -Recurse -File
        $itemCount = $items.Count
        Write-Host "  📊 Found $itemCount file(s) to move" -ForegroundColor Cyan
        
        if ($itemCount -gt 0) {
            # Move all contents
            Write-Host "  🚚 Moving files..." -ForegroundColor Cyan
            Get-ChildItem $Source | Move-Item -Destination $Destination -Force
            Write-Host "  ✅ Moved $itemCount file(s) from $Source to $Destination" -ForegroundColor Green
        } else {
            Write-Host "  ℹ️  No files to move (folder is empty)" -ForegroundColor Gray
        }
        
        # Remove old empty folder
        Remove-Item $Source -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  🗑️  Removed old folder: $Source" -ForegroundColor Gray
        Write-Host ""
        
        return $itemCount
    } else {
        Write-Host "  ℹ️  Folder not found: $Source (skipping)" -ForegroundColor Gray
        Write-Host ""
        return 0
    }
}

# Track total moved files
$totalMoved = 0

Write-Host "[2/5] Creating new root-level folders..." -ForegroundColor Yellow
Write-Host ""

# Create root-level folders
New-Item -ItemType Directory -Path "test_cases" -Force -ErrorAction SilentlyContinue | Out-Null
New-Item -ItemType Directory -Path "test_sessions" -Force -ErrorAction SilentlyContinue | Out-Null
New-Item -ItemType Directory -Path "test_suites" -Force -ErrorAction SilentlyContinue | Out-Null
New-Item -ItemType Directory -Path "execution_results" -Force -ErrorAction SilentlyContinue | Out-Null

Write-Host "  ✅ Root-level folders ready" -ForegroundColor Green
Write-Host ""

Write-Host "[3/5] Moving test data folders..." -ForegroundColor Yellow
Write-Host ""

# Move test_cases
$moved = Move-FolderContents -Source "src\resources\test_cases" -Destination "test_cases" -FolderName "Test Cases"
$totalMoved += $moved

# Move test_sessions
$moved = Move-FolderContents -Source "src\resources\test_sessions" -Destination "test_sessions" -FolderName "Test Sessions"
$totalMoved += $moved

# Move test_suites
$moved = Move-FolderContents -Source "src\resources\test_suites" -Destination "test_suites" -FolderName "Test Suites"
$totalMoved += $moved

# Move execution_results
$moved = Move-FolderContents -Source "src\resources\execution_results" -Destination "execution_results" -FolderName "Execution Results"
$totalMoved += $moved

Write-Host "[4/5] Creating .gitignore files..." -ForegroundColor Yellow
Write-Host ""

# Root .gitignore (update if exists, create if not)
$gitignoreContent = @"
# Execution results (NOT version controlled)
execution_results/
screenshots/

# Optional: Exclude active sessions (uncomment if needed)
# test_sessions/

# Python
*.pyc
__pycache__/
.venv/
*.pyo
*.egg-info/
.pytest_cache/

# Environment
.env
*.log

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
"@

$gitignorePath = ".gitignore"
if (Test-Path $gitignorePath) {
    # Append to existing .gitignore
    Write-Host "  📝 Updating existing .gitignore..." -ForegroundColor Cyan
    Add-Content -Path $gitignorePath -Value "`n# === Folder Migration Additions ===" -Force
    Add-Content -Path $gitignorePath -Value "execution_results/" -Force
    Add-Content -Path $gitignorePath -Value "screenshots/" -Force
    Write-Host "  ✅ Updated .gitignore" -ForegroundColor Green
} else {
    # Create new .gitignore
    Write-Host "  📝 Creating .gitignore..." -ForegroundColor Cyan
    Set-Content -Path $gitignorePath -Value $gitignoreContent -Force
    Write-Host "  ✅ Created .gitignore" -ForegroundColor Green
}

# execution_results/.gitignore
$execResultsIgnore = @"
# Ignore all execution results
*
!.gitignore
"@
Set-Content -Path "execution_results\.gitignore" -Value $execResultsIgnore -Force
Write-Host "  ✅ Created execution_results/.gitignore" -ForegroundColor Green

# Create screenshots folder if needed
if (-not (Test-Path "screenshots")) {
    New-Item -ItemType Directory -Path "screenshots" -Force | Out-Null
}

$screenshotsIgnore = @"
# Ignore all screenshots
*
!.gitignore
"@
Set-Content -Path "screenshots\.gitignore" -Value $screenshotsIgnore -Force
Write-Host "  ✅ Created screenshots/.gitignore" -ForegroundColor Green

Write-Host ""

Write-Host "[5/5] Migration Summary" -ForegroundColor Yellow
Write-Host ""

# Summary
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ MIGRATION COMPLETED SUCCESSFULLY!                      ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  📊 Total files moved: $totalMoved" -ForegroundColor Cyan
Write-Host ""
Write-Host "  📁 New Structure:" -ForegroundColor Cyan
Write-Host "     ├── test_cases/          (permanent saved tests)" -ForegroundColor White
Write-Host "     │   ├── builder/         (AI-generated)" -ForegroundColor Gray
Write-Host "     │   └── recorder/        (saved recordings)" -ForegroundColor Gray
Write-Host "     ├── test_sessions/       (TEMPORARY, in-progress)" -ForegroundColor White
Write-Host "     ├── test_suites/         (suite definitions)" -ForegroundColor White
Write-Host "     ├── execution_results/   (Git ignored)" -ForegroundColor White
Write-Host "     └── screenshots/         (Git ignored)" -ForegroundColor White
Write-Host ""
Write-Host "  🔄 Recorder Workflow:" -ForegroundColor Cyan
Write-Host "     1. Record test → test_sessions/ (temporary)" -ForegroundColor White
Write-Host "     2. User clicks Save → move to test_cases/recorder/" -ForegroundColor White
Write-Host "     3. Delete from test_sessions/ (cleanup)" -ForegroundColor White
Write-Host ""
Write-Host "  ⚠️  IMPORTANT: Next Steps Required" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1️⃣  Update Python code references:" -ForegroundColor White
Write-Host "      Find: 'src/resources/test_cases'" -ForegroundColor Gray
Write-Host "      Replace: 'test_cases'" -ForegroundColor Gray
Write-Host ""
Write-Host "  2️⃣  Files to check (recommended):" -ForegroundColor White
Write-Host "      - src/main/python/test_case_builder.py" -ForegroundColor Gray
Write-Host "      - src/main/python/test_session_manager.py" -ForegroundColor Gray
Write-Host "      - src/main/python/test_executor.py" -ForegroundColor Gray
Write-Host "      - src/main/python/api_server_modular.py" -ForegroundColor Gray
Write-Host ""
Write-Host "  3️⃣  Test the application:" -ForegroundColor White
Write-Host "      - Create a new test case" -ForegroundColor Gray
Write-Host "      - Execute a test" -ForegroundColor Gray
Write-Host "      - Verify file paths work correctly" -ForegroundColor Gray
Write-Host ""
Write-Host "  4️⃣  Git commands:" -ForegroundColor White
Write-Host "      git add test_cases/ test_suites/ .gitignore" -ForegroundColor Gray
Write-Host "      git commit -m 'Refactor: Move test data to root level'" -ForegroundColor Gray
Write-Host "      git push origin main" -ForegroundColor Gray
Write-Host ""
Write-Host "  📖 For detailed instructions, see: MIGRATE_FOLDER_STRUCTURE.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
