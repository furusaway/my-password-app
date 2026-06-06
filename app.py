import streamlit as st
import pandas as pd
import json
import os

# ページ全体の初期設定
st.set_page_config(page_title="🔐 パスワード管理アプリ", page_icon="🔐", layout="centered")

# ─── 🔑 セキュリティ設定 ───
# あなただけの「マスターパスワード（暗証番号）」
# ※ 好きな番号に書き換えてください
MASTER_PASSWORD = "1234"

# データを保存するファイル名（サーバー内に自動で作られます）
SAVE_FILE = "passwords_data.json"


# ─── 💾 データの読み込み・保存機能 ───
def load_passwords():
    """ファイルからパスワードデータを読み込む関数"""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_passwords(data_list):
    """ファイルにパスワードデータを書き込む関数"""
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)


# アプリ起動時に、ファイルからデータを一瞬で読み込んでセットする
if "password_list" not in st.session_state:
    st.session_state.password_list = load_passwords()

# ロック状態の管理
if "is_unlocked" not in st.session_state:
    st.session_state.is_unlocked = False


# ─── ページ1: パスワード登録画面 ───
def register_page():
    st.title("📝 パスワードの登録")
    st.write("新しいサービスとパスワードを入力して保存してください。")
    
    with st.form(key="password_form", clear_on_submit=True):
        service_name = st.text_input("サービス名（例: Google, Twitter）")
        password = st.text_input("パスワード", type="password")
        submit_button = st.form_submit_button(label="保存する")

    if submit_button:
        if service_name and password:
            # 1. データを追加
            new_data = {"サービス名": service_name, "パスワード": password}
            st.session_state.password_list.append(new_data)
            
            # 2. 【重要】ファイルに上書き保存する（これでリロードしても消えません）
            save_passwords(st.session_state.password_list)
            
            st.success(f"🎉 {service_name} のパスワードを保存しました！ファイルに記録されたためリロードしても消えません。")
        else:
            st.warning("⚠️ サービス名とパスワードの両方を入力してください。")


# ─── ページ2: パスワード一覧画面（ロック機能付き） ───
def list_page():
    st.title("📋 登録済みパスワード一覧")
    
    # ロックが解除されていない場合
    if not st.session_state.is_unlocked:
        st.warning("🔒 このページを表示するには暗証番号が必要です。")
        input_pin = st.text_input("マスターパスワードを入力してください", type="password")
        unlocked_button = st.button("ロックを解除")
        
        if unlocked_button:
            if input_pin == MASTER_PASSWORD:
                st.session_state.is_unlocked = True
                st.rerun()
            else:
                st.error("❌ 暗証番号が違います。アクセスを拒否しました。")
        return 

    # ロックが解除された時だけ表示
    st.success("🔓 ロックが解除されました。")
    if st.button("🔴 すぐに再ロックする"):
        st.session_state.is_unlocked = False
        st.rerun()
        
    st.markdown("---")

    # 常に最新のファイルを読み込み直して表示する
    st.session_state.password_list = load_passwords()

    if st.session_state.password_list:
        df = pd.DataFrame(st.session_state.password_list)
        st.dataframe(
            df,
            column_config={"パスワード": st.column_config.TextColumn("パスワード")},
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("まだ登録されたパスワードはありません。")


# ─── ページナビゲーションの設定 ───
pg = st.navigation([
    st.Page(register_page, title="パスワード登録", icon="📝"),
    st.Page(list_page, title="パスワード一覧", icon="📋")
])

pg.run()
