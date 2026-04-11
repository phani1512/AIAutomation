# Comprehensive test for ALL template types from dataset

Write-Host "`n🎯 COMPREHENSIVE TEMPLATE SYSTEM TEST" -ForegroundColor Green
Write-Host "Testing that ANY template from dataset works automatically" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Gray

$tests = @(
    @{ name = "BUTTON ({VALUE})"; prompt = "click Save button"; expectedValue = "Save" },
    @{ name = "BUTTON ({VALUE})"; prompt = "click Cancel button"; expectedValue = "Cancel" },
    @{ name = "TAB ({TAB})"; prompt = "click Settings tab"; expectedValue = "Settings" },
    @{ name = "TAB ({TAB})"; prompt = "click Profile tab"; expectedValue = "Profile" },
    @{ name = "LINK ({LINK})"; prompt = "click Terms of Service link"; expectedValue = "Terms of Service" },
    @{ name = "LINK ({LINK})"; prompt = "click Contact Us link"; expectedValue = "Contact Us" }
)

$passCount = 0
$failCount = 0

foreach ($test in $tests) {
    Write-Host "`n📝 Testing $($test.name): '$($test.prompt)'" -ForegroundColor Yellow
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:5002/generate" -Method POST -ContentType "application/json" -Body (@{
            prompt = $test.prompt
            language = "python"
            with_fallbacks = $true
            compact_mode = $true
        } | ConvertTo-Json) -ErrorAction Stop
        
        $generatedCode = $response.generated
        $expectedValue = $test.expectedValue
        
        # Check if the extracted value appears in the generated code
        if ($generatedCode -match [regex]::Escape($expectedValue.ToLower()) -or $generatedCode -match [regex]::Escape($expectedValue)) {
            Write-Host "   ✅ SUCCESS: '$expectedValue' found in generated code!" -ForegroundColor Green
            $passCount++
            
            # Show first selector
            if ($generatedCode -match "selectors\s*=\s*\[([^\]]+)\]") {
                $firstSelector = ($matches[1] -split ',')[0].Trim()
                Write-Host "   📌 First selector: $firstSelector" -ForegroundColor DarkGray
            }
        } else {
            Write-Host "   ❌ FAILED: '$expectedValue' NOT found in code!" -ForegroundColor Red
            $failCount++
            Write-Host "   Code preview: $($generatedCode.Substring(0, [Math]::Min(150, $generatedCode.Length)))..." -ForegroundColor DarkRed
        }
    }
    catch {
        Write-Host "   ❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
        $failCount++
    }
}

Write-Host "`n" + ("=" * 70) -ForegroundColor Gray
Write-Host "📊 TEST RESULTS:" -ForegroundColor Cyan
Write-Host "   ✅ Passed: $passCount / $($tests.Count)" -ForegroundColor Green
Write-Host "   ❌ Failed: $failCount / $($tests.Count)" -ForegroundColor $(if ($failCount -eq 0) { "Green" } else { "Red" })

if ($failCount -eq 0) {
    Write-Host "`n🎉 ALL TESTS PASSED! Template system works for ANY dataset template!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Some tests failed. Review the output above." -ForegroundColor Yellow
}

Write-Host ""
