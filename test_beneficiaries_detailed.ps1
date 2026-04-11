$testPayload = @{
    prompt = "click Beneficiaries button"
    language = "python"
    with_fallbacks = $true
    compact_mode = $true
} | ConvertTo-Json

Write-Host "`n🔬 DETAILED TEST: Beneficiaries Button" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

$response = Invoke-RestMethod -Uri "http://localhost:5002/generate" -Method POST -Body $testPayload -ContentType "application/json"

if ($response.generated) {
    $code = $response.generated
    
    # Extract the selectors line
    if ($code -match 'selectors = \[(.*?)\]') {
        $selectorsList = $matches[1]
        Write-Host "`n📍 SELECTORS GENERATED:" -ForegroundColor Yellow
        Write-Host "selectors = [$selectorsList]" -ForegroundColor White
        
        # Check what's in the first selector
        if ($selectorsList -like '*Beneficiaries*' -or $selectorsList -like '*beneficiaries*') {
            Write-Host "`n✅ CORRECT! Contains 'Beneficiaries'" -ForegroundColor Green
        } else {
            Write-Host "`n❌ WRONG! Does NOT contain 'Beneficiaries'" -ForegroundColor Red
            if ($selectorsList -like '*Confirm*') {
                Write-Host "   Found 'Confirm' instead - still matching wrong template!" -ForegroundColor Red
            }
        }
    }
    
    Write-Host "`n📄 Full Code:" -ForegroundColor Cyan
    Write-Host $code -ForegroundColor DarkGray
} else {
    Write-Host "`n❌ No code generated" -ForegroundColor Red
    Write-Host "Response:" -ForegroundColor Yellow
    Write-Host ($response | ConvertTo-Json) -ForegroundColor White
}
