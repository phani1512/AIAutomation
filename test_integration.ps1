#!/usr/bin/env pwsh
# PowerShell script to test all integration options

Write-Host ""
Write-Host ("=" * 60)
Write-Host "🧪 TESTING ALL INTEGRATION OPTIONS"
Write-Host ("=" * 60)

# Test 1: API Server Health
Write-Host "`n📡 Test 1: API Server Health Check"
Write-Host ("-" * 60)

try {
    $response = Invoke-RestMethod -Uri "http://localhost:5001/health" -Method Get -ErrorAction Stop
    Write-Host "✅ API Server is running"
    Write-Host "   Response: $($response | ConvertTo-Json -Compress)"
} catch {
    Write-Host "❌ API Server not responding"
    Write-Host "   Please start the server: python src/main/python/api_server_modular.py"
}

# Test 2: Generate Code
Write-Host "`n🔧 Test 2: Generate Selenium Code"
Write-Host ("-" * 60)

$generatePayload = @{
    prompt = "method: beforeClick`naction: click`nelement_type: button"
    max_tokens = 50
    temperature = 0.7
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:5001/generate" `
        -Method Post `
        -ContentType "application/json" `
        -Body $generatePayload `
        -ErrorAction Stop
    
    Write-Host "✅ Code generated successfully"
    Write-Host "   Prompt: $($response.prompt)"
    Write-Host "   Generated:`n$($response.generated)"
} catch {
    Write-Host "❌ Failed to generate code"
    Write-Host "   Error: $_"
}

# Test 3: Suggest Locator
Write-Host "`n🎯 Test 3: Suggest Optimal Locator"
Write-Host ("-" * 60)

$locatorPayload = @{
    element_type = "input"
    action = "sendKeys"
    attributes = @{
        id = "username"
        name = "user"
        class = "form-control"
    }
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:5001/suggest-locator" `
        -Method Post `
        -ContentType "application/json" `
        -Body $locatorPayload `
        -ErrorAction Stop
    
    Write-Host "✅ Locators suggested"
    Write-Host "   Element: $($response.element_type)"
    Write-Host "   Action: $($response.action)"
    Write-Host "   Suggested Locators:"
    foreach ($locator in $response.suggested_locators) {
        Write-Host "     - $locator"
    }
} catch {
    Write-Host "❌ Failed to suggest locator"
    Write-Host "   Error: $_"
}

# Test 4: Suggest Action
Write-Host "`n⚡ Test 4: Suggest Action for Element"
Write-Host ("-" * 60)

$actionPayload = @{
    element_type = "button"
    context = "login form"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:5001/suggest-action" `
        -Method Post `
        -ContentType "application/json" `
        -Body $actionPayload `
        -ErrorAction Stop
    
    Write-Host "✅ Actions suggested"
    Write-Host "   Element: $($response.element_type)"
    Write-Host "   Suggested Actions: $($response.suggested_actions -join ', ')"
} catch {
    Write-Host "❌ Failed to suggest action"
    Write-Host "   Error: $_"
}

# Summary
Write-Host "`n"
Write-Host ("=" * 60)
Write-Host "📊 TEST SUMMARY"
Write-Host ("=" * 60)
Write-Host "All API endpoints tested"
Write-Host "Run 'python src/main/python/demo_all_options.py' for full demo"
Write-Host ("=" * 60)
Write-Host ""
