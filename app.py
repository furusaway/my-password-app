import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

# ページ全体の初期設定
st.set_page_config(page_title="🔐 パスワード管理アプリ", page_icon="🔐", layout="centered")

# ─── 🔑 セキュリティ設定 ───
MASTER_PASSWORD = "1234"
SAVE_FILE = "passwords_data.json"


# ─── 💾 データの読み込み・保存機能 ───
def load_passwords():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_passwords(data_list):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)


if "password_list" not in st.session_state:
    st.session_state.password_list = load_passwords()

if "is_unlocked" not in st.session_state:
    st.session_state.is_unlocked = False


# ─── ページ1: パスワード登録画面（有効期限の入力追加） ───
def register_page():
    st.title("📝 パスワードの登録")
    st.write("サービス名、パスワード、および有効期限を設定してください。")
    
    with st.form(key="password_form", clear_on_submit=True):
        service_name = st.text_input("サービス名（例: Google, Twitter）")
        password = st.text_input("パスワード", type="password")
        
        # 有効期限の入力欄（デフォルトは本日の日付）
        expiry_date = st.date_input("パスワードの有効期限", value=date.today())
        
        submit_button = st.form_submit_button(label="保存する")

    if submit_button:
        if service_name and password:
            # 日付を保存可能な文字列型（YYYY-MM-DD）に変換して保存
            new_data = {
                "サービス名": service_name, 
                "パスワード": password,
                "有効期限": expiry_date.strftime("%Y-%m-%d")
            }
            st.session_state.password_list.append(new_data)
            save_passwords(st.session_state.password_list)
            st.success(f"🎉 {service_name} のパスワード（期限: {expiry_date}）を保存しました！")
        else:
            st.warning("⚠️ サービス名とパスワードの両方を入力してください。")


# ─── ページ2: パスワード一覧画面（期限切れアラート機能付き） ───
def list_page():
    st.title("📋 登録済みパスワード一覧")
    
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

    st.success("🔓 ロックが解除されました。")
    if st.button("🔴 すぐに再ロックする"):
        st.session_state.is_unlocked = False
        st.rerun()
        
    st.markdown("---")

    st.session_state.password_list = load_passwords()

    if st.session_state.password_list:
        # 画面表示用のデータを作成（期限チェックを行う）
        processed_list = []
        today = date.today()
        
        for item in st.session_state.password_list:
            expiry_str = item.get("有効期限", today.strftime("%Y-%m-%d"))
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            
            # 残り日数の計算
            days_left = (expiry_date - today).days
            
            # ステータスの判定
            if days_left < 0:
                status = "⚠️ 期限切れ！変更してください"
            elif days_left <= 30:
                status = f"⏳ あと {days_left} 日で期限切れ"
            else:
                status = "✅ 安全（期限内）"
            
            processed_list.append({
                "サービス名": item["サービス名"],
                "パスワード": item["パスワード"],
                "有効期限": expiry_str,
                "状態": status
            })
            
        df = pd.DataFrame(processed_list)
        
        # 状態がパッと見てわかりやすいように一覧を表示
        st.dataframe(
            df,
            column_config={
                "パスワード": st.column_config.TextColumn("パスワード"),
                "状態": st.column_config.TextColumn("状態")
            },
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
