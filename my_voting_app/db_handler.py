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
    
    creds = None
    if os.path.exists(KEY_FILE):
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE, scope)
        except Exception as e:
            st.error(f"認証ファイル(key.json)の読み込みエラー: {e}")
            return None
    else:
        try:
            # Secretsから読み込む
            if "gcp_service_account" in st.secrets:
                key_dict = dict(st.secrets["gcp_service_account"])
                creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
            else:
                return None
        except Exception as e:
            st.error(f"Secrets認証情報の読み込みエラー: {e}")
            return None

    try:
        client = gspread.authorize(creds)
        sheet = client.open(SPREADSHEET_NAME)
        return sheet
    except Exception as e:
        st.error(f"接続エラー: {e}")
        return None

# ---------------------------------------------------------
# 1. 議題を保存する（修正済み：メールとステータスを保存）
# ---------------------------------------------------------
def add_topic_to_sheet(title, author, options, deadline, owner_email):
    sheet = connect_to_sheet()
    if sheet is None: return
    
    try:
        worksheet = sheet.worksheet("topics")
        t_delta = datetime.timedelta(hours=9)
        JST = datetime.timezone(t_delta, 'JST')
        created_at = datetime.datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")
        
        # ▼▼▼ ここが重要！7つのデータを保存します ▼▼▼
        # 1.タイトル 2.作成者 3.選択肢 4.締切 5.作成日 6.ステータス 7.所有者メアド
        new_row = [title, author, options, str(deadline), created_at, "active", owner_email]
        
        worksheet.append_row(new_row)
    except Exception as e:
        st.error(f"書き込みエラー: {e}")

# ---------------------------------------------------------
# 2. 議題を読み込む
# ---------------------------------------------------------
def get_topics_from_sheet():
    sheet = connect_to_sheet()
    if sheet is None: return pd.DataFrame()
    
    try:
        worksheet = sheet.worksheet("topics")
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"読み込みエラー: {e}")
        return pd.DataFrame()

# ---------------------------------------------------------
# 3. 投票を保存する
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# 4. 投票数を集計する
# ---------------------------------------------------------
def get_votes_from_sheet():
    sheet = connect_to_sheet()
    if sheet is None: return pd.DataFrame()
    
    try:
        worksheet = sheet.worksheet("votes")
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"投票読み込みエラー: {e}")
        return pd.DataFrame()

# ---------------------------------------------------------
# 5. ステータスを終了にする
# ---------------------------------------------------------
def close_topic_status(topic_title):
    try:
        sheet = connect_to_sheet()
        if sheet is None: return

        worksheet = sheet.worksheet("topics")
        cell = worksheet.find(topic_title)
        # F列(6列目)を closed に書き換える
        worksheet.update_cell(cell.row, 6, "closed")
        
    except Exception as e:
        st.error(f"ステータス更新エラー: {e}")
