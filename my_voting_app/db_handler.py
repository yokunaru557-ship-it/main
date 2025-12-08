import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
import os
import datetime

# ---------------------------------------------------------
# 設定
# ---------------------------------------------------------
SPREADSHEET_NAME = "voting_app_db"
KEY_FILE = "key.json"

# ---------------------------------------------------------
# Googleスプレッドシートに接続する関数
# ---------------------------------------------------------
def connect_to_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    # 認証情報の取得
    creds = None
    if os.path.exists(KEY_FILE):
        # ローカル環境
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE, scope)
        except Exception as e:
            st.error(f"認証ファイル(key.json)の読み込みエラー: {e}")
            return None
    else:
        # Streamlit Cloud環境
        try:
            key_dict = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
        except Exception as e:
            st.error(f"Secrets認証情報の読み込みエラー: {e}")
            return None

    # スプレッドシートへの接続
    try:
        client = gspread.authorize(creds)
        sheet = client.open(SPREADSHEET_NAME)
        return sheet
    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"エラー: スプレッドシート '{SPREADSHEET_NAME}' が見つかりません。共有設定か名前を確認してください。")
        return None
    except Exception as e:
        st.error(f"接続エラー: {e}")
        return None

# ---------------------------------------------------------
# データ操作用の関数
# ---------------------------------------------------------

# 1. 議題を保存する
def add_topic_to_sheet(title, author, options, deadline):
    sheet = connect_to_sheet()
    if sheet is None: return
    
    try:
        worksheet = sheet.worksheet("topics")
        t_delta = datetime.timedelta(hours=9)
        JST = datetime.timezone(t_delta, 'JST')
        created_at = datetime.datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")
        new_row = [title, author, options, str(deadline), created_at]
        worksheet.append_row(new_row)
    except gspread.exceptions.WorksheetNotFound:
        st.error("エラー: ワークシート 'topics' が見つかりません。")
    except Exception as e:
        st.error(f"書き込みエラー: {e}")

# 2. 議題を読み込む
def get_topics_from_sheet():
    sheet = connect_to_sheet()
    # 接続自体が失敗している場合はここで空を返す（エラーメッセージはconnect_to_sheetで表示済み）
    if sheet is None: return pd.DataFrame()
    
    try:
        worksheet = sheet.worksheet("topics")
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except gspread.exceptions.WorksheetNotFound:
        st.error("エラー: ワークシート 'topics' が見つかりません。")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"読み込みエラー: {e}") # ここで具体的なエラーを表示！
        return pd.DataFrame()

# 3. 投票を保存する
def add_vote_to_sheet(topic_title, option):
    sheet = connect_to_sheet()
    if sheet is None: return
    
    try:
        worksheet = sheet.worksheet("votes")
        t_delta = datetime.timedelta(hours=9)
        JST = datetime.timezone(t_delta, 'JST')
        voted_at = datetime.datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")
        new_row = [topic_title, option, voted_at]
        worksheet.append_row(new_row)
    except Exception as e:
        st.error(f"投票書き込みエラー: {e}")

# 4. 投票数を集計する
def get_votes_from_sheet():
    sheet = connect_to_sheet()
    if sheet is None: return pd.DataFrame()
    
    try:
        worksheet = sheet.worksheet("votes")
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except gspread.exceptions.WorksheetNotFound:
        st.error("エラー: ワークシート 'votes' が見つかりません。")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"投票読み込みエラー: {e}")
        return pd.DataFrame()
