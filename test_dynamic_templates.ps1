# Test dynamic template substitution for ALL template types

Write-Host "`n🧪 TESTING DYNAMIC TEMPLATE SYSTEM" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

# Test 1: Button template
Write-Host "`n1️⃣ Testing BUTTON template: 'click Beneficiaries button'" -ForegroundColor Yellow
$response1 = Invoke-RestMethod -Uri "http://localhost:5002/generate" -Method POST -ContentType "application/json" -Body (@{
    prompt = "click Beneficiaries button"
    language = "python"
    with_fallbacks = $true
    compact_mode = $true
} | ConvertTo-Json)

if ($response1.generated -match "Beneficiaries") {
    Write-Host "   ✅ SUCCESS: 'Beneficiaries' found in selectors!" -ForegroundColor Green
    # Extract and display first selector
    if ($response1.generated -match "selectors\s*=\s*\[(.*?)\]") {
        $selectors = $matches[1] -split ',' | Select-Object -First 3
        Write-Host "   📝 First 3 selectors:" -ForegroundColor Cyan
        foreach ($sel in $selectors) {
            Write-Host "      - $($sel.Trim())" -ForegroundColor White
        }
    }
} else {
    Write-Host "   ❌ FAILED: 'Beneficiaries' NOT found!" -ForegroundColor Red
}

# Test 2: Tab template 
Write-Host "`n2️⃣ Testing TAB template: 'click Overview tab'" -ForegroundColor Yellow
$response2 = Invoke-RestMethod -Uri "http://localhost:5002/generate" -Method POST -ContentType "application/json" -Body (@{
    prompt = "click Overview tab"
    language = "python"
    with_fallbacks = $true
    compact_mode = $true
} | ConvertTo-Json)

if ($response2.generated -match "Overview") {
    Write-Host "   ✅ SUCCESS: 'Overview' found in selectors!" -ForegroundColor Green
} else {
    Write-Host "   ❌ FAILED: 'Overview' NOT found!" -ForegroundColor Red
}

# Test 3: Link template
Write-Host "`n3️⃣ Testing LINK template: 'click Privacy Policy link'" -ForegroundColor Yellow
$response3 = Invoke-RestMethod -Uri "http://localhost:5002/generate" -Method POST -ContentType "application/json" -Body (@{
    prompt = "click Privacy Policy link"
    language = "python"
    with_fallbacks = $true
    compact_mode = $true
} | ConvertTo-Json)

if ($response3.generated -match "Privacy Policy") {
    Write-Host "   ✅ SUCCESS: 'Privacy Policy' found in selectors!" -ForegroundColor Green
} else {
    Write-Host "   ❌ FAILED: 'Privacy Policy' NOT found!" -ForegroundColor Red
}

# Test 4: Another button to verify it's truly dynamic
Write-Host "`n4️⃣ Testing BUTTON template: 'click Submit button'" -ForegroundColor Yellow
$response4 = Invoke-RestMethod -Uri "http://localhost:5002/generate" -Method POST -ContentType "application/json" -Body (@{
    prompt = "click Submit button"
    language = "python"
    with_fallbacks = $true
    compact_mode = $true
} | ConvertTo-Json)

if ($response4.generated -match "Submit") {
    Write-Host "   ✅ SUCCESS: 'Submit' found in selectors!" -ForegroundColor Green
} else {
    Write-Host "   ❌ FAILED: 'Submit' NOT found!" -ForegroundColor Red
}

Write-Host "`n" + ("=" * 60) -ForegroundColor Gray
Write-Host "✨ All templates should work dynamically from dataset!" -ForegroundColor Green
Write-Host ""
