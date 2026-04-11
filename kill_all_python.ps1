Write-Host "🔍 Finding ALL Python processes..." -ForegroundColor Cyan
Write-Host "="*70

$allPython = Get-Process | Where-Object {$_.ProcessName -like "*python*"}

if ($allPython) {
    Write-Host "`nFound $($allPython.Count) Python processes:" -ForegroundColor Yellow
    $allPython | ForEach-Object {
        Write-Host "`n  PID: $($_.Id)" -ForegroundColor White
        Write-Host "  Name: $($_.ProcessName)" -ForegroundColor Gray
        Write-Host "  Start: $($_.StartTime)" -ForegroundColor Gray
        Write-Host "  Path: $($_.Path)" -ForegroundColor Gray
    }
    
    Write-Host "`n💀 KILLING ALL..." -ForegroundColor Red
    $allPython | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "✅ All Python killed" -ForegroundColor Green
} else {
    Write-Host "No Python processes found" -ForegroundColor Green
}

Write-Host "="*70
