@echo off

setlocal
    set "sourcefolder=%~1"

    cd /d "%sourcefolder%"

    git pull origin master

    python ./.bin/make-posts.py "d:" "e:" "f:" 2 "TLP"
    python ./.bin/make-stats.py

    git add .
    git commit -am "captures!"
    git push origin master
endlocal
