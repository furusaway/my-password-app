import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date, timedelta

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


# ─── ページ1: パスワード登録画面 ───
def register_page():
    st.title("📝 パスワードの登録")
    st.write("サービス名、パスワード、および有効期限を設定してください。")
    
    with st.form(key="password_form", clear_on_submit=True):
        service_name = st.text_input("サービス名（例: Google, Twitter）")
        password = st.text_input("パスワード", type="password")
        
        st.markdown("---")
        st.write("📅 **有効期限の設定**")
        
        days_offset = st.number_input("① 今日から何日後にしますか？", min_value=0, value=90, step=1)
        calculated_date = date.today() + timedelta(days=days_offset)
        expiry_date = st.date_input("② または、カレンダーから直接選ぶ", value=calculated_date)
        
        st.markdown("---")
        submit_button = st.form_submit_button(label="保存する")

    if submit_button:
        if service_name and password:
            new_data = {
                "サービス名": service_name, 
                "パスワード": password,
                "有効期限": expiry_date.strftime("%Y-%m-%d")
            }
            st.session_state.password_list.append(new_data)
            save_passwords(st.session_state.password_list)
            st.success(f"🎉 {service_name} のパスワードを保存しました！")
        else:
            st.warning("⚠️ サービス名とパスワードの両方を入力してください。")


# ─── ページ2: パスワード一覧画面（削除機能付き） ───
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

    # ファイルから最新データを読み込み
    st.session_state.password_list = load_passwords()

    if st.session_state.password_list:
        processed_list = []
        today = date.today()
        
        for item in st.session_state.password_list:
            expiry_str = item.get("有効期限", today.strftime("%Y-%m-%d"))
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            days_left = (expiry_date - today).days
            
            if days_left < 0:
                status = "⚠️ 期限切れ！"
            elif days_left <= 30:
                status = f"⏳ あと {days_left} 日"
            else:
                status = "✅ 安全（期限内）"
            
            processed_list.append({
                "サービス名": item["サービス名"],
                "パスワード": item["パスワード"],
                "有効期限": expiry_str,
                "状態": status
            })
            
        df = pd.DataFrame(processed_list)
        
        st.write("💡 削除したいデータの**左端にチェック**を入れて、下の「選択したデータを削除」ボタンを押してください。")
        
        # 【修正箇所】selection_mode を "multi-row" に変更
        event = st.dataframe(
            df,
            column_config={
                "パスワード": st.column_config.TextColumn("パスワード"),
                "状態": st.column_config.TextColumn("状態")
            },
            hide_index=True,
            use_container_width=True,
            on_select="rerun",
            selection_mode="multi-row"
        )
        
        # 選択された行のインデックス（番号）を取得
        selected_rows = event.selection.rows
        
        if selected_rows:
            # 選択されたサービス名をリストアップして画面に表示
            selected_services = [df.iloc[r]["サービス名"] for r in selected_rows]
            st.write(f"選択中: `{', '.join(selected_services)}`")
            
            # 🔴 削除ボタンの出現
            if st.button("🗑️ 選択したデータを削除", type="primary"):
                # 選択されていないデータだけを残す（＝選択されたものを消す）
                new_password_list = [
                    item for i, item in enumerate(st.session_state.password_list) if i not in selected_rows
                ]
                
                # データを更新してファイルに保存
                st.session_state.password_list = new_password_list
                save_passwords(new_password_list)
                
                st.success("💥 選択されたパスワードを削除しました！")
                st.rerun()  # 画面を更新して消えた状態にする
                
    else:
        st.info("まだ登録されたパスワードはありません。")


# ─── ページナビゲーションの設定 ───
pg = st.navigation([
    st.Page(register_page, title="パスワード登録", icon="📝"),
    st.Page(list_page, title="パスワード一覧", icon="📋")
])

pg.run()
