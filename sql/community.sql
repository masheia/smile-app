-- Run this if you already ran setup.sql before the community tables existed.
-- Run it as ACCOUNTADMIN.

USE ROLE ACCOUNTADMIN;

GRANT INSERT, SELECT, UPDATE ON TABLE smile_app_db.public.smile_words TO ROLE smile_app_role;

CREATE TABLE IF NOT EXISTS smile_app_db.public.smile_saves (
  save_id NUMBER IDENTITY,
  created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
  payload VARIANT
);

GRANT INSERT, SELECT ON TABLE smile_app_db.public.smile_saves TO ROLE smile_app_role;
