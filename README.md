# Vespa

The SuperWASP __V__ariabl__e__ __S__tar __P__hotometry __A__rchive.

## Data Import

There are three management commands for importing data:

* `python manage.py importclassifications class_top.dat` -- this must be run first. It will create database entries for all non-junk classifications.
* `python manage.py importlightcurves results_total.dat` -- this imports metadata about the period folding (skipping any records which don't already have database entries).
* `python manage.py importzooniverse superwasp-variable-stars-subjects.csv` -- this imports Zooniverse metadata (skipping any records which don't already have database entries).
