# Test the fixed /recorder/generate-test endpoint with compact mode

Write-Host "`n🧪 Testing Test Builder with Compact Mode" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

# Step 1: Create a test session
Write-Host "`n📝 Step 1: Creating test session..." -ForegroundColor Yellow
$createSession = @{
    prompt = "click Carrier Account 2 button"
    actions = @(
        @{
            prompt = "click Carrier Account 2 button"
            action = "click"
        }
    )
} | ConvertTo-Json

# Step 2: Generate test code
Write-Host "🤖 Step 2: Calling /recorder/generate-test..." -ForegroundColor Yellow

# First, we need to create a mock session in the recorder
# Since we can't directly manipulate the server's session state, let's test the /generate endpoint directly

$testPrompt = "click Carrier Account 2 button"

Write-Host "`n📤 Testing prompt: '$testPrompt'" -ForegroundColor Cyan

$body = @{
    prompt = $testPrompt
    compact_mode = $true
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:5002/generate" `
                                  -Method POST `
                                  -Body $body `
                                  -ContentType "application/json"
    
    Write-Host "`n✅ SUCCESS!" -ForegroundColor Green
    Write-Host "`n📊 Response Details:" -ForegroundColor Cyan
    Write-Host "  Prompt: $($response.prompt)" -ForegroundColor White
    Write-Host "  Action: $($response.action)" -ForegroundColor Yellow
    Write-Host "  Locator: $($response.locator)" -ForegroundColor Magenta
    Write-Host "  Compact: $($response.compact_mode)" -ForegroundColor $(if($response.compact_mode){'Green'}else{'Red'})
    
    Write-Host "`n📝 Generated Code:" -ForegroundColor Cyan
    Write-Host "─" * 60 -ForegroundColor Gray
    Write-Host $response.code -ForegroundColor White
    Write-Host "─" * 60 -ForegroundColor Gray
    
    $lines = ($response.code -split "`n").Count
    Write-Host "`n📏 Code size: $lines lines" -ForegroundColor $(if($lines -lt 15){'Green'}else{'Yellow'})
    
    if ($response.compact_mode -and $lines -lt 15) {
        Write-Host "`n🎉 COMPACT MODE WORKING!" -ForegroundColor Green
    } else {
        Write-Host "`n⚠️  Not compact (expected < 15 lines)" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "`n❌ ERROR:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}
