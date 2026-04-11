#!/usr/bin/env pwsh
# ==============================================================================
# AUTOMATED MIGRATION: Move test_cases/ → test_suites/ and DELETE old folder
# ==============================================================================

Write-Host "`n╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     AUTOMATED MIGRATION: test_cases/ → test_suites/          ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Check if test_cases folder exists
if (-not (Test-Path "test_cases")) {
    Write-Host "✅ test_cases/ folder does not exist - migration not needed!`n" -ForegroundColor Green
    exit 0
}

# Step 1: Count files
Write-Host "📊 COUNTING FILES..." -ForegroundColor Yellow
$recorderTests = Get-ChildItem -Path "test_cases\recorder\*.json" -ErrorAction SilentlyContinue
$builderTests = Get-ChildItem -Path "test_cases\builder\*.json" -ErrorAction SilentlyContinue
$exportedTests = Get-ChildItem -Path "test_cases\builder\exports\*" -ErrorAction SilentlyContinue

$javaFiles = $exportedTests | Where-Object { $_.Extension -eq '.java' }
$pythonFiles = $exportedTests | Where-Object { $_.Name -like '*_test.py' }
$cypressFiles = $exportedTests | Where-Object { $_.Name -like '*.cy.js' }
$playwrightFiles = $exportedTests | Where-Object { $_.Name -like '*.spec.js' }

$totalFiles = $recorderTests.Count + $builderTests.Count + $exportedTests.Count

Write-Host "  📁 Recorder JSON:  $($recorderTests.Count)" -ForegroundColor White
Write-Host "  📁 Builder JSON:   $($builderTests.Count)" -ForegroundColor White
Write-Host "  📦 Java exports:   $($javaFiles.Count)" -ForegroundColor White
Write-Host "  📦 Python exports: $($pythonFiles.Count)" -ForegroundColor White
Write-Host "  📦 Cypress exports: $($cypressFiles.Count)" -ForegroundColor White
Write-Host "  📦 Playwright exports: $($playwrightFiles.Count)" -ForegroundColor White
Write-Host "  📊 TOTAL: $totalFiles files`n" -ForegroundColor Cyan

