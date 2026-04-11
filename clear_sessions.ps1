Write-Host "`n🧹 CLEARING ALL TEST BUILDER SESSIONS" -ForegroundColor Cyan
Write-Host "="*70

# Get all active sessions
try {
    $sessions = Invoke-RestMethod -Uri "http://localhost:5002/test-suite/sessions" -Method GET
    
    if ($sessions) {
        Write-Host "Found $($sessions.Count) active sessions" -ForegroundColor Yellow
        
        foreach ($session in $sessions) {
            Write-Host "  Deleting: $($session.name) ($($session.session_id))" -ForegroundColor Gray
            
            try {
                $deleteResponse = Invoke-RestMethod -Uri "http://localhost:5002/test-suite/session/$($session.session_id)" -Method DELETE
                Write-Host "    ✅ Deleted" -ForegroundColor Green
            } catch {
                Write-Host "    ❌ Failed: $_" -ForegroundColor Red
            }
        }
        
        Write-Host "`n✅ All sessions cleared!" -ForegroundColor Green
        Write-Host "Refresh your browser and create a NEW test" -ForegroundColor Cyan
    } else {
        Write-Host "No active sessions found" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

Write-Host "="*70
