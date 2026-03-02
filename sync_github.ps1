param(
    [string]$Message = 'Atualizacao automatica do projeto SUAP'
)

Set-Location $PSScriptRoot

git add .
$changes = git status --porcelain
if (-not $changes) {
    Write-Output 'Sem alterações para enviar.'
    exit 0
}

git commit -m $Message
git push origin main
