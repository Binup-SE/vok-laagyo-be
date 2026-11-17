-- Local Postgres bootstrap for Vok Laagyo.
-- Run as superuser (postgres) against the default "postgres" database.
-- Safe to re-run: skips role/DB if they already exist.

DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'vok') THEN
    CREATE ROLE vok LOGIN PASSWORD 'vok';
  END IF;
END
$$;

SELECT 'CREATE DATABASE vok_laagyo OWNER vok'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'vok_laagyo')\gexec
