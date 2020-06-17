@echo off

cd /d %~dp0

git pull origin master

python ./bin/make-posts.py
python ./bin/make-stats.py

git add .
git commit -am "captures of %date%!"
git push origin master
