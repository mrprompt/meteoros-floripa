@echo off 

setlocal
    set "sourcefolder=%~1"

    for /R "%sourcefolder%" %%a in (*.avi) do (
        set "sourcefile=%%~fa"
        set "sourcepath=%%~dpa"
        set "targetfile=%%~na.mp4"

        setlocal enabledelayedexpansion
            c:\bramon\tools\ffmpeg -n -i "!sourcefile!" -c:v libx264 -profile:v baseline -level 3.0 -pix_fmt yuv420p "!sourcepath!!targetfile!"
        endlocal
    )
endlocal
