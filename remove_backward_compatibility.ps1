#!/usr/bin/env pwsh
# ==============================================================================
# CLEANUP SCRIPT: Remove Backward Compatibility Code
# ==============================================================================
# Purpose: Remove dual-directory scanning code from Python backend
# Run this AFTER running migrate_to_test_suites.ps1
# ==============================================================================

Write-Host "`n╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       REMOVE BACKWARD COMPATIBILITY CODE                     ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "⚠️  WARNING: This will modify Python backend files!" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

Write-Host "📋 CODE TO BE REMOVED:" -ForegroundColor Yellow
Write-Host "  • recorder_handler.py: 31 lines (backward compatibility for test_cases/recorder/)" -ForegroundColor White
Write-Host "  • test_case_builder.py: ~30 lines (dual-directory scanning)" -ForegroundColor White
Write-Host "  • TOTAL: ~61 lines of code" -ForegroundColor White

Write-Host "`n✅ BENEFITS:" -ForegroundColor Green
Write-Host "  • Simpler codebase" -ForegroundColor Gray
Write-Host "  • Single source of truth" -ForegroundColor Gray
Write-Host "  • Faster file scanning" -ForegroundColor Gray
Write-Host "  • Easier to maintain" -ForegroundColor Gray

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

$confirm = Read-Host "⚠️  Proceed with code cleanup? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "`n❌ Cleanup cancelled by user`n" -ForegroundColor Red
    exit 0
}

Write-Host "`n🚀 STARTING CLEANUP..." -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

# Backup files first
Write-Host "  1️⃣  Creating backups..." -NoNewline
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "backups\migration_$timestamp"
New-Item -Path $backupDir -ItemType Directory -Force | Out-Null

Copy-Item "src\main\python\recorder\recorder_handler.py" "$backupDir\recorder_handler.py.bak" -Force
Copy-Item "src\main\python\test_management\test_case_builder.py" "$backupDir\test_case_builder.py.bak" -ErrorAction SilentlyContinue

Write-Host " ✅ DONE" -ForegroundColor Green
Write-Host "     • Backups saved to: $backupDir" -ForegroundColor Gray

# Instructions for manual cleanup
Write-Host "`n  2️⃣  Code cleanup instructions:" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

Write-Host "📝 MANUAL STEPS (GitHub Copilot can help):" -ForegroundColor Cyan

Write-Host "`n  📄 File 1: recorder_handler.py" -ForegroundColor Yellow
Write-Host "     Location: src/main/python/recorder/recorder_handler.py" -ForegroundColor Gray
Write-Host "     Function: list_saved_recorder_tests() (around line 644)" -ForegroundColor Gray
Write-Host "     Remove: Lines containing 'ALSO scan OLD location (test_cases/recorder/)'" -ForegroundColor White
Write-Host "     Block: ~31 lines starting with '# ALSO scan OLD location...'" -ForegroundColor White

Write-Host "`n  📄 File 2: test_case_builder.py" -ForegroundColor Yellow
Write-Host "     Location: src/main/python/test_management/test_case_builder.py" -ForegroundColor Gray
Write-Host "     Function: list_test_cases() (around line 1024)" -ForegroundColor Gray
Write-Host "     Remove: Scanning of 'test_cases/builder/' directory" -ForegroundColor White
Write-Host "     Keep: Only test_suites/{test_type}/builder/ scanning" -ForegroundColor White

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "💡 TIP: Ask GitHub Copilot:" -ForegroundColor Cyan
Write-Host "   'Remove backward compatibility code for test_cases/ from" -ForegroundColor Gray
Write-Host "    recorder_handler.py and test_case_builder.py'" -ForegroundColor Gray
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

Write-Host "⏸️  PAUSED - Waiting for manual code cleanup..." -ForegroundColor Yellow
Write-Host "After removing the code, restart the API server and test.`n" -ForegroundColor Gray

$completedManual = Read-Host "Have you completed the manual cleanup? (yes/no)"
if ($completedManual -eq "yes") {
    Write-Host "`n✅ CLEANUP COMPLETE!" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray
    
    Write-Host "📝 FINAL STEPS:" -ForegroundColor Yellow
    Write-Host "  1. Restart API server: python src/main/python/api_server_modular.py" -ForegroundColor White
    Write-Host "  2. Test dropdowns show all migrated tests" -ForegroundColor White
    Write-Host "  3. Verify semantic analysis workflow" -ForegroundColor White
    Write-Host "  4. If everything works, delete test_cases/ folder" -ForegroundColor White
    Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray
} else {
    Write-Host "`n⏭️  You can complete the cleanup later`n" -ForegroundColor Yellow
}
