SET PROJECT_NAME=guga
SET PGHOST=localhost
SET PGPORT=5437
SET PGDATABASE=%PROJECT_NAME%
SET PGUSER=postgres
SET PGPASSWORD=postgres


REM find last dump file
FOR /f "tokens=*" %%a IN ('dir /b /od *.pgdump') DO SET last_dump=%%a
IF [%last_dump%] == [] GOTO exit
ECHO  closing all connections
psql -d %PGDATABASE% -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid <> pg_backend_pid() AND datname = '%PGDATABASE%';"

REM drop existing database
psql -d postgres -c "DROP DATABASE IF EXISTS %PGDATABASE%;"

psql -d postgres -c "CREATE DATABASE %PGDATABASE%;"
REM IF %ERRORLEVEL% NEQ 0 goto error
ECHO Restoring database %PGDATABASE% from dump: %last_dump%
pg_restore -d %PROJECT_NAME% %last_dump%
ECHO restore user rights
REM psql -d %PGDATABASE% -c "GRANT CONNECT ON DATABASE %PGDATABASE% TO %PROJECT_NAME%;"
REM psql -d %PGDATABASE% -c "GRANT ALL PRIVILEGES ON SCHEMA public TO %PROJECT_NAME%;"
REM psql -d %PGDATABASE% -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA "public" TO %PROJECT_NAME%;"
REM psql -d %PGDATABASE% -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA "public" TO %PROJECT_NAME%;"
REM psql -d %PGDATABASE% -c "GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA "public" TO %PROJECT_NAME%;"

goto exit
:error
echo error
:exit