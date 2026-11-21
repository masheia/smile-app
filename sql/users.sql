-- Run this once in Snowsight as ACCOUNTADMIN.
-- A new name receives the next value from smile_user_seq.

USE ROLE ACCOUNTADMIN;

CREATE SEQUENCE IF NOT EXISTS smile_app_db.public.smile_user_seq
  START = 1
  INCREMENT = 1;

CREATE TABLE IF NOT EXISTS smile_app_db.public.smile_users (
  user_id NUMBER,
  created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  name STRING UNIQUE
);

GRANT USAGE ON SEQUENCE smile_app_db.public.smile_user_seq TO ROLE smile_app_role;
GRANT INSERT, SELECT ON TABLE smile_app_db.public.smile_users TO ROLE smile_app_role;
