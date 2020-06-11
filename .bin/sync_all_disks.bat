@echo off

setlocal
    for %%d in (D E F) do (
        start sync.bat "%%d:\"
    )
endlocal
