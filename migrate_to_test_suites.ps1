#!/usr/bin/env pwsh
# ==============================================================================
# MIGRATION SCRIPT: Consolidate test_cases/ → test_suites/
# ==============================================================================
# Purpose: Move old test_cases/ files to test_suites/general/ structure
#          and remove backward compatibility code
# ==============================================================================

Write-Host "`n╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         MIGRATE TO UNIFIED test_suites/ STRUCTURE            ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Step 1: Check current structure
Write-Host "📂 CURRENT FILE INVENTORY" -ForegroundColor Yellow
Write-Host "══════════════════════════════════════════════════════════════`n" -ForegroundColor Gray

$recorderTests = Get-ChildItem -Path "test_cases\recorder\*.json" -ErrorAction SilentlyContinue
$builderTests = Get-ChildItem -Path "test_cases\builder\*.json" -ErrorAction SilentlyContinue
$exportedTests = Get-ChildItem -Path "test_cases\builder\exports\*" -ErrorAction SilentlyContinue

Write-Host "  📁 test_cases/recorder/  → " -NoNewline -ForegroundColor White
Write-Host "$($recorderTests.Count) JSON files" -ForegroundColor Cyan
$recorderTests | ForEach-Object { Write-Host "     - $($_.Name)" -ForegroundColor Gray }

Write-Host "`n  📁 test_cases/builder/   → " -NoNewline -ForegroundColor White
Write-Host "$($builderTests.Count) JSON files" -ForegroundColor Cyan
$builderTests | ForEach-Object { Write-Host "     - $($_.Name)" -ForegroundColor Gray }

Write-Host "`n  📁 test_cases/builder/exports/ → " -NoNewline -ForegroundColor White
Write-Host "$($exportedTests.Count) exported files" -ForegroundColor Cyan

# Group exports by language
$javaFiles = $exportedTests | Where-Object { $_.Extension -eq '.java' }
$pythonFiles = $exportedTests | Where-Object { $_.Name -like '*_test.py' }
$cypressFiles = $exportedTests | Where-Object { $_.Name -like '*.cy.js' }
$playwrightFiles = $exportedTests | Where-Object { $_.Name -like '*.spec.js' }

Write-Host "     • Java (Selenium): $($javaFiles.Count)" -ForegroundColor Gray
Write-Host "     • Python (Pytest): $($pythonFiles.Count)" -ForegroundColor Gray
Write-Host "     • Cypress: $($cypressFiles.Count)" -ForegroundColor Gray
Write-Host "     • Playwright: $($playwrightFiles.Count)" -ForegroundColor Gray

$totalFiles = $recorderTests.Count + $builderTests.Count + $exportedTests.Count
Write-Host "`n  📊 TOTAL FILES TO MIGRATE: $totalFiles" -ForegroundColor Green

# Step 2: Confirm migration
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "📋 MIGRATION PLAN" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

Write-Host "  1️⃣  Create test_suites/general/{recorded,builder,exports}/" -ForegroundColor White
Write-Host "  2️⃣  Move $($recorderTests.Count) recorder tests → test_suites/general/recorded/" -ForegroundColor White
Write-Host "  3️⃣  Move $($builderTests.Count) builder tests → test_suites/general/builder/" -ForegroundColor White
Write-Host "  4️⃣  Organize $($exportedTests.Count) exports by language:" -ForegroundColor White
Write-Host "      • $($javaFiles.Count) Java → test_suites/general/exports/java/" -ForegroundColor Gray
Write-Host "      • $($pythonFiles.Count) Python → test_suites/general/exports/python/" -ForegroundColor Gray
Write-Host "      • $($cypressFiles.Count) Cypress → test_suites/general/exports/cypress/" -ForegroundColor Gray
Write-Host "      • $($playwrightFiles.Count) Playwright → test_suites/general/exports/playwright/" -ForegroundColor Gray
Write-Host "  5️⃣  Remove backward compatibility code (31 lines from recorder_handler.py)" -ForegroundColor White
Write-Host "  6️⃣  Remove dual scanning code from test_case_builder.py" -ForegroundColor White
Write-Host "  7️⃣  Delete empty test_cases/ folder" -ForegroundColor White

Write-Host "`n  ✅ BENEFITS:" -ForegroundColor Green
Write-Host "     • Single source of truth (test_suites/ only)" -ForegroundColor Gray
Write-Host "     • Cleaner codebase (~60 lines removed)" -ForegroundColor Gray
Write-Host "     • Easier maintenance" -ForegroundColor Gray
Write-Host "     • Industry-standard structure" -ForegroundColor Gray

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

