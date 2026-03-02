Start-Process -FilePath powershell.exe -ArgumentList '-NoExit','-NoProfile','-ExecutionPolicy','Bypass','-File',"$PSScriptRoot\\auto_sync_watcher.ps1"
