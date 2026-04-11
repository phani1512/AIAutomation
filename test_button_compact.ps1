$testPayload = @{
    prompt = "click login button"
    language = "python"
    with_fallbacks = $true
    compact_mode = $true
} | ConvertTo-Json

Write-Host "`n🧪 TESTING WITH BUTTON CLICK" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

$response = Invoke-RestMethod -Uri "http://localhost:5002/generate" -Method POST -Body $testPayload -ContentType "application/json"

if ($response.generated) {
    $codeLines = @($response.generated -split "`n").Count
    Write-Host "`n📊 Result: $codeLines lines of code" -ForegroundColor White
    
    if ($codeLines -le 10) {
        Write-Host "✅ COMPACT MODE WORKING! (Expected: 7-10 lines)" -ForegroundColor Green
    } else {
        Write-Host "❌ Code still verbose (Expected: 7-10, got: $codeLines)" -ForegroundColor Red
    }
    
    Write-Host "`n📄 Generated Code:" -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host $response.generated
    Write-Host "================================" -ForegroundColor Cyan
} else {
    Write-Host "❌ No code generated" -ForegroundColor Red
}
