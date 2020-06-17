@echo off

cd /d %~dp0
cd ..
del _captures/*.md
del _stations/*.md
del _posts/*.md
del _watches/*.md

python ./bin/make-posts.py
python ./bin/make-stats.py
