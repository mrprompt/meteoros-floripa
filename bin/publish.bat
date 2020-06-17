@echo off

cd /d %~1

git pull origin master

python ./bin/make-posts.py
python ./bin/make-stats.py

git add .
git commit -am "captures!"
git push origin master
