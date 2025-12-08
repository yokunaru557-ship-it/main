import streamlit as st
import datetime
import sys
import os

# db_handler.py を読み込めるようにパスを通す設定
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))

import db_handler 

# ---------------------------------------------------------
# ページ設定
# ---------------------------------------------------------
st.set_page_config(page_title="新規議題の作成", page_icon="✨")

st.title("✨ 新しい議題を作成する")
st.markdown("チームのみんなに聞いてみたいことを投稿しましょう！")

# 選択肢の数を管理
if "num_options" not in st.session_state:
    st.session_state.num_options = 2

def add_option():
    st.session_state.num_options += 1

def remove_option():
    if st.session_state.num_options > 2:
        st.session_state.num_options -= 1

# ---------------------------------------------------------
# メイン画面
# ---------------------------------------------------------
with st.container(border=True):
    st.subheader("📝 議題の内容")
    title = st.text_input("議題のタイトル", placeholder="例：来週のランチどこ行く？")
    
    # 作成者名
    author = st.text_input("作成者名", placeholder="例：山田 太郎")

    # ▼▼▼ 修正ポイント：日付と時間を横並びにする ▼▼▼
    # ▼▼▼ 修正：時間指定を「時」と「分」の数字入力に分ける ▼▼▼
    st.markdown("##### 📅 締め切り設定")
    
    # まず日付と時間エリアを左右に分ける
    col_date, col_time_area = st.columns([1, 1])
    
    with col_date:
        # 日付の入力
        input_date = st.date_input("締め切り日", min_value=datetime.date.today())
    
    with col_time_area:
        st.write("締め切り時間")
        # 時間エリアの中で、さらに「時」と「分」を横に並べる
        t_col1, t_col2 = st.columns(2)
        
        with t_col1:
            # 時 (0〜23)
            input_hour = st.number_input("時", min_value=0, max_value=23, value=12, step=1)
        with t_col2:
            # 分 (0〜59)
            input_minute = st.number_input("分", min_value=0, max_value=59, value=0, step=1)

    # 日付と、作成した「時・分」を合体させる
    deadline_dt = datetime.datetime.combine(
        input_date, 
        datetime.time(input_hour, input_minute)
    )
    # ▲▲▲ 修正ポイントここまで ▲▲▲
    # ▲▲▲ 修正ポイントここまで ▲▲▲
    
    st.markdown("---")
    
    st.subheader("🔢 選択肢")
    options_inputs = []
    for i in range(st.session_state.num_options):
        val = st.text_input(f"選択肢 {i+1}", key=f"option_{i}", placeholder=f"選択肢 {i+1} を入力")
        options_inputs.append(val)

    btn_col1, btn_col2, _ = st.columns([1, 1, 3])
    with btn_col1:
        st.button("＋ 選択肢を追加", on_click=add_option)
    with btn_col2:
        st.button("－ 1行削除", on_click=remove_option, disabled=(st.session_state.num_options <= 2))

    st.markdown("---")

    # 送信ボタン
    if st.button("この内容で議題を作成する", type="primary", use_container_width=True):
        # 空欄を除去
        valid_options = [opt.strip() for opt in options_inputs if opt.strip()]

        if not title:
            st.error("⚠️ タイトルを入力してください！")
        elif len(valid_options) < 2:
            st.error("⚠️ 選択肢は少なくとも2つ以上入力してください。")
        else:
            options_str = "/".join(valid_options)
            
            try:
                # 日時を見やすい文字（例: 2025-12-08 12:30）に変換
                formatted_deadline = deadline_dt.strftime("%Y-%m-%d %H:%M")

                # db_handlerを使ってスプレッドシートに書き込む
                db_handler.add_topic_to_sheet(title, author, options_str, formatted_deadline)
                
                st.success(f"✅ 議題「{title}」を作成しました！")
                st.balloons()
            except Exception as e:
                # もし設定ミスなどで保存できなかったらエラーを表示
                st.error(f"スプレッドシートへの保存に失敗しました...: {e}")
            
            # 元のコードにあった「最後の行の st.balloons()」は削除しました（重複していたため）





