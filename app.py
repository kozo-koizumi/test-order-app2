import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# ページの設定
st.set_page_config(page_title="注文票アプリ", layout="centered")
st.title("住所入力・Excel保存アプリ")

# 1. データの保存場所（セッション状態）を準備
if "data_list" not in st.session_state:
    st.session_state.data_list = []
if "address_input" not in st.session_state:
    st.session_state.address_input = ""

# --- 入力エリア ---
st.subheader("お届け先情報入力")

# お名前と郵便番号の入力
name = st.text_input("お名前", key="name_input")
zipcode = st.text_input("郵便番号 (7桁、ハイフンなし)", max_chars=7)

# 2. 住所検索の処理
if st.button("住所を検索"):
    if len(zipcode) == 7:
        try:
            url = f"https://zipcloud.ibsnet.co.jp/api/search?zipcode={zipcode}"
            response = requests.get(url)
            res_data = response.json()
            
            if res_data["results"]:
                r = res_data["results"][0]
                # 住所を結合してセッションに保存
                st.session_state.address_input = f"{r['address1']}{r['address2']}{r['address3']}"
            else:
                st.error("該当する住所が見つかりませんでした。")
                st.session_state.address_input = ""
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
    else:
        st.warning("郵便番号を7桁で入力してください。")

# 3. 住所の確認・詳細入力（検索結果がここに入る）
final_address = st.text_input("住所詳細（番地など）", value=st.session_state.address_found if "address_found" in locals() else st.session_state.address_input)

# 4. リストに追加ボタン
if st.button("リストに追加"):
    if name and final_address:
        new_entry = {
            "登録日時": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
            "お名前": name,
            "郵便番号": zipcode,
            "住所": final_address
        }
        st.session_state.data_list.append(new_entry)
        st.success(f"{name}様のデータを追加しました。")
    else:
        st.error("お名前と住所を両方入力してください。")

# --- 登録データの一覧表示とExcel出力 ---
if st.session_state.data_list:
    st.divider()
    st.subheader("登録済みデータ一覧")
    df = pd.DataFrame(st.session_state.data_list)
    st.dataframe(df)

    # Excelファイルの作成（メモリ上）
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Orders')
    
    # ダウンロードボタン
    st.download_button(
        label="Excel形式で全データをダウンロード",
        data=output.getvalue(),
        file_name="order_list_2026.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # リセットボタン
    if st.button("全データを消去"):
        st.session_state.data_list = []
        st.session_state.address_input = ""
        st.rerun()
