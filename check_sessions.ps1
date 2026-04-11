Write-Host "`n🔍 DIAGNOSTIC CHECK" -ForegroundColor Yellow
Write-Host "="*70

# Check if server is running
Write-Host "`n1. Server Check:" -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "http://localhost:5002/health" -TimeoutSec 2
    Write-Host "  ✅ Server is RUNNING" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Server is NOT running!" -ForegroundColor Red
    exit 1
}

# Check test sessions
Write-Host "`n2. Test Sessions:" -ForegroundColor Cyan
try {
    $sessions = Invoke-RestMethod -Uri "http://localhost:5002/test-suite/sessions" -TimeoutSec 2
    if ($sessions.Count -gt 0) {
        Write-Host "  ⚠️ Found $($sessions.Count) OLD sessions in memory!" -ForegroundColor Red
        $sessions | Select-Object -First 3 | ForEach-Object {
            Write-Host "    - $($_.name)" -ForegroundColor Yellow
        }
        Write-Host "`n  💡 These tests were created BEFORE the fix!" -ForegroundColor Yellow
        Write-Host "  💡 Delete them or create a BRAND NEW test!" -ForegroundColor Yellow
    } else {
        Write-Host "  ✅ No old sessions (good!)" -ForegroundColor Green
    }
} catch {
    Write-Host "  Error: $_" -ForegroundColor Red
}

# Check source code
Write-Host "`n3. Source Code Check:" -ForegroundColor Cyan
$line = Get-Content "src\main\python\test_case_builder.py" | Select-Object -Skip 240 -First 1
if ($line -like "*os.path.dirname(os.path.abspath*") {
    Write-Host "  ✅ Source code is CORRECT" -ForegroundColor Green
    Write-Host "    Line 241: $line" -ForegroundColor Gray
} else {
    Write-Host "  ❌ Source code is WRONG!" -ForegroundColor Red
    Write-Host "    Line 241: $line" -ForegroundColor Gray
}

Write-Host "`n="*70
