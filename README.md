# Smile

A public page where a person leaves a kind line and chooses public or private. Public lines are what other people read. A like adds one to the count. A name brings back the lines that person saved.

Each line is stored as JSON in a `VARIANT` column. Visitors do not need a Snowflake login. Cortex is not used. The app user can insert, select, and update `smile_words`, and insert or select on `smile_saves`. A resource monitor stops that warehouse at 5 credits in a month.

If you already ran `sql/setup.sql` before `smile_saves` existed, run `sql/community.sql` as `ACCOUNTADMIN`.

After a test submission, this shows the stored JSON:

```sql
SELECT payload:text::STRING, payload:public::BOOLEAN, payload:likes::NUMBER
FROM smile_app_db.public.smile_words;
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

That local URL is only on your computer.

## Give everyone the link

1. Push this folder to a public GitHub repository. Do not push `secrets.toml` or a setup script that still contains the real password.
2. Sign in at [share.streamlit.io](https://share.streamlit.io) and create an app from that repository. The main file is `streamlit_app.py`.
3. In the app settings, open Secrets and paste the contents of your filled-in `secrets.toml`.
4. Deploy. Streamlit gives you a public `streamlit.app` URL. That is the link for LinkedIn.

## What people can and cannot do

Visitors can type a word and read the sentence on their own screen. The Snowflake role has `INSERT` and `SELECT` on this table only. It cannot create objects, drop the table, or use your other databases.

Words that mention job, family, or money are not shown to the next visitor. If the page is being filled with junk, suspend `SMILE_APP_USER` in Snowsight. The warehouse also suspends itself when the 5-credit monitor is reached.
