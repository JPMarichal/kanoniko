# Engine Isolation - Startup Fix
# Runs at user logon to ensure Rancher Desktop and Podman Desktop remain isolated.
# Prevents the "docker_engine pipe race" where Podman Desktop steals RD's pipe on boot.

param(
    [switch]$Force,
    [switch]$Silent
)

$ErrorActionPreference = 'SilentlyContinue'
$ProgressPreference = 'SilentlyContinue'

function Write-Status($msg) {
    if (-not $Silent) { Write-Host $msg }
}

# Step 1: Stop Podman Desktop remnants if they're running
$pdRunning = Get-Process -Name "Podman Desktop","win-sshproxy","podman" -ErrorAction SilentlyContinue
if ($pdRunning) {
    Write-Status "[EngineIsolation] Stopping Podman Desktop remnants..."
    Stop-Process -Name "Podman Desktop","win-sshproxy","podman" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
}

# Step 2: Ensure Rancher Desktop owns docker_engine pipe
$rdRunning = Get-Process -Name "Rancher Desktop" -ErrorAction SilentlyContinue
$pipeExists = Test-Path "\\.\pipe\docker_engine"

if (-not $rdRunning -or -not $pipeExists) {
    Write-Status "[EngineIsolation] Rancher Desktop not running or pipe missing. Starting RD..."
    if ($rdRunning) {
        Stop-Process -Name "Rancher Desktop" -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
    }
    Start-Process "C:\Program Files\Rancher Desktop\Rancher Desktop.exe"
    Start-Sleep -Seconds 10
}

# Step 3: Verify docker_engine serves RD
$env:DOCKER_HOST = "npipe:////./pipe/docker_engine"
try {
    $info = docker info --format "{{.Name}} {{.OperatingSystem}} {{.ServerVersion}}" 2>$null
    if ($info -match "Rancher Desktop") {
        Write-Status "[EngineIsolation] docker_engine pipe correctly serves Rancher Desktop."
    } else {
        Write-Status "[EngineIsolation] WARNING: docker_engine does not serve RD. Current: $info"
    }
} catch {
    Write-Status "[EngineIsolation] WARNING: Cannot reach docker_engine pipe."
}

# Step 4: Force Podman Desktop context to SSH (prevents it from claiming docker_engine)
$pdContextPath = "$env:LOCALAPPDATA\Programs\Podman Desktop\contexts\meta\f2ee66de448cc35da4348bada82ac5aacea03097c000faf88749fb7f038572f1\meta.json"
if (Test-Path $pdContextPath) {
    $content = Get-Content $pdContextPath -Raw
    if ($content -match 'npipe:////./pipe/docker_engine') {
        Write-Status "[EngineIsolation] Correcting Podman Desktop context to SSH..."
        $content = $content -replace 'npipe:////./pipe/docker_engine','ssh://user@127.0.0.1:53064/run/user/1000/podman/podman.sock'
        Set-Content -Path $pdContextPath -Value $content -Encoding UTF8
    }
}

# Step 5: Clear DOCKER_HOST from user environment
$currentHost = [System.Environment]::GetEnvironmentVariable("DOCKER_HOST","User")
if ($currentHost) {
    Write-Status "[EngineIsolation] Clearing DOCKER_HOST from user environment..."
    [System.Environment]::SetEnvironmentVariable("DOCKER_HOST",$null,"User")
}

# Step 6: Set docker default context to rd-pipe
docker context use rd-pipe 2>$null | Out-Null

# Step 7: Verify isolation
Write-Status "[EngineIsolation] === Verification ==="
try {
    $rdContainers = docker --context rd-pipe ps -a --format "{{.Names}}" 2>$null
    $ownInRd = $rdContainers | Where-Object { $_ -match "wp_bc|alejandria|ccm-system" }
    if ($ownInRd) {
        Write-Status "[EngineIsolation] WARNING: own containers detected in RD!"
    } else {
        Write-Status "[EngineIsolation] RD correctly shows only C:\git containers."
    }
} catch {
    Write-Status "[EngineIsolation] Could not verify RD containers."
}

try {
    $podmanContainers = docker --context podman-machine-default ps -a --format "{{.Names}}" 2>$null
    $gitInPodman = $podmanContainers | Where-Object { $_ -match "web-shim|sso-api|mysql|k8s_" }
    if ($gitInPodman) {
        Write-Status "[EngineIsolation] WARNING: git containers detected in Podman!"
    } else {
        Write-Status "[EngineIsolation] Podman correctly shows only C:\own containers."
    }
} catch {
    Write-Status "[EngineIsolation] Could not verify Podman containers."
}

Write-Status "[EngineIsolation] Startup fix complete."
