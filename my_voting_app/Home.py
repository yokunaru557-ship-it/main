import streamlit as st
import os
from PIL import Image
import base64
import google_auth_oauthlib.flow
import json # ▼追加：Cloudの設定を読み込むために必要
from background import set_background

# ---------------------------------------------------------
# 1. 設定 & 定数
# ---------------------------------------------------------
PAGE_TITLE = "投票アプリ Home"
APP_DESCRIPTION = "チームの意見を一つに。新しい議題を作ったり、投票に参加しましょう。"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PAGEICON_PATH = os.path.join(BASE_DIR, "images/icon_01.png")

# Googleログイン設定
CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, "client_secret.json")
SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.email']

# ▼▼▼ 修正：CloudとローカルでURLを自動切り替え ▼▼▼
# Secretsに "auth" 設定があればCloud用のURLを使う
if "auth" in st.secrets and "redirect_uri" in st.secrets["auth"]:
    REDIRECT_URI = st.secrets["auth"]["redirect_uri"]
else:
    REDIRECT_URI = 'http://localhost:8501' # ローカル用

# ---------------------------------------------------------
# 2. ページ設定
# ---------------------------------------------------------
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGEICON_PATH,
    layout="centered"
)

set_background("background.png")

# ---------------------------------------------------------
# 3. カスタムCSS & ヘッダー関数
# ---------------------------------------------------------
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

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
# Googleログイン処理（Cloud対応ハイブリッド版）
# ---------------------------------------------------------
def google_login():
    flow = None
    
    # 1. PCにファイルがあるか探す（ローカル用）
    if os.path.exists(CLIENT_SECRETS_FILE):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
    
    # 2. ファイルがないならCloudのSecretsを探す（Cloud用）
    elif "auth" in st.secrets and "client_secret_json" in st.secrets["auth"]:
        try:
            # Secretsの文字列をプログラムで使える形に変換
            client_config = json.loads(st.secrets["auth"]["client_secret_json"])
            
            flow = google_auth_oauthlib.flow.Flow.from_client_config(
                client_config,
                scopes=SCOPES,
                redirect_uri=REDIRECT_URI
            )
        except Exception as e:
            st.error(f"Secrets設定エラー: {e}")
            return None
    else:
        st.error("⚠️ 認証キーが見つかりません。client_secret.jsonを置くか、Secretsを設定してください。")
        return None

    # --- 認証フローの実行 ---
    if 'code' not in st.query_params:
        # ログインボタン表示
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.title("🔒 ログイン")
        st.write("アプリを利用するにはGoogleアカウントでログインしてください。")
        st.link_button("Googleでログイン", auth_url, type="primary")
        return None
    else:
        # Googleから戻ってきた後の処理
        code = st.query_params['code']
        try:
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            from google.oauth2 import id_token
            from google.auth.transport import requests
            
            token_request = requests.Request()
            id_info = id_token.verify_oauth2_token(
                credentials.id_token, token_request, credentials.client_id)
            
            email = id_info.get('email')
            
            st.query_params.clear()
            return email
            
        except Exception as e:
            st.error(f"ログインエラー: {e}")
            return None

# ---------------------------------------------------------
# 4. メインUI構築
# ---------------------------------------------------------
def main():
    if "logged_in_user" not in st.session_state:
        st.session_state.logged_in_user = None

    # ログインしていない場合
    if st.session_state.logged_in_user is None:
        user_email = google_login()
        if user_email:
            st.session_state.logged_in_user = user_email
            st.rerun()
        return

    # --- ログイン済み ---
    
    with st.container(border=True):
        header_with_icon(PAGEICON_PATH, "投票アプリへようこそ！")
        
        st.caption(f"ログイン中: {st.session_state.logged_in_user}")
        
        st.markdown(APP_DESCRIPTION)
        st.divider()

        st.subheader("メニュー")
        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            st.page_link("pages/1_議題一覧.py", label="議題一覧を見る", icon="📋", help="現在進行中の投票に参加します")
            st.page_link("pages/2_新規作成.py", label="新しい議題を作成する", icon="✨", help="新しい投票トピックを立ち上げます")
            st.page_link("pages/3_投票結果.py", label="投票結果を見る", icon="📊", help="集計結果を確認します")

        st.divider()

        if st.button("ログアウト"):
            st.session_state.logged_in_user = None
            st.rerun()

        st.caption("Project-SYOUDAいRA")

if __name__ == "__main__":
    main()
