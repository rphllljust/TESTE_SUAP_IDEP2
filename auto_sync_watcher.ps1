$ErrorActionPreference = 'Stop'

Set-Location $PSScriptRoot
$host.UI.RawUI.WindowTitle = 'SUAP Auto Sync GitHub'

$repoRoot = (Get-Location).Path
$ignoredPatterns = @(
    '\\.git\\',
    '\\__pycache__\\',
    '\\.venv\\',
    '\\venv\\',
    'db.sqlite3',
    '.log',
    '.pyc'
)

$script:pending = $false
$script:lastEvent = Get-Date
$script:syncing = $false

function Test-IgnoredPath {
    param([string]$Path)

    foreach ($pattern in $ignoredPatterns) {
        if ($Path -like "*$pattern*") {
            return $true
        }
    }
    return $false
}

function Queue-Sync {
    param($Source, $EventArgs)

    $fullPath = ''
    if ($EventArgs -and $EventArgs.PSObject.Properties['FullPath']) {
        $fullPath = $EventArgs.FullPath
    }

    if ($fullPath -and (Test-IgnoredPath -Path $fullPath)) {
        return
    }

    $script:pending = $true
    $script:lastEvent = Get-Date
}

function Invoke-AutoSync {
    if ($script:syncing) {
        return
    }

    $script:syncing = $true
    try {
        Set-Location $repoRoot
        git add . | Out-Null
        $changes = git status --porcelain
        if (-not $changes) {
            return
        }

        $stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
        git commit -m "Auto-sync: $stamp" | Out-Null
        git push origin main | Out-Null
        Write-Host "[$stamp] Alteracoes sincronizadas com GitHub." -ForegroundColor Green
    }
    catch {
        Write-Host "Falha no auto-sync: $($_.Exception.Message)" -ForegroundColor Red
    }
    finally {
        $script:syncing = $false
    }
}

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $repoRoot
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true
$watcher.NotifyFilter = [System.IO.NotifyFilters]'FileName, DirectoryName, LastWrite, CreationTime'
$watcher.Filter = '*.*'

$created = Register-ObjectEvent $watcher Created -Action { Queue-Sync $Sender $EventArgs }
$changed = Register-ObjectEvent $watcher Changed -Action { Queue-Sync $Sender $EventArgs }
$deleted = Register-ObjectEvent $watcher Deleted -Action { Queue-Sync $Sender $EventArgs }
$renamed = Register-ObjectEvent $watcher Renamed -Action { Queue-Sync $Sender $EventArgs }

Write-Host 'Auto-sync do GitHub ativo. Deixe esta janela aberta.' -ForegroundColor Cyan
Write-Host 'Repositorio: ' $repoRoot

try {
    while ($true) {
        Start-Sleep -Milliseconds 1200
        if ($script:pending) {
            $elapsed = (Get-Date) - $script:lastEvent
            if ($elapsed.TotalSeconds -ge 3) {
                $script:pending = $false
                Invoke-AutoSync
            }
        }
    }
}
finally {
    Unregister-Event -SourceIdentifier $created.Name -ErrorAction SilentlyContinue
    Unregister-Event -SourceIdentifier $changed.Name -ErrorAction SilentlyContinue
    Unregister-Event -SourceIdentifier $deleted.Name -ErrorAction SilentlyContinue
    Unregister-Event -SourceIdentifier $renamed.Name -ErrorAction SilentlyContinue
    $watcher.Dispose()
}
