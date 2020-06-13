@echo off

setlocal
    set "sourcefolder=%~1"

    cd /d "%sourcefolder%"

    git pull origin master

    REM python ./.bin/make-analyzers.py "d:" "e:" "f:"
    python ./.bin/make-posts.py
    python ./.bin/make-stats.py

    git add .
    git commit -am "captures!"
    git pull origin master --rebase
    git push origin master
endlocal
