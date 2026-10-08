<#
.SYNOPSIS
    Installs the pgvector extension into a Windows PostgreSQL 16 installation.

.DESCRIPTION
    Windows builds of PostgreSQL do not ship pgvector and there is no official
    prebuilt installer. This script drops a prebuilt pgvector build (vector.dll,
    the SQL/control files and headers) into the PostgreSQL tree.

    It requires Administrator rights because it writes to C:\Program Files.

.PARAMETER PgRoot
    Root of the PostgreSQL installation (default: C:\Program Files\PostgreSQL\16).

.PARAMETER SourceDir
    Directory that contains the extracted pgvector build (must contain lib\vector.dll
    and share\extension\*). If omitted the script downloads the pinned build.

.PARAMETER Version
    pgvector version to download when SourceDir is not supplied.
#>
[CmdletBinding()]
param(
    [string]$PgRoot = "C:\Program Files\PostgreSQL\16",
    [string]$SourceDir = "",
    [string]$Version = "0.8.6",
    [string]$PgMajor = "16"
)

$ErrorActionPreference = "Stop"
$logPath = Join-Path $env:TEMP "pgvector_install.log"
Start-Transcript -Path $logPath -Force | Out-Null

function Write-Step($msg) { Write-Host "[pgvector] $msg" }

try {
    if (-not (Test-Path $PgRoot)) {
        throw "PostgreSQL root not found: $PgRoot"
    }

    if ([string]::IsNullOrWhiteSpace($SourceDir)) {
        $tag = "$Version`_$PgMajor"
        $url = "https://github.com/andreiramani/pgvector_pgsql_windows/releases/download/$tag/vector.v$Version-pg$PgMajor.zip"
        $work = Join-Path $env:TEMP "pgvector_dl"
        New-Item -ItemType Directory -Force -Path $work | Out-Null
        $zip = Join-Path $work "vector.zip"
        Write-Step "Downloading $url"
        curl.exe -sL $url -o $zip | Out-Null
        if (-not (Test-Path $zip)) { throw "Download failed: $url" }
        $SourceDir = Join-Path $work "extracted"
        if (Test-Path $SourceDir) { Remove-Item -Recurse -Force $SourceDir }
        Expand-Archive -Force $zip $SourceDir
    }

    $dll = Join-Path $SourceDir "lib\vector.dll"
    if (-not (Test-Path $dll)) { throw "vector.dll not found under $SourceDir\lib" }

    Write-Step "Copying vector.dll -> $PgRoot\lib"
    Copy-Item -Force $dll (Join-Path $PgRoot "lib")

    Write-Step "Copying extension SQL/control -> $PgRoot\share\extension"
    Copy-Item -Force (Join-Path $SourceDir "share\extension\*") (Join-Path $PgRoot "share\extension")

    $incSrc = Join-Path $SourceDir "include\server\extension\vector"
    if (Test-Path $incSrc) {
        $incDst = Join-Path $PgRoot "include\server\extension\vector"
        New-Item -ItemType Directory -Force -Path $incDst | Out-Null
        Copy-Item -Force (Join-Path $incSrc "*") $incDst
    }

    Write-Step "Verifying"
    if (-not (Test-Path (Join-Path $PgRoot "lib\vector.dll"))) { throw "vector.dll missing after copy" }
    if (-not (Test-Path (Join-Path $PgRoot "share\extension\vector.control"))) { throw "vector.control missing after copy" }

    Write-Step "OK - pgvector $Version installed into $PgRoot"
    Write-Output "PGVECTOR_INSTALL_OK"
}
catch {
    Write-Error $_.Exception.Message
    Write-Output "PGVECTOR_INSTALL_FAILED"
    exit 1
}
finally {
    Stop-Transcript | Out-Null
}
