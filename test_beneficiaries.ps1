$testPayload = @{
    prompt = "click Beneficiaries button"
    language = "python"
    with_fallbacks = $true
    compact_mode = $true
} | ConvertTo-Json

Write-Host "`n🧪 TEST: Beneficiaries Button" -ForegroundColor Cyan
$response = Invoke-RestMethod -Uri "http://localhost:5002/generate" -Method POST -Body $testPayload -ContentType "application/json"

if ($response.generated) {
    $code = $response.generated
    Write-Host "`n📄 Code:" -ForegroundColor Green
    Write-Host $code -ForegroundColor White
    
    if ($code -like "*beneficiaries*") {
        Write-Host "`n✅ SUCCESS! 'Beneficiaries' found in selectors" -ForegroundColor Green
    } else {
        Write-Host "`n❌ FAILED - 'Beneficiaries' not found" -ForegroundColor Red
    }
} else {
    Write-Host "`n❌ No code generated" -ForegroundColor Red
}
