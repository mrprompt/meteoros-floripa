@echo off

cd /d %~1
aws s3 sync . s3://meteoros/ --exclude "*$RECYCLE.BIN*" --exclude "*Backups*" --exclude "*WindowsImageBackup*" --exclude "*Boot*"
exit
