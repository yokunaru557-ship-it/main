import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
import db_handler

st.title("📊 投票結果")

# 5秒ごとに自動更新
st_autorefresh(interval=5000, key="auto_refresh")


# データ取得

topics_df = db_handler.get_topics_from_sheet()
votes_df = db_handler.get_votes_from_sheet()

if topics_df.empty:
    st.info("まだ議題がありません。")
    st.stop()


# 議題選択

topic_titles = topics_df["title"].tolist()
selected_topic = st.selectbox("議題を選択してください", topic_titles)
# 集計表示
# ---------------------------------------------------------
if selected_topic:
    topic_row = topics_df[topics_df["title"] == selected_topic].iloc[0]
    options = topic_row["options"].split("/")

    # この議題の投票だけ抽出
    topic_votes = votes_df[votes_df["topic_title"] == selected_topic] if not votes_df.empty else pd.DataFrame()

    st.subheader(f"📝 議題：{selected_topic}")

    # データ作成
    result_data = []
    counts = topic_votes["option"].value_counts() if not topic_votes.empty else {}

    for opt in options:
        result_data.append({
            "選択肢": opt,
            "投票数": int(counts.get(opt, 0))
        })

    result_df = pd.DataFrame(result_data)

    # 表で表示
    st.table(result_df)

    # グラフで表示
    st.bar_chart(result_df.set_index("選択肢"))

