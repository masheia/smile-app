-- Run this once in Snowsight as ACCOUNTADMIN.
-- Replace the password on the CREATE USER line before you run it.
-- Do not commit a copy of this file that contains the real password.

USE ROLE ACCOUNTADMIN;

CREATE RESOURCE MONITOR IF NOT EXISTS smile_app_monitor
  WITH CREDIT_QUOTA = 5
       FREQUENCY = MONTHLY
       START_TIMESTAMP = IMMEDIATELY
       TRIGGERS
         ON 80 PERCENT DO NOTIFY
         ON 100 PERCENT DO SUSPEND_IMMEDIATE;

CREATE WAREHOUSE IF NOT EXISTS smile_app_wh
  WAREHOUSE_SIZE = XSMALL
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  RESOURCE_MONITOR = smile_app_monitor;

CREATE DATABASE IF NOT EXISTS smile_app_db;
CREATE SCHEMA IF NOT EXISTS smile_app_db.public;

CREATE SEQUENCE IF NOT EXISTS smile_app_db.public.smile_user_seq
  START = 1
  INCREMENT = 1;

CREATE TABLE IF NOT EXISTS smile_app_db.public.smile_users (
  user_id NUMBER,
  created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  name STRING UNIQUE
);

CREATE TABLE IF NOT EXISTS smile_app_db.public.smile_words (
  event_id NUMBER IDENTITY,
  created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  payload VARIANT
);

CREATE ROLE IF NOT EXISTS smile_app_role;

GRANT USAGE ON WAREHOUSE smile_app_wh TO ROLE smile_app_role;
GRANT USAGE ON DATABASE smile_app_db TO ROLE smile_app_role;
GRANT USAGE ON SCHEMA smile_app_db.public TO ROLE smile_app_role;
GRANT INSERT, SELECT, UPDATE ON TABLE smile_app_db.public.smile_words TO ROLE smile_app_role;
GRANT USAGE ON SEQUENCE smile_app_db.public.smile_user_seq TO ROLE smile_app_role;
GRANT INSERT, SELECT ON TABLE smile_app_db.public.smile_users TO ROLE smile_app_role;

CREATE TABLE IF NOT EXISTS smile_app_db.public.smile_dictionary (
  word_name STRING,
  word_key STRING UNIQUE
);

CREATE TABLE IF NOT EXISTS smile_app_db.public.smile_entries (
  entry_id NUMBER IDENTITY,
  created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  payload VARIANT
);

CREATE TABLE IF NOT EXISTS smile_app_db.public.smile_kept (
  user_id NUMBER,
  entry_id NUMBER,
  created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  UNIQUE (user_id, entry_id)
);

GRANT INSERT, SELECT ON TABLE smile_app_db.public.smile_dictionary TO ROLE smile_app_role;
GRANT INSERT, SELECT, UPDATE ON TABLE smile_app_db.public.smile_entries TO ROLE smile_app_role;
GRANT INSERT, SELECT ON TABLE smile_app_db.public.smile_kept TO ROLE smile_app_role;

CREATE TABLE IF NOT EXISTS smile_app_db.public.smile_saves (
  save_id NUMBER IDENTITY,
  created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  payload VARIANT
);

GRANT INSERT, SELECT ON TABLE smile_app_db.public.smile_saves TO ROLE smile_app_role;

-- Pick a long password here. This role can only insert and read smile_words.
CREATE USER IF NOT EXISTS smile_app_user
  PASSWORD = 'CHANGE_ME_BEFORE_RUNNING'
  DEFAULT_ROLE = smile_app_role
  DEFAULT_WAREHOUSE = smile_app_wh
  DEFAULT_NAMESPACE = smile_app_db.public
  MUST_CHANGE_PASSWORD = FALSE;

GRANT ROLE smile_app_role TO USER smile_app_user;
