# Smile

Someone types a name and a kind line, chooses Public or Private, and other people can read, like, and save the public lines.

## How the data is stored

This is the semi-structured pattern from the Data Warehousing badge. Each share is one JSON document in a `VARIANT` column. You read a field with colon notation and cast it.

A new name is stored once in `smile_users`. `smile_user_seq` assigns the user id. That id stays in the database. The page shows the words.

A word is stored once, under `word_name`, in `smile_dictionary`. The same word from another person uses that same name.

Each share is a row in `smile_entries`. The document lives in `payload`:

```json
{"user_id": 1, "word_name": "hope", "public": true, "likes": 0}
```

```sql
SELECT payload
FROM smile_app_db.public.smile_entries;

SELECT
  payload:word_name::STRING AS word_name,
  payload:public::BOOLEAN AS is_public,
  payload:likes::NUMBER AS likes
FROM smile_app_db.public.smile_entries;
```

A saved line is a row in `smile_kept`.

If these tables already exist, run `sql/words.sql` in Snowsight as `ACCOUNTADMIN`. Do not commit `.streamlit/secrets.toml`.