$confirm = Read-Host "⚠️  Proceed with migration? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "`n❌ Migration cancelled by user`n" -ForegroundColor Red
    exit 0
}

Write-Host "`n🚀 STARTING MIGRATION..." -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

# Step 3: Create target directories
Write-Host "  1️⃣  Creating directory structure..." -NoNewline
$recordedDir = "test_suites\general\recorded"
$builderDir = "test_suites\general\builder"
$exportsBaseDir = "test_suites\general\exports"

New-Item -Path $recordedDir -ItemType Directory -Force | Out-Null
New-Item -Path $builderDir -ItemType Directory -Force | Out-Null
New-Item -Path "$exportsBaseDir\java" -ItemType Directory -Force | Out-Null
New-Item -Path "$exportsBaseDir\python" -ItemType Directory -Force | Out-Null
New-Item -Path "$exportsBaseDir\cypress" -ItemType Directory -Force | Out-Null
New-Item -Path "$exportsBaseDir\playwright" -ItemType Directory -Force | Out-Null
Write-Host " ✅ DONE" -ForegroundColor Green

# Step 4: Move recorder tests
Write-Host "  2️⃣  Moving recorder tests..." -NoNewline
$movedRecorder = 0
foreach ($file in $recorderTests) {
    $destination = Join-Path $recordedDir $file.Name
    Move-Item -Path $file.FullName -Destination $destination -Force
    $movedRecorder++
}
Write-Host " ✅ DONE ($movedRecorder files)" -ForegroundColor Green

# Step 5: Move builder tests
Write-Host "  3️⃣  Moving builder tests..." -NoNewline
$movedBuilder = 0
foreach ($file in $builderTests) {
    $destination = Join-Path $builderDir $file.Name
    Move-IMove exported files by language
Write-Host "  4️⃣  Organizing exported files by language..." -NoNewline
$movedJava = 0
$movedPython = 0
$movedCypress = 0
$movedPlaywright = 0

# Step 7: Verify migration
Write-Host "  5️⃣  Verifying migration..." -NoNewline
$verifyRecorded = (Get-ChildItem -Path $recordedDir -Filter "*.json" -ErrorAction SilentlyContinue).Count
$verifyBuilder = (Get-ChildItem -Path $builderDir -Filter "*.json" -ErrorAction SilentlyContinue).Count
$verifyJava = (Get-ChildItem -Path "$exportsBaseDir\java" -Filter "*.java" -ErrorAction SilentlyContinue).Count
$verifyPython = (Get-ChildItem -Path "$exportsBaseDir\python" -Filter "*_test.py" -ErrorAction SilentlyContinue).Count
$verifyCypress = (Get-ChildItem -Path "$exportsBaseDir\cypress" -Filter "*.cy.js" -ErrorAction SilentlyContinue).Count
$verifyPlaywright = (Get-ChildItem -Path "$exportsBaseDir\playwright" -Filter "*.spec.js" -ErrorAction SilentlyContinue).Count

$totalExports = $verifyJava + $verifyPython + $verifyCypress + $verifyPlaywright

if ($verifyRecorded -eq $recorderTests.Count -and $verifyBuilder -eq $builderTests.Count -and $totalExports -eq $exportedTests.Count) {
    Write-Host " ✅ DONE" -ForegroundColor Green
    Write-Host "     • Recorded: $verifyRecorded files in $recordedDir" -ForegroundColor Gray
    Write-Host "     • Builder: $verifyBuilder files in $builderDir" -ForegroundColor Gray
    Write-Host "     • Java exports: $verifyJava files" -ForegroundColor Gray
    Write-Host "     • Python exports: $verifyPython files" -ForegroundColor Gray
    Write-Host "     • Cypress exports: $verifyCypress files" -ForegroundColor Gray
    Write-Host "     • Playwright exports: $verifyPlaywright files" -ForegroundColor Gray
} else {
    Write-Host " ⚠️  WARNING: File count mismatch!" -ForegroundColor Yellow
    Write-Host "     Expected: $($recorderTests.Count) recorded, $($builderTests.Count) builder, $($exportedTests.Count) exports" -ForegroundColor Yellow
    Write-Host "     Found: $verifyRecorded recorded, $verifyBuilder builder, $totalExports exports" -ForegroundColor Yellow
}

# Step 8: Clean up empty test_cases/ folders
Write-Host "  6files
foreach ($file in $cypressFiles) {
    $destination = Join-Path "$exportsBaseDir\cypress" $file.Name
    Move-Item -Path $file.FullName -Destination $destination -Force
    $movedCypress++
}

# Move Playwright files
foreach ($file in $playwrightFiles) {
    $destination = Join-Path "$exportsBaseDir\playwright" $file.Name
    Move-Item -Path $file.FullName -Destination $destination -Force
    $movedPlaywright++
}

Write-Host " ✅ DONE" -ForegroundColor Green
Write-Host "     • Java: $movedJava files" -ForegroundColor Gray
Write-Host "     • Python: $movedPython files" -ForegroundColor Gray
Write-Host "     • Cypress: $movedCypress files" -ForegroundColor Gray
Write-Host "     • Playwright: $movedPlaywright files" -ForegroundColor Gray

# Step 7: Verify migration
Write-Host "  5er++
}
Write-Host " ✅ DONE ($movedBuilder files)" -ForegroundColor Green

