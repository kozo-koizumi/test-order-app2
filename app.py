import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from streamlit_gsheets import GSheetsConnection  # 追加

# ページ設定とタイトル
st.set_page_config(page_title="注文票アプリ", layout="centered")
st.title("住所入力・Googleシート保存アプリ")

# Google Sheetsへの接続設定
conn = st.connection("gsheets", type=GSheetsConnection)

# --- データの保存場所（セッション状態） ---
if "address_input" not in st.session_state:
    st.session_state.address_input = ""

# --- 入力エリア ---
st.subheader("お届け先情報入力")
name = st.text_input("お名前")
zipcode = st.text_input("郵便番号 (7桁)", max_chars=7)

if st.button("住所を検索"):
    if len(zipcode) == 7:
        url = f"https://zipcloud.ibsnet.co.jp/api/search?zipcode={zipcode}"
        res = requests.get(url).json()
        if res.get("results"):
            r = res["results"][0]
            st.session_state.address_input = f"{r['address1']}{r['address2']}{r['address3']}"
        else:
            st.error("住所が見つかりませんでした。")

final_address = st.text_input("住所詳細（番地など）", value=st.session_state.address_input)

# --- 保存ボタン ---
if st.button("データをGoogleシートへ保存"):
    if name and final_address:
        # 新しいデータ行の作成
        new_data = pd.DataFrame([{
            "登録日時": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
            "お名前": name,
            "郵便番号": zipcode,
            "住所": final_address
        }])
        
        # 既存のシートを読み込んで追記
        existing_data = conn.read(worksheet="Sheet1")
        updated_df = pd.concat([existing_data, new_data], ignore_index=True)
        
        # シートを更新
        conn.update(worksheet="Sheet1", data=updated_df)
        
        st.success("Googleスプレッドシートに保存しました！")
    else:
        st.error("お名前と住所を入力してください。")

