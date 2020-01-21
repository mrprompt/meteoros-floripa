# Meteoros Floripa - Site


## Running local

```console
docker-compose up
```

## The publish script

Read the stations captures stored in the S3 bucket and create the collections to be used from Jekyll/GitHub Pages.

Captures are grouped by station ID and date.

This script clone the repository used by GitHub-pages, create a work branch, make the collections and posts to be 
read by Jekyll, they will merge the new branch and commit directly to the production branch - aka master.

The project will be cloned to a temporary directory and removed at the finish.

The `Git` executable must be present at the PATH.
