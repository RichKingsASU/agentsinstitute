<#
.SYNOPSIS
  Agents Institute media engine tasks.
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts/build.ps1 setup
  powershell -ExecutionPolicy Bypass -File scripts/build.ps1 render-video -Episode ep01_mcp_servers
#>
param(
    [Parameter(Mandatory, Position = 0)]
    [ValidateSet('setup', 'test-pipeline', 'render-assets', 'render-video')]
    [string]$Task,
    [string]$Episode = 'ep01_mcp_servers'
)
$ErrorActionPreference = 'Stop'
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

# Pick up tools installed since this shell started (winget edits the registry PATH, not ours).
$env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')

function Invoke-Native { $exe = $args[0]; $rest = @($args | Select-Object -Skip 1); & $exe @rest;if ($LASTEXITCODE) { throw "$exe exited $LASTEXITCODE" } }

function Install-UserFonts([string]$Repo, [string]$Match) {
    $fontDir = "$env:LOCALAPPDATA\Microsoft\Windows\Fonts"
    $tmp = Join-Path $env:TEMP "fonts-$($Repo -replace '/', '-')"
    Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
    Invoke-Native gh release download -R $Repo -p '*.zip' -D $tmp
    Get-ChildItem $tmp -Filter *.zip | ForEach-Object { Expand-Archive $_.FullName -DestinationPath $tmp -Force }
    New-Item -ItemType Directory -Force $fontDir | Out-Null
    Get-ChildItem $tmp -Recurse -Filter *.ttf | Where-Object { $_.FullName -match $Match } | ForEach-Object {
        Copy-Item $_.FullName $fontDir -Force
        New-ItemProperty 'HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts' -Name "$($_.BaseName) (TrueType)" `
            -Value (Join-Path $fontDir $_.Name) -PropertyType String -Force | Out-Null
    }
}

function Test-Toolchain {
    $ok = $true
    foreach ($t in 'mmdc', 'vhs', 'ttyd', 'ffmpeg', 'python', 'node') {
        if (-not (Get-Command $t -ErrorAction SilentlyContinue)) { Write-Host "MISSING  $t" -ForegroundColor Red; $ok = $false }
    }
    $py = [version]((python --version) -replace 'Python ', '')
    $node = [version]((node --version) -replace 'v', '')
    if ($py -lt [version]'3.10') { Write-Host "Python $py < 3.10" -ForegroundColor Red; $ok = $false }
    if ($node -lt [version]'20.0') { Write-Host "Node $node < 20" -ForegroundColor Red; $ok = $false }
    Write-Host "python $py | node $node | mmdc $(mmdc --version) | $(vhs --version) | $((ffmpeg -version)[0])"
    if (-not $ok) { throw 'Toolchain incomplete - run: scripts/build.ps1 setup' }
}

switch ($Task) {
    'setup' {
        $winget = "$env:LOCALAPPDATA\Microsoft\WindowsApps\winget.exe"
        $pkgs = @{ vhs = 'charmbracelet.vhs'; ttyd = 'tsl0922.ttyd'; ffmpeg = 'Gyan.FFmpeg' }
        foreach ($cmd in $pkgs.Keys) {
            if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
                & $winget install -e --id $pkgs[$cmd] --silent --accept-source-agreements --accept-package-agreements
            }
        }
        # Gyan.FFmpeg doesn't always register its PATH alias.
        if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
            $bin = (Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\Gyan.FFmpeg*" -Recurse -Filter ffmpeg.exe | Select-Object -First 1).DirectoryName
            [Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path', 'User') + ";$bin", 'User')
            $env:Path += ";$bin"
        }
        if (-not (Get-Command mmdc -ErrorAction SilentlyContinue)) { Invoke-Native npm install -g '@mermaid-js/mermaid-cli' }
        if (-not (Test-Path "$env:LOCALAPPDATA\Microsoft\Windows\Fonts\JetBrainsMono-Regular.ttf")) {
            Install-UserFonts 'JetBrains/JetBrainsMono' '\\fonts\\ttf\\'
        }
        if (-not (Test-Path "$env:LOCALAPPDATA\Microsoft\Windows\Fonts\InterVariable.ttf")) {
            Install-UserFonts 'rsms/inter' 'InterVariable'
        }
        Invoke-Native python -m pip install --quiet -r requirements.txt
        Push-Location remotion; try { Invoke-Native npm install } finally { Pop-Location }
        Test-Toolchain
    }
    'test-pipeline' {
        Test-Toolchain
        Invoke-Native python pipeline/test_pipeline.py
    }
    'render-assets' {
        Invoke-Native python pipeline/generator.py $Episode
    }
    'render-video' {
        $build = "build\$Episode"
        if (-not (Test-Path "$build\manifest.json")) { Invoke-Native python pipeline/generator.py $Episode }
        $public = "remotion\public\$Episode"
        Remove-Item $public -Recurse -Force -ErrorAction SilentlyContinue
        New-Item -ItemType Directory -Force (Split-Path $public) | Out-Null
        Copy-Item $build $public -Recurse
        New-Item -ItemType Directory -Force out | Out-Null
        Push-Location remotion
        try { Invoke-Native npx remotion render src/index.ts Episode "..\out\$Episode.mp4" "--props=..\$build\manifest.json" }
        finally { Pop-Location }
        Write-Host "-> out\$Episode.mp4"
    }
}
