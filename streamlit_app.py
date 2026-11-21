import json

import streamlit as st
from snowflake.connector import connect

st.set_page_config(page_title="Smile", layout="centered")
st.title("Smile")
st.write("Leave a kind line. Read the lines other people chose to share.")

REQUIRED_SECRETS = ("account", "user", "password", "role", "warehouse", "database", "schema")


def secrets_ready():
    if "snowflake" not in st.secrets:
        return False
    return all(st.secrets["snowflake"].get(key) for key in REQUIRED_SECRETS)


def open_connection():
    cfg = st.secrets["snowflake"]
    return connect(
        account=cfg["account"],
        user=cfg["user"],
        password=cfg["password"],
        role=cfg["role"],
        warehouse=cfg["warehouse"],
        database=cfg["database"],
        schema=cfg["schema"],
    )


def run(sql, params=None):
    connection = open_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(sql, params or {})
        if cursor.description:
            return cursor.fetchall()
        return []
    finally:
        connection.close()


if "liked" not in st.session_state:
    st.session_state.liked = []

name = st.text_input("Your name", max_chars=40, placeholder="Same name brings back the lines you saved")
st.caption("A name is enough to find your saved lines. It is not a password.")

with st.form("share", clear_on_submit=True):
    text = st.text_input("A word, a thought, or some encouragement", max_chars=200)
    share_as = st.radio("Who can read it", ["Public", "Private"], horizontal=True)
    submitted = st.form_submit_button("Share")

if submitted:
    cleaned = " ".join(text.split())[:200]
    if not cleaned:
        st.error("Write something first.")
    elif not secrets_ready():
        st.error("Snowflake is not connected yet.")
    else:
        is_public = share_as == "Public"
        payload = {"text": cleaned, "public": is_public, "likes": 0}
        run(
            "INSERT INTO smile_words (payload) SELECT PARSE_JSON(%(payload)s)",
            {"payload": json.dumps(payload)},
        )
        st.write(f"“{cleaned}”")
        if is_public:
            st.caption("Shared. Other people can read this.")
        else:
            st.caption("Saved for you. Other people cannot read this.")

st.divider()
st.subheader("Shared lines")

if not secrets_ready():
    st.info("Connect Snowflake to see what people have shared.")
else:
    rows = run(
        """
        SELECT
          event_id,
          payload:text::STRING,
          COALESCE(payload:likes::NUMBER, 0)
        FROM smile_words
        WHERE payload:public::BOOLEAN = TRUE
        ORDER BY event_id DESC
        LIMIT 30
        """
    )
    if not rows:
        st.write("Be the first kind line on this page.")

    saved_ids = []
    clean_name = " ".join(name.split())[:40]
    if clean_name:
        saved_rows = run(
            """
            SELECT payload:word_id::NUMBER
            FROM smile_saves
            WHERE payload:name::STRING = %(name)s
            """,
            {"name": clean_name},
        )
        saved_ids = [row[0] for row in saved_rows]

    for event_id, line, likes in rows:
        st.write(f"“{line}”")
        like_col, save_col = st.columns(2)
        already_liked = event_id in st.session_state.liked
        like_label = f"Liked {int(likes)}" if already_liked else f"Like {int(likes)}"
        if like_col.button(like_label, key=f"like-{event_id}", disabled=already_liked):
            run(
                """
                UPDATE smile_words
                SET payload = OBJECT_INSERT(
                  payload,
                  'likes',
                  COALESCE(payload:likes::NUMBER, 0) + 1,
                  TRUE
                )
                WHERE event_id = %(event_id)s
                """,
                {"event_id": event_id},
            )
            st.session_state.liked.append(event_id)
            st.rerun()
        if event_id in saved_ids:
            save_col.write("Saved")
        elif save_col.button("Save", key=f"save-{event_id}"):
            if not clean_name:
                st.warning("Type your name first, then save.")
            else:
                run(
                    "INSERT INTO smile_saves (payload) SELECT PARSE_JSON(%(payload)s)",
                    {"payload": json.dumps({"name": clean_name, "word_id": event_id})},
                )
                st.rerun()

    if clean_name:
        saved_lines = run(
            """
            SELECT w.payload:text::STRING
            FROM smile_saves s
            JOIN smile_words w
              ON w.event_id = s.payload:word_id::NUMBER
            WHERE s.payload:name::STRING = %(name)s
            ORDER BY s.save_id DESC
            """,
            {"name": clean_name},
        )
        if saved_lines:
            st.divider()
            st.subheader("Saved for you")
            for (line,) in saved_lines:
                st.write(f"“{line}”")
