# Vespa

The SuperWASP **V**ariabl**e** **S**tar **P**hotometry **A**rchive.

## Running Locally

You can run the latest build of the `main` branch in Docker with:

```
docker pull ghcr.io/ou-escape-eco/vespa
docker run -it --rm -p 8080:8080 ghcr.io/ou-escape-eco/vespa
```

This will run the Django dev server backed by a SQLite database.

You can also use docker-compose:

```
docker-compose build && docker-compose up
```

Or without Docker, install Pipenv in you Python environment and run:

```
pipenv install
./start_server.sh
```

## Data Import

There are three management commands for importing data:

* `python manage.py importclassifications class_top.dat` -- this must be run first. It will create database entries for all non-junk classifications.
* `python manage.py importlightcurves results_total.dat` -- this imports metadata about the period folding (skipping any records which don't already have database entries).
* `python manage.py importzooniverse superwasp-variable-stars-subjects.csv` -- this imports Zooniverse metadata (skipping any records which don't already have database entries).
