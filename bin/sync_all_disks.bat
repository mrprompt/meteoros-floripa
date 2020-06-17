@echo off

setlocal
    for %%d in (D E F) do (
        start sync_disk.bat "%%d:\"
    )
endlocal