# Step 6: Verify migration
Write-Host "  4️⃣  Verifying migration..." -NoNewline
$verifyRecorded = (Get-ChildItem -Path $recordedDir -Filter "*.json" -ErrorAction SilentlyContinue).Count
$verifyBuilder = (Get-ChildItem -Path $builderDir -Filter "*.json" -ErrorAction SilentlyContinue).Count

if ($verifyRecorded -eq $recorderTests.Count -and $verifyBuilder -eq $builderTests.Count) {
    Write-Host " ✅ DONE" -ForegroundColor Green
    Write-Host "     • Recorded: $verifyRecorded files in $recordedDir" -ForegroundColor Gray
    Write-Host "     • Builder: $verifyBuilder files in $builderDir" -ForegroundColor Gray
} else {
    Write-Host " ⚠️  WARNING: File count mismatch!" -ForegroundColor Yellow
    Write-Host "     Expected: $($recorderTests.Count) recorded, $($builderTests.Count) builder" -ForegroundColor Yellow
    Write-Host "     Found: $verifyRecorded recorded, $verifyBuilder builder" -ForegroundColor Yellow
}

# Step 7: Clean up empty test_cases/ folders
Write-Host "  5️⃣  Cleaning up old structure..." -NoNewline
$confirmDelete = Read-Host "`n     Delete test_cases/ folder now? (yes/no)"
if ($confirmDelete -eq "yes") {
    Remove-Item -Path "test_cases" -Recurse -Force -ErrorAction Sil + $movedJava + $movedPython + $movedCypress + $movedPlaywright)" -ForegroundColor White
Write-Host "     • Recorder tests: $movedRecorder → test_suites/general/recorded/" -ForegroundColor White
Write-Host "     • Builder tests: $movedBuilder → test_suites/general/builder/" -ForegroundColor White
Write-Host "     • Exported tests (organized by language):" -ForegroundColor White
Write-Host "       - Java: $movedJava → test_suites/general/exports/java/" -ForegroundColor Gray
Write-Host "       - Python: $movedPython → test_suites/general/exports/python/" -ForegroundColor Gray
Write-Host "       - Cypress: $movedCypress → test_suites/general/exports/cypress/" -ForegroundColor Gray
Write-Host "       - Playwright: $movedPlaywright → test_suites/general/exports/playwright/" -ForegroundColor Gray
    Write-Host "     ⏭️  SKIPPED (you can manually delete test_cases/ later)" -ForegroundColor Yellow
}

# Step 8: Summary
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "✅ FILE MIGRATION COMPLETE!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

Write-Host "  📊 MIGRATION SUMMARY:" -ForegroundColor Yellow
Write-Host "     • Files migrated: $($movedRecorder + $movedBuilder)" -ForegroundColor White
Write-Host "     • Recorder tests: $movedRecorder → test_suites/general/recorded/" -ForegroundColor White
Write-Host "     • Builder tests: $movedBuilder → test_suites/general/bu cases appear in dropdowns" -ForegroundColor White
Write-Host "     4. Verify exported files work (Java, Python, Cypress, Playwright)" -ForegroundColor White
Write-Host "     5. Test
Write-Host "`n  📝 NEXT STEPS:" -ForegroundColor Yellow
Write-Host "     1. Remove backward compatibility code from Python files" -ForegroundColor White
Write-Host "     2. Restart the API server" -ForegroundColor White
Write-Host "     3. Test that all $($movedRecorder + $movedBuilder) tests appear in dropdowns" -ForegroundColor White
Write-Host "     4. Verify semantic analysis save workflow" -ForegroundColor White

Write-Host "`n  💡 TO REMOVE BACKWARD COMPATIBILITY CODE:" -ForegroundColor Cyan
Write-Host "     Run: " -NoNewline -ForegroundColor Gray
Write-Host ".\remove_backward_compatibility.ps1" -ForegroundColor Yellow

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray
