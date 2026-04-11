# Restart API Server Script
Write-Host "Stopping API server..." -ForegroundColor Yellow

# Kill all Python processes running api_server_modular.py
Get-Process python* -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -and (Get-Process -Id $_.Id -ErrorAction SilentlyContinue | 
    Select-Object -ExpandProperty CommandLine -ErrorAction SilentlyContinue) -like "*api_server_modular.py*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Start-Sleep -Seconds 2

Write-Host "Starting API server..." -ForegroundColor Green
$env:PYTHONIOENCODING='utf-8'
Start-Process python -ArgumentList "src\main\python\api_server_modular.py" -NoNewWindow -WorkingDirectory $PSScriptRoot

Start-Sleep -Seconds 3

Write-Host "`nServer restarted!" -ForegroundColor Green
Write-Host "Wait a few seconds for initialization, then refresh your browser." -ForegroundColor Cyan
Write-Host "`nExpected logs after restart:" -ForegroundColor Yellow
Write-Host "  [MATCHER] Indexed 5024 exact entries (4247 variations), 42 templates" -ForegroundColor White
Write-Host "`nIf you see only 777 entries, the server didn't reload properly." -ForegroundColor Yellow
