FROM postgres:16

COPY /postgres/create_tables.sql /docker-entrypoint-initdb.d/20-create_tables.sql
COPY /postgres/seed_data.sql /docker-entrypoint-initdb.d/30-seed_test_data.sql

RUN chmod a+r /docker-entrypoint-initdb.d/*