import streamlit as st
import pandas as pd
import sys
import os

# ---------------------------------------------------------
# db_handler.py を読み込めるようにパスを通す
# ---------------------------------------------------------
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import db_handler

# ---------------------------------------------------------
# ページ設定
# ---------------------------------------------------------
st.set_page_config(page_title="投票結果", page_icon="📊")

st.title("📊 投票結果一覧")
st.caption("締切済み議題の結果のみ表示します")

# ---------------------------------------------------------
# データ取得
# ---------------------------------------------------------
topics_df = db_handler.get_topics_from_sheet()
votes_df = db_handler.get_votes_from_sheet()

# ---------------------------------------------------------
# 現在時刻（pandas形式で統一）
# ---------------------------------------------------------
now = pd.to_datetime("now")

# ---------------------------------------------------------
# deadline を datetime に変換
# ---------------------------------------------------------
if not topics_df.empty and "deadline" in topics_df.columns:
    topics_df["deadline"] = pd.to_datetime(topics_df["deadline"], errors="coerce")

# ---------------------------------------------------------
# 締切済みの議題だけ抽出
# ---------------------------------------------------------
finished_topics = (
    topics_df[topics_df["deadline"] < now]
    if not topics_df.empty
    else pd.DataFrame()
)

# ---------------------------------------------------------
# 議題リスト（ドロップダウン）
# ---------------------------------------------------------
if finished_topics.empty:
    topic_titles = ["（締切済みの議題がありません）"]
else:
    topic_titles = finished_topics["title"].tolist()

selected_topic = st.selectbox("議題を選択してください", topic_titles)

# ---------------------------------------------------------
# 表示処理
# ---------------------------------------------------------
if finished_topics.empty or selected_topic == "（締切済みの議題がありません）":
    st.info("締め切り済みの議題がまだありません。")

else:
    topic_row = finished_topics[finished_topics["title"] == selected_topic].iloc[0]
    options = topic_row["options"].split("/")

    topic_votes = (
        votes_df[votes_df["topic_title"] == selected_topic]
        if not votes_df.empty
        else pd.DataFrame()
    )

    st.subheader(f"📝 議題：{selected_topic}")

    # 集計
    result = []
    counts = topic_votes["option"].value_counts() if not topic_votes.empty else {}

    for opt in options:
        result.append({
            "選択肢": opt,
            "投票数": int(counts.get(opt, 0))
        })

    result_df = pd.DataFrame(result)

    # 表のみ表示
    st.table(result_df.reset_index(drop=True))

# ---------------------------------------------------------
# 手動更新ボタン
# ---------------------------------------------------------
st.divider()
if st.button("🔄 更新"):
    st.rerun()
