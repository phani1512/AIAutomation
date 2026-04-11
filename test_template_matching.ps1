$testPayload = @{
    prompt = "click Carrier Account 2 button"
    language = "python"
    with_fallbacks = $true
    compact_mode = $true
} | ConvertTo-Json

Write-Host "`n🧪 TESTING TEMPLATE MATCHING + COMPACT MODE" -ForegroundColor Cyan
Write-Host "Prompt: click Carrier Account 2 button" -ForegroundColor Yellow
Write-Host "Expected: Template match with 'Carrier Account 2' substituted" -ForegroundColor Gray
Write-Host "=" * 60 -ForegroundColor Cyan

$response = Invoke-RestMethod -Uri "http://localhost:5002/generate" -Method POST -Body $testPayload -ContentType "application/json"

if ($response.generated) {
    $code = $response.generated
    $codeLines = @($code -split "`n").Count
    
    Write-Host "`n📊 RESULT:" -ForegroundColor Green
    Write-Host "  Lines of code: $codeLines" -ForegroundColor White
    
    # Check for template substitution
    if ($code -like "*Carrier Account 2*") {
        Write-Host "  ✅ Template substitution WORKING! Found 'Carrier Account 2' in selectors" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Template substitution FAILED - 'Carrier Account 2' not found" -ForegroundColor Red
    }
    
    # Check for compact mode
    if ($codeLines -le 10) {
        Write-Host "  ✅ Compact mode WORKING! ($codeLines lines)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Code verbose ($codeLines lines, expected 8-10)" -ForegroundColor Yellow
    }
    
    # Check for multiple selectors
    if ($code -like "*selectors = *") {
        $selectorsMatch = [regex]::Match($code, 'selectors = \[(.*?)\]', [System.Text.RegularExpressions.RegexOptions]::Singleline)
        if ($selectorsMatch.Success) {
            $selectorCount = ([regex]::Matches($selectorsMatch.Value, '["'']')).Count / 2
            Write-Host "  ✅ Self-healing with $selectorCount fallback selectors" -ForegroundColor Green
        }
    }
    
    Write-Host "`n📄 Generated Code:" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host $code -ForegroundColor White
    Write-Host "=" * 60 -ForegroundColor Cyan
    
    # Summary
    Write-Host "`n✨ SUMMARY:" -ForegroundColor Magenta
    if ($code -like "*Carrier Account 2*" -and $codeLines -le 10) {
        Write-Host "  🎉 SUCCESS! Template matching + Compact mode both working!" -ForegroundColor Green
    } elseif ($code -like "*Carrier Account 2*") {
        Write-Host "  ⚠️  Template works but code not compact" -ForegroundColor Yellow
    } else {
        Write-Host "  ❌ Template matching not working" -ForegroundColor Red
    }
} else {
    Write-Host "`n❌ No code generated" -ForegroundColor Red
}
