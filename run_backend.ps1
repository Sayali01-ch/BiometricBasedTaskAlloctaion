$ErrorActionPreference = "Stop"

$backend = "C:\Users\Sanskruti Chopade\BiometricRealtimeTask\backend"
$venvPath = Join-Path $backend ".venv"
if (-not (Test-Path $venvPath)) {
    python -m venv $venvPath
    $py = Join-Path $venvPath "Scripts/python.exe"
} else {
    $py = Join-Path $venvPath "Scripts/python.exe"
}
# Your credentials path
$env:FCM_SERVICE_ACCOUNT_JSON = (Join-Path $backend "credentials/firebase-credentials.json")
$targetPort = "8000"

Set-Location $backend

# Ensure dependencies exist
& $py -m pip install -r requirements.txt

# Free Port 8000
$p = (Get-NetTCPConnection -LocalPort $targetPort -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1).OwningProcess
if ($p) {
    Write-Host "Stopping existing process on port $targetPort..."
    Stop-Process -Id $p -Force
    Start-Sleep -Seconds 1
}

# Firewall rule
try {
    
    New-NetFirewallRule -DisplayName "BiometricTask_$targetPort" -Direction Inbound -Protocol TCP -LocalPort $targetPort -Action Allow -ErrorAction SilentlyContinue | Out-Null
} catch {}

$env:PORT = $targetPort
# $env:DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/ID/TOKEN" # Replace with Discord webhook

Write-Host "---"
Write-Host "Starting backend at http://localhost:$targetPort ..."
Write-Host "TEAMS_WEBHOOK_URL: $(if ($env:TEAMS_WEBHOOK_URL) { 'Set' } else { 'Not set' })"
Write-Host "DISCORD_WEBHOOK_URL: $(if ($env:DISCORD_WEBHOOK_URL) { 'Set' } else { 'Not set' })"
Write-Host "---"
& $py app.py
