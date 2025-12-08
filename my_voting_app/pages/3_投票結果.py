import streamlit as st
from db_handler import get_topics_from_sheet, get_votes_from_sheet

st.title("📊 投票結果")

topics_df = get_topics_from_sheet()
votes_df = get_votes_from_sheet()

if topics_df.empty:
    st.warning("議題がありません")
else:
    topic_titles = topics_df["title"].tolist()

    selected_topic = st.selectbox("議題を選択", topic_titles)

    if selected_topic:
        topic_votes = votes_df[votes_df["topic_title"] == selected_topic]

        if topic_votes.empty:
            st.info("まだ投票がありません")
        else:
            result = topic_votes["option"].value_counts().reset_index()
            result.columns = ["選択肢", "投票数"]

            st.table(result)
            st.bar_chart(result.set_index("選択肢"))
