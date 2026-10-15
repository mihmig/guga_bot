#!/bin/bash
export PROJECT_NAME=guga
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=$PROJECT_NAME
export PGUSER=postgres
export PGPASSWORD=postgres
export DUMP=$PGDATABASE_`date '+%Y-%m-%d'`.pgdump

pg_dump -c -C --if-exists -F c -v -d $PGDATABASE -f $DUMP

