# Smile

A public page where a person types a name and a kind line, then chooses Public or Private. Other people read the public lines, like them, and save them to revisit.

Visitors do not get a Snowflake login. The page uses one restricted user. A new name receives a user id from `smile_user_seq`. The same name keeps that id. The same word, ignoring case, is stored once in `smile_dictionary` under `word_name`. Each share in `smile_entries` stores that word name. A save is a row in `smile_kept`. The page shows the words. The user id stays in Snowflake.

Cortex is not used. A resource monitor stops the warehouse at 5 credits in a month.

If you already ran an older `sql/setup.sql`, run `sql/users.sql` and `sql/words.sql` in Snowsight as `ACCOUNTADMIN`.

After a test share, look in the database:

```sql
SELECT user_id, name FROM smile_app_db.public.smile_users ORDER BY user_id;
SELECT word_name FROM smile_app_db.public.smile_dictionary ORDER BY word_name;
SELECT entry_id, user_id, word_name, is_public, likes
FROM smile_app_db.public.smile_entries ORDER BY entry_id;
```

## One-time Snowflake setup

1. Open `sql/setup.sql`.
2. Replace `CHANGE_ME_BEFORE_RUNNING` with a long password.
3. Run the script in Snowsight as `ACCOUNTADMIN`.
4. Leave the password out of git. The copy in the repo must keep the placeholder.

The account value for the app is the identifier Snowsight shows under the account menu, usually `ORGNAME-ACCOUNTNAME`.

## Run it on your machine

```text
cd smile-app
py -3.12 -m venv .venv312
.venv312\Scripts\activate
pip install -r requirements.txt
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
```

Fill in `.streamlit/secrets.toml`, then:

```text
streamlit run streamlit_app.py
```

Use Python 3.12. That local URL is only on your computer.

## Give everyone the link

1. Push this folder to a public GitHub repository. Do not push `secrets.toml` or a setup script that still contains the real password.
2. Sign in at [share.streamlit.io](https://share.streamlit.io) and create an app from that repository. Branch `master`. Main file `streamlit_app.py`. Python 3.12.
3. In Advanced settings, open Secrets and paste the contents of your filled-in `secrets.toml`.
4. Deploy. Streamlit gives you a public `streamlit.app` URL. That is the link for LinkedIn.

## What people can and cannot do

Visitors type a name and a line. Public lines appear for the next visitor. The Snowflake role can insert, select, and update the Smile tables. It cannot create objects, drop tables, or use your other databases.

The typed name is a lookup key, not a password. Anyone who types the same name sees the lines saved under that name. If the page is being filled with junk, suspend `SMILE_APP_USER` in Snowsight. The warehouse also suspends itself when the 5-credit monitor is reached.
