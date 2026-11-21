# Smile

Sometimes one kind sentence is enough to get someone through the day.

Smile is a small public page where a person types a name and a kind line, then chooses Public or Private. Other people can read the public lines, like them, and save the ones they want to see again.

## What you can do

- **Share a line.** Write something kind, then choose who can read it.
- **Read public lines.** See the lines other people marked Public.
- **Like a line.** Add one to the count when a message stays with you.
- **Keep a line.** Save it under the name you typed, so you can open it again.

A name is typed on the page. There is no sign-up. `smile_user_seq` assigns a user id, and that same name keeps the same id. The page shows the words. The id stays in Snowflake.

## How a share is stored

Each share is one JSON document in a Snowflake `VARIANT` column. That is the semi-structured pattern from the Data Warehousing badge: store the document, then read a field with colon notation.

```json
{
  "user_id": 1,
  "word_name": "hope",
  "public": true,
  "likes": 0
}
```

`word_name` is the line that was typed. The same word, ignoring case, is stored once in `smile_dictionary`. Another person who types it uses that same name.

```sql
SELECT payload
FROM smile_app_db.public.smile_entries;

SELECT
  payload:word_name::STRING AS word_name,
  payload:public::BOOLEAN AS is_public,
  payload:likes::NUMBER AS likes
FROM smile_app_db.public.smile_entries;
```

## Tech

| Technology | Purpose |
|---|---|
| Snowflake | Stores the names, the word names, and each share |
| SQL | Creates the objects and reads the JSON fields |
| VARIANT | Holds each share as JSON |
| Python | Runs the page logic |
| Streamlit | The page people use |

## Tables

| Table | What it holds |
|---|---|
| `smile_users` | The typed name and the user id from `smile_user_seq` |
| `smile_dictionary` | Each distinct word name, stored once |
| `smile_entries` | One row per share, with the JSON in `payload` |
| `smile_kept` | The lines a name has saved |

## Public and private

Public and private is a field in the JSON. The page lists only the rows where `public` is true. A private line is still in `smile_entries`. The app role can read every row. It can insert and update the Smile tables, and it cannot create objects or use your other databases.

If these tables already exist, run `sql/words.sql` in Snowsight as `ACCOUNTADMIN`. Leave `.streamlit/secrets.toml` out of git.

Leave a word. Find a word. Keep a word.
