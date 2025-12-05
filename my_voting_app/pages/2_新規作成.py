import streamlit as st
import pandas as pd
import os
import datetime

# ---------------------------------------------------------
# 1. ページ設定
# ---------------------------------------------------------
st.set_page_config(page_title="新規議題の作成", page_icon="✨")

DATA_FILE = "data/topics.csv"

# ---------------------------------------------------------
# 2. 関数: データをCSVに保存する
# ---------------------------------------------------------
def save_topic(title, author, options, deadline):
    new_data = {
        "title": title,
        "author": author,
        "options": options,
        "deadline": deadline,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    new_df = pd.DataFrame([new_data])
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df = pd.concat([df, new_df], ignore_index=True)
    else:
        df = new_df

    df.to_csv(DATA_FILE, index=False)

# ---------------------------------------------------------
# 3. メインUI
# ---------------------------------------------------------
st.title("✨ 新しい議題を作成する")
st.markdown("チームのみんなに聞いてみたいことを投稿しましょう！")

# ▼▼▼ 画面の状態（選択肢の数）を管理する準備 ▼▼▼
if "num_options" not in st.session_state:
    st.session_state.num_options = 2  # 最初は2個からスタート

def add_option():
    st.session_state.num_options += 1 # 1つ増やす

def remove_option():
    if st.session_state.num_options > 2:
        st.session_state.num_options -= 1 # 1つ減らす
# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

with st.container(border=True):
    # --- 基本情報エリア ---
    st.subheader("📝 議題の内容")
    title = st.text_input("議題のタイトル", placeholder="例：来週のランチどこ行く？")
    
    col_a, col_b = st.columns(2)
    with col_a:
        author = st.text_input("作成者名", placeholder="例：山田 太郎")
    with col_b:
        deadline = st.date_input("締め切り日", min_value=datetime.date.today())
    
    st.markdown("---")
    
    # --- 選択肢エリア (Googleフォーム風) ---
    st.subheader("🔢 選択肢")
    
    # 現在の数の分だけ、入力ボックスを表示する
    options_inputs = []
    for i in range(st.session_state.num_options):
        # keyを "option_0", "option_1"... とすることで区別する
        val = st.text_input(f"選択肢 {i+1}", key=f"option_{i}", placeholder=f"選択肢 {i+1} を入力")
        options_inputs.append(val)

    # 追加・削除ボタン
    btn_col1, btn_col2, _ = st.columns([1, 1, 3])
    with btn_col1:
        st.button("＋ 選択肢を追加", on_click=add_option)
    with btn_col2:
        # 2個より多いときだけ削除ボタンを押せるようにする
        st.button("－ 1行削除", on_click=remove_option, disabled=(st.session_state.num_options <= 2))

    st.markdown("---")

    # --- 送信ボタン ---
    # フォームを使わない場合、普通のボタンで処理を書きます
    if st.button("この内容で議題を作成する", type="primary", use_container_width=True):
        
        # 空欄を除去してリストにする
        valid_options = [opt.strip() for opt in options_inputs if opt.strip()]

        if not title:
            st.error("⚠️ タイトルを入力してください！")
        elif len(valid_options) < 2:
            st.error("⚠️ 選択肢は少なくとも2つ以上入力してください（空欄は無視されます）。")
        else:
            options_str = "/".join(valid_options)
            save_topic(title, author, options_str, deadline)
            
            st.success(f"✅ 議題「{title}」を作成しました！")
            st.balloons()
