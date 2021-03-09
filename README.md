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

## VPS Services

This is deployed on a VPS with Podman. Here are the initial commands used to set up the services:

```
podman pod create --name vespa -p 80:80

podman run -d --restart=always --pod=vespa --name vespa-postgres --label "io.containers.autoupdate=image" -v /opt/vespa/psql:/var/lib/postgresql/data:z --env-file /opt/vespa/postgres.env docker.io/postgres:13.1

podman run -d --restart=always --pod=vespa --name vespa-nginx --label "io.containers.autoupdate=image" -v /opt/vespa/nginx.conf:/etc/nginx/nginx.conf:ro -v /opt/vespa/static/:/opt/vespa/static:z docker.io/nginx:1

podman run -d --restart=always --pod=vespa --name=vespa-django --label "io.containers.autoupdate=image"  --env-file /opt/vespa/prod.env -v /opt/vespa/static:/opt/vespa/static:z ghcr.io/ou-escape-eco/vespa

cd /etc/systemd/system

podman generate systemd --new -f vespa

systemctl daemon-reload
systemctl enable pod-2e9f36b88b26480ea7d704970d85f9794b7defaa9b26c766996de3a4ed5db309.service
systemctl start pod-2e9f36b88b26480ea7d704970d85f9794b7defaa9b26c766996de3a4ed5db309.service
```