# Instância local de demonstração. Sem instalação global ou alteração persistente de PATH.
param([string[]]$N8nArguments = @('start'))
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Push-Location $projectRoot
try {
    $npxCli = Join-Path $projectRoot '.local-tools/npm/package/bin/npx-cli.js'
    if (-not (Test-Path -LiteralPath $npxCli)) {
        throw 'npm local ausente. Consulte docs/N8N_VALIDATION.md.'
    }
    $env:npm_config_cache = Join-Path $projectRoot '.npm-cache'
    $env:npm_config_prefix = Join-Path $projectRoot '.local-tools/npm-prefix'
    $env:N8N_USER_FOLDER = Join-Path $projectRoot '.n8n-local'
    $env:N8N_LISTEN_ADDRESS = '127.0.0.1'
    $env:N8N_HOST = 'localhost'
    $env:N8N_PORT = '5678'
    $env:N8N_PROTOCOL = 'http'
    $env:N8N_EDITOR_BASE_URL = 'http://localhost:5678'
    $env:GENERIC_TIMEZONE = 'America/Sao_Paulo'
    $env:N8N_DIAGNOSTICS_ENABLED = 'false'
    $env:N8N_VERSION_NOTIFICATIONS_ENABLED = 'false'
    $env:N8N_TEMPLATES_ENABLED = 'false'
    & node $npxCli --yes --allow-scripts=sqlite3 --package=n8n@2.48.4 n8n @N8nArguments
    if ($LASTEXITCODE -ne 0) { throw "n8n encerrou com código $LASTEXITCODE" }
} finally {
    Pop-Location
}