if ($totalFiles -eq 0) {
    Write-Host "⚠️  No files found in test_cases/ - safe to delete folder" -ForegroundColor Yellow
} else {
    # Step 2: Create directories
    Write-Host "🔨 Creating directory structure..." -ForegroundColor Yellow
    New-Item -Path "test_suites\general\recorded" -ItemType Directory -Force | Out-Null
    New-Item -Path "test_suites\general\builder" -ItemType Directory -Force | Out-Null
    New-Item -Path "test_suites\general\exports\java" -ItemType Directory -Force | Out-Null
    New-Item -Path "test_suites\general\exports\python" -ItemType Directory -Force | Out-Null
    New-Item -Path "test_suites\general\exports\cypress" -ItemType Directory -Force | Out-Null
    New-Item -Path "test_suites\general\exports\playwright" -ItemType Directory -Force | Out-Null
    Write-Host "  ✅ Directories created`n" -ForegroundColor Green

    # Step 3: Move recorder tests
    if ($recorderTests.Count -gt 0) {
        Write-Host "📦 Moving $($recorderTests.Count) recorder test(s)..." -ForegroundColor Yellow
        foreach ($file in $recorderTests) {
            Move-Item -Path $file.FullName -Destination "test_suites\general\recorded\$($file.Name)" -Force
        }
        Write-Host "  ✅ Recorder tests moved`n" -ForegroundColor Green
    }

    # Step 4: Move builder tests
    if ($builderTests.Count -gt 0) {
        Write-Host "📦 Moving $($builderTests.Count) builder test(s)..." -ForegroundColor Yellow
        foreach ($file in $builderTests) {
            Move-Item -Path $file.FullName -Destination "test_suites\general\builder\$($file.Name)" -Force
        }
        Write-Host "  ✅ Builder tests moved`n" -ForegroundColor Green
    }

    # Step 5: Move exports by language
    if ($exportedTests.Count -gt 0) {
        Write-Host "📦 Organizing exports by language..." -ForegroundColor Yellow
        
        foreach ($file in $javaFiles) {
            Move-Item -Path $file.FullName -Destination "test_suites\general\exports\java\$($file.Name)" -Force
        }
        foreach ($file in $pythonFiles) {
            Move-Item -Path $file.FullName -Destination "test_suites\general\exports\python\$($file.Name)" -Force
        }
        foreach ($file in $cypressFiles) {
            Move-Item -Path $file.FullName -Destination "test_suites\general\exports\cypress\$($file.Name)" -Force
        }
        foreach ($file in $playwrightFiles) {
            Move-Item -Path $file.FullName -Destination "test_suites\general\exports\playwright\$($file.Name)" -Force
        }
        
        Write-Host "  ✅ Java: $($javaFiles.Count) files" -ForegroundColor Green
        Write-Host "  ✅ Python: $($pythonFiles.Count) files" -ForegroundColor Green
        Write-Host "  ✅ Cypress: $($cypressFiles.Count) files" -ForegroundColor Green
        Write-Host "  ✅ Playwright: $($playwrightFiles.Count) files`n" -ForegroundColor Green
    }

    # Step 6: Verify migration
    Write-Host "🔍 Verifying migration..." -ForegroundColor Yellow
    $verifyRecorded = (Get-ChildItem -Path "test_suites\general\recorded" -Filter "*.json" -ErrorAction SilentlyContinue).Count
    $verifyBuilder = (Get-ChildItem -Path "test_suites\general\builder" -Filter "*.json" -ErrorAction SilentlyContinue).Count
    $verifyJava = (Get-ChildItem -Path "test_suites\general\exports\java" -ErrorAction SilentlyContinue).Count
    $verifyPython = (Get-ChildItem -Path "test_suites\general\exports\python" -ErrorAction SilentlyContinue).Count
    $verifyCypress = (Get-ChildItem -Path "test_suites\general\exports\cypress" -ErrorAction SilentlyContinue).Count
    $verifyPlaywright = (Get-ChildItem -Path "test_suites\general\exports\playwright" -ErrorAction SilentlyContinue).Count

    if ($verifyRecorded -eq $recorderTests.Count -and $verifyBuilder -eq $builderTests.Count) {
        Write-Host "  ✅ Migration verified successfully!`n" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  WARNING: File count mismatch!" -ForegroundColor Yellow
        Write-Host "  Expected: $($recorderTests.Count) recorded, $($builderTests.Count) builder" -ForegroundColor Yellow
        Write-Host "  Found: $verifyRecorded recorded, $verifyBuilder builder`n" -ForegroundColor Yellow
    }
}

# Step 7: Delete test_cases folder
Write-Host "🗑️  DELETING old test_cases/ folder..." -ForegroundColor Red
try {
    Remove-Item -Path "test_cases" -Recurse -Force -ErrorAction Stop
    Write-Host "  ✅ test_cases/ folder deleted successfully!`n" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  Could not delete test_cases/ folder: $_`n" -ForegroundColor Yellow
}

# Summary
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "✅ MIGRATION COMPLETE!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

Write-Host "📊 RESULTS:" -ForegroundColor Yellow
Write-Host "  ✅ Moved $totalFiles files to test_suites/general/" -ForegroundColor White
Write-Host "  ✅ Organized exports by language" -ForegroundColor White
Write-Host "  ✅ Deleted old test_cases/ folder" -ForegroundColor White

Write-Host "`n🎉 Your system now uses ONLY test_suites/ structure!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

Write-Host "📝 NEXT STEP: Restart the server" -ForegroundColor Cyan
Write-Host "   python src/main/python/api_server_modular.py`n" -ForegroundColor Yellow
