@echo off

setlocal
set "sourcefolder=%~1"

cd /d "%sourcefolder%"

python ./.bin/make-posts.py
python ./.bin/make-stats.py

git add .
git commit -am "captures!"
git pull origin master --rebase
git push origin master
