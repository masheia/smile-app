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


def user_id_for(name):
    found = run(
        "SELECT user_id FROM smile_users WHERE name = %(name)s",
        {"name": name},
    )
    if found:
        return found[0][0]
    run(
        """
        INSERT INTO smile_users (user_id, name)
        SELECT smile_user_seq.NEXTVAL, %(name)s
        """,
        {"name": name},
    )
    found = run(
        "SELECT user_id FROM smile_users WHERE name = %(name)s",
        {"name": name},
    )
    return found[0][0]


def word_name_for(text):
    key = text.lower()
    found = run(
        "SELECT word_name FROM smile_dictionary WHERE word_key = %(key)s",
        {"key": key},
    )
    if found:
        return found[0][0]
    run(
        """
        INSERT INTO smile_dictionary (word_name, word_key)
        SELECT %(text)s, %(key)s
        """,
        {"text": text, "key": key},
    )
    return text


if "liked" not in st.session_state:
    st.session_state.liked = []

name = st.text_input("Your name", max_chars=40)
clean_name = " ".join(name.split())[:40]
current_user_id = None
if clean_name and secrets_ready():
    current_user_id = user_id_for(clean_name)

with st.form("share", clear_on_submit=True):
    text = st.text_input("A word, a thought, or some encouragement", max_chars=200)
    share_as = st.radio("Who can read it", ["Public", "Private"], horizontal=True)
    submitted = st.form_submit_button("Share")

if submitted:
    cleaned = " ".join(text.split())[:200]
    if not clean_name:
        st.error("Type your name first.")
    elif not cleaned:
        st.error("Write something first.")
    elif not secrets_ready():
        st.error("Snowflake is not connected yet.")
    else:
        is_public = share_as == "Public"
        word_name = word_name_for(cleaned)
        run(
            """
            INSERT INTO smile_entries (payload)
            SELECT OBJECT_CONSTRUCT(
              'user_id', %(user_id)s,
              'word_name', %(word_name)s,
              'public', %(is_public)s = 1,
              'likes', 0
            )
            """,
            {
                "user_id": int(current_user_id),
                "word_name": word_name,
                "is_public": 1 if is_public else 0,
            },
        )
        if is_public:
            st.success("Shared.")
        else:
            st.success("Kept private.")

st.divider()
st.subheader("Shared lines")

if not secrets_ready():
    st.info("Connect Snowflake to see what people have shared.")
else:
    rows = run(
        """
        SELECT
          entry_id,
          payload:word_name::STRING,
          payload:likes::NUMBER
        FROM smile_entries
        WHERE payload:public::BOOLEAN
        ORDER BY entry_id DESC
        LIMIT 30
        """
    )
    if not rows:
        st.write("Be the first kind line on this page.")

    saved_ids = []
    if current_user_id is not None:
        saved_rows = run(
            """
            SELECT entry_id
            FROM smile_kept
            WHERE user_id = %(user_id)s
            """,
            {"user_id": int(current_user_id)},
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
                UPDATE smile_entries
                SET payload = OBJECT_INSERT(
                  payload,
                  'likes',
                  payload:likes::NUMBER + 1,
                  TRUE
                )
                WHERE entry_id = %(event_id)s
                """,
                {"event_id": event_id},
            )
            st.session_state.liked.append(event_id)
            st.rerun()
        if event_id in saved_ids:
            save_col.write("Saved")
        elif save_col.button("Save", key=f"save-{event_id}"):
            if current_user_id is None:
                st.warning("Type your name first, then save.")
            else:
                run(
                    """
                    INSERT INTO smile_kept (user_id, entry_id)
                    SELECT %(user_id)s, %(entry_id)s
                    """,
                    {"user_id": int(current_user_id), "entry_id": event_id},
                )
                st.rerun()

    if current_user_id is not None:
        saved_lines = run(
            """
            SELECT e.payload:word_name::STRING
            FROM smile_kept k
            JOIN smile_entries e
              ON e.entry_id = k.entry_id
            WHERE k.user_id = %(user_id)s
            ORDER BY k.created_at DESC
            """,
            {"user_id": int(current_user_id)},
        )
        if saved_lines:
            st.divider()
            st.subheader("Saved for you")
            for (line,) in saved_lines:
                st.write(f"“{line}”")
