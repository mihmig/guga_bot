#!/bin/bash
export PROJECT_NAME=guga
export PGDATABASE=$PROJECT_NAME
export last_dump=`ls -tr *.pgdump|tail -1`

echo closing all connections
psql -d $PGDATABASE -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid <> pg_backend_pid() AND datname = '$PGDATABASE';"

#echo clear all data...
#psql -d $PGDATABASE -c "DROP SCHEMA public CASCADE;"
psql -d postgres -c "DROP DATABASE IF EXISTS $PGDATABASE;"
psql -d postgres -c "CREATE DATABASE $PGDATABASE;"

echo Restoring database $PGDATABASE from dump: $last_dump ...
pg_restore -d $PGDATABASE $last_dump

echo DONE!
