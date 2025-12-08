import streamlit as st
import os
import base64
from background import set_background  #  # 背景画像の設定ファイルをインポート
# ---------------------------------------------------------
# 1. 設定 & 定数
# ---------------------------------------------------------
PAGE_TITLE = "投票アプリ Home"
APP_DESCRIPTION = "チームの意見を一つに。新しい議題を作ったり、投票に参加しましょう。"
PAGEICON_PATH = os.path.join(os.path.dirname(__file__), "images/icon_01.png")
# ---------------------------------------------------------
# 2. ページ設定
# ---------------------------------------------------------
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGEICON_PATH,
    layout="centered"
)

set_background("background.png")  # 背景画像の設定
# ---------------------------------------------------------
# 3. カスタムCSS (見た目の微調整)
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* 全体の余白調整 */
    .block-container {AC
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# アイコン＋文字列のヘッダー表示用関数
def header_with_icon(icon_path, text):
    with open(icon_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    header_html = f"""
    <div style="display:flex; align-items:center; gap:10px;">
        <img src="data:image/png;base64,{encoded}" width="40">
        <h1 style="margin:0;">{text}</h1>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
# ---------------------------------------------------------
# 4. メインUI構築
# ---------------------------------------------------------
def main():
    # 外枠のコンテナ
    with st.container(border=True):
        
     # --- ヘッダー（ここを書き換え！） --
        header_with_icon(PAGEICON_PATH, "投票アプリへようこそ！")
        st.markdown(APP_DESCRIPTION)
        st.divider()

        # --- ナビゲーションメニュー ---
        st.subheader("メニュー")
        
        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            st.page_link("pages/1_議題一覧.py", label="議題一覧を見る", icon="📋", help="現在進行中の投票に参加します")
            st.page_link("pages/2_新規作成.py", label="新しい議題を作成する", icon="✨", help="新しい投票トピックを立ち上げます")
            st.page_link("pages/3_投票結果.py", label="投票結果を見る", icon="📊", help="集計結果を確認します")

        st.divider()

        # --- フッター ---
        # 統計情報は削除し、シンプルな表記のみにしました
        st.caption("Project-SYOUDAいRA")

if __name__ == "__main__":
    main()
















