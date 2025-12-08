#%%writefile app.py
import streamlit as st
import pandas as pd
import datetime
import sys
import os

# ---------------------------------------------------------
# db_handler.py を読み込めるようにパスを通す
# ---------------------------------------------------------
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import db_handler

# ---------------------------------------------------------
# 設定 & 定数
# ---------------------------------------------------------
PAGE_TITLE = "投票アプリ"
APP_HEADER = "🗳️ 議題一覧"
APP_DESCRIPTION = "みんなで意見を集めよう！気になる議題に投票できます。"

# ---------------------------------------------------------
# ページ設定
# ---------------------------------------------------------
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="🗳️",
    layout="centered"
)

# ---------------------------------------------------------
# ヘッダー
# ---------------------------------------------------------
st.title(APP_HEADER)
st.caption(APP_DESCRIPTION)
st.divider()

# ---------------------------------------------------------
# セッションステート初期化（ソート用）
# ---------------------------------------------------------
if "fg" not in st.session_state:
    st.session_state["fg"] = 0  # 0: 期限順, 1: 新着順

# ---------------------------------------------------------
# ソートボタン（横並び）
# ---------------------------------------------------------
col_sort1, col_sort2 = st.columns([1,1])
with col_sort1:
    if st.button("⏰ 期限順"):
        st.session_state["fg"] = 0
with col_sort2:
    if st.button("🆕 新着順"):
        st.session_state["fg"] = 1
st.divider()

# ---------------------------------------------------------
# スプレッドシートから議題を取得
# ---------------------------------------------------------
topics_df = db_handler.get_topics_from_sheet()

if topics_df.empty:
    st.info("まだ議題が登録されていません。")
    st.stop()

votes_df = db_handler.get_votes_from_sheet()
today = datetime.date.today()

# 日付型に変換
topics_df["deadline"] = pd.to_datetime(topics_df["deadline"], errors="coerce").dt.date

# 締切済みの議題を除外
topics_df = topics_df[topics_df["deadline"].isna() | (topics_df["deadline"] >= today)]

# ソート
if st.session_state["fg"] == 0:
    topics_df = topics_df.sort_values("deadline", ascending=True)
else:
    topics_df = topics_df.sort_values("deadline", ascending=False)

# ---------------------------------------------------------
# 議題表示
# ---------------------------------------------------------
for index, topic in topics_df.iterrows():
    title = topic["title"]
    author = topic.get("author", "不明")
    options = topic["options"].split("/")
    deadline = topic.get("deadline", "")

    # カード風コンテナ
    with st.container():
        st.markdown(f"### {title}")
        st.caption(f"作成者：{author}｜締切：{deadline}")
        st.divider()

        col1, col2 = st.columns([1, 2])

        # 投票UI
        with col1:
            selected_option = st.radio(
                "投票してください",
                options,
                key=f"radio_{index}"
            )
            if st.button("👍 投票する", key=f"vote_{index}"):
                db_handler.add_vote_to_sheet(title, selected_option)
                st.success("投票しました！")
                st.rerun()

        # 集計表示
        with col2:
            st.write("### 📊 現在の投票数")
            topic_votes = votes_df[votes_df["topic_title"] == title] if not votes_df.empty else pd.DataFrame()
            if topic_votes.empty:
                for opt in options:
                    st.write(f"{opt}：0 票")
            else:
                counts = topic_votes["option"].value_counts()
                for opt in options:
                    st.write(f"{opt}：{counts.get(opt, 0)} 票")

        st.divider()
