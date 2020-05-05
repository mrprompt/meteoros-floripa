# Meteoros Floripa - Site

![Build](https://github.com/Meteoros-Floripa/site/workflows/Build/badge.svg)

Captures of [BRAMON](https://www.bramonmeteor.org) [TLP](https://www.mrprompt.com.br) meteor stations.

## Running local

```console
docker-compose up
```

## The make collection script

Read the stations captures stored in the S3 bucket and create the collections to be used from Jekyll/GitHub Pages.

Captures are grouped by station ID and date.

Script actions:

- clone the repository
- create a work branch
- make the collections and posts to be read by Jekyll
- merge the new branch and commit directly to master.

## Site publish

Make collection script is run by [Github Actions](https://help.github.com/en/actions/automating-your-workflow-with-github-actions) 
and need an AWS credentials and a S3 bucket to work.

## Your oun station

If you want to build your own meteor station, send me an [email](mailto:mrprompt+meteor@gmail.com) and I'll be happy 
to help you.

