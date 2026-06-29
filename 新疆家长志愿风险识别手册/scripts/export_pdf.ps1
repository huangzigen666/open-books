$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if (-not (Test-Path -Path $edge)) {
    $edge = "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
}
if (-not (Test-Path -Path $edge)) {
    throw "Microsoft Edge executable not found"
}

$html = Join-Path $root "dist\index.html"
$pdf = Join-Path $root "dist\book.pdf"
$profile = Join-Path $env:TEMP ("codex-edge-profile-" + [guid]::NewGuid().ToString("N"))

if (-not (Test-Path -Path $html)) {
    throw "HTML not found: $html. Run scripts\build_publish.py first."
}
if (Test-Path -Path $pdf) {
    Remove-Item -Path $pdf -Force
}

$uri = (New-Object System.Uri($html)).AbsoluteUri
$args = @(
    "--headless=new",
    "--disable-gpu",
    "--disable-extensions",
    "--no-first-run",
    "--no-default-browser-check",
    "--no-pdf-header-footer",
    "--user-data-dir=$profile",
    "--print-to-pdf=$pdf",
    $uri
)

try {
    $process = Start-Process -FilePath $edge -ArgumentList $args -Wait -PassThru -WindowStyle Hidden
    if (-not (Test-Path -Path $pdf)) {
        throw "PDF was not created; Edge exit code $($process.ExitCode)"
    }
    Get-Item -Path $pdf | Select-Object FullName, Length, LastWriteTime | Format-List
}
finally {
    if (Test-Path -Path $profile) {
        Remove-Item -Path $profile -Recurse -Force -ErrorAction SilentlyContinue
    }
}
