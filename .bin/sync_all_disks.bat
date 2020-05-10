@echo off

setlocal

for %%d in (D E) do (
    start sync.bat "%%d:\"
)

endlocal
