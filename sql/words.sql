-- Run this once in Snowsight as ACCOUNTADMIN.
-- Each share is JSON in a VARIANT column. The word name is stored once.
-- This replaces the share tables, so earlier test shares are cleared.
-- Names already stored in smile_users are kept.

USE ROLE ACCOUNTADMIN;

DROP TABLE IF EXISTS smile_app_db.public.smile_kept;
DROP TABLE IF EXISTS smile_app_db.public.smile_entries;
DROP TABLE IF EXISTS smile_app_db.public.smile_dictionary;

CREATE TABLE smile_app_db.public.smile_dictionary (
  word_name STRING,
  word_key STRING UNIQUE
);

CREATE TABLE smile_app_db.public.smile_entries (
  entry_id NUMBER IDENTITY,
  created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  payload VARIANT
);

CREATE TABLE smile_app_db.public.smile_kept (
  user_id NUMBER,
  entry_id NUMBER,
  created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  UNIQUE (user_id, entry_id)
);

GRANT INSERT, SELECT ON TABLE smile_app_db.public.smile_dictionary TO ROLE smile_app_role;
GRANT INSERT, SELECT, UPDATE ON TABLE smile_app_db.public.smile_entries TO ROLE smile_app_role;
GRANT INSERT, SELECT ON TABLE smile_app_db.public.smile_kept TO ROLE smile_app_role;
