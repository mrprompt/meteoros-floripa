@echo off

setlocal
    set "sourcefolder=%~1"
    cd /d "%sourcefolder%"
    aws s3 sync . s3://meteoros/ --exclude "*$RECYCLE.BIN*" --exclude "*Backups*" --exclude "*WindowsImageBackup*" --exclude "*Boot*"
    exit
endlocal
