import json
import os
from datetime import date, datetime, timedelta
import pandas as pd
import requests
import streamlit as st

# ページ全体の初期設定
st.set_page_config(
    page_title="🔐 パスワード管理アプリ", page_icon="🔐", layout="centered"
)

# ─── 🔑 セキュリティ・外部連携設定 ───
MASTER_PASSWORD = "1234"
SAVE_FILE = "passwords_data.json"

# LINE Messaging API設定（取得した値をここに入力してください）
LINE_CHANNEL_ACCESS_TOKEN = "YOUR_CHANNEL_ACCESS_TOKEN"
LINE_USER_ID = "YOUR_USER_ID"


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


# ─── 💬 LINE通知機能 ───
def send_line_notification(message):
    if (
        LINE_CHANNEL_ACCESS_TOKEN == "YOUR_CHANNEL_ACCESS_TOKEN"
        or LINE_USER_ID == "YOUR_USER_ID"
    ):
        return  # 初期設定のままなら送信しない

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
    }
    payload = {
        "to": LINE_USER_ID,
        "messages": [{"type": "text", "text": message}],
    }
    try:
        requests.post(url, json=payload, headers=headers, timeout=5)
    except Exception as e:
        st.error(f"LINE通知に失敗しました: {e}")


# ─── ⏰ 期限チェック＆LINE通知実行 ───
def check_and_notify_expiry():
    # セッション内で1回のみ実行するためのフラグ
    if "has_checked_expiry" not in st.session_state:
        st.session_state.has_checked_expiry = False

    if st.session_state.has_checked_expiry:
        return

    passwords = load_passwords()
    today = date.today()
    alert_services = []

    for item in passwords:
        expiry_str = item.get("有効期限", "")
        if expiry_str:
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            days_left = (expiry_date - today).days
            # 💡 期限切れ、または10日前からのものを対象にする
            if days_left <= 10:
                if days_left < 0:
                    alert_services.append(
                        f"・{item['サービス名']} (期限切れ!)"
                    )
                else:
                    alert_services.append(
                        f"・{item['サービス名']} (あと {days_left} 日)"
                    )

    if alert_services:
        msg = "【パスワード期限通知】\n期限が近づいている、または切れているサービスがあります。\n\n" + "\n".join(
            alert_services
        )
        send_line_notification(msg)

    st.session_state.has_checked_expiry = True


# 初期化
if "password_list" not in st.session_state:
    st.session_state.password_list = load_passwords()

if "is_unlocked" not in st.session_state:
    st.session_state.is_unlocked = False

if "editing_index" not in st.session_state:
    st.session_state.editing_index = None

# アプリ起動時に期限チェック（LINE通知）を実行
check_and_notify_expiry()


# ─── ページ1: パスワード登録画面 ───
def register_page():
    st.title("📝 パスワードの登録")
    st.write("サービス名、パスワード、および有効期限を設定してください。")

    with st.form(key="password_form", clear_on_submit=True):
        service_name = st.text_input("サービス名（例: Google, Twitter）")
        password = st.text_input("パスワード", type="password")

        st.markdown("---")
        st.write("📅 **有効期限の設定**")

        days_offset = st.number_input(
            "① 今日から何日後にしますか？", min_value=0, value=90, step=1
        )
        calculated_date = date.today() + timedelta(days=days_offset)
        expiry_date = st.date_input(
            "② または、カレンダーから直接選ぶ", value=calculated_date
        )

        st.markdown("---")
        submit_button = st.form_submit_button(label="保存する")

    if submit_button:
        if service_name and password:
            new_data = {
                "サービス名": service_name,
                "パスワード": password,
                "有効期限": expiry_date.strftime("%Y-%m-%d"),
            }
            st.session_state.password_list.append(new_data)
            save_passwords(st.session_state.password_list)
            st.success(f"🎉 {service_name} のパスワードを保存しました！")
            st.session_state.has_checked_expiry = (
                False  # データ追加されたので再チェック可能に
            )
        else:
            st.warning("⚠️ サービス名とパスワードの両方を入力してください。")


# ─── ページ2: パスワード一覧・編集・削除画面 ───
def list_page():
    st.title("📋 登録済みパスワード一覧")

    if not st.session_state.is_unlocked:
        st.warning("🔒 このページを表示するには暗証番号が必要です。")
        input_pin = st.text_input(
            "マスターパスワードを入力してください", type="password"
        )
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
        st.session_state.editing_index = None
        st.rerun()

    st.markdown("---")

    # 最新データの読み込み
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
            elif days_left <= 10:
                status = f"🚨 あと {days_left} 日 (10日以内)"
            elif days_left <= 30:
                status = f"⏳ あと {days_left} 日"
            else:
                status = "✅ 安全（期限内）"

            processed_list.append(
                {
                    "サービス名": item["サービス名"],
                    "パスワード": item["パスワード"],
                    "有効期限": expiry_str,
                    "状態": status,
                }
            )

        df = pd.DataFrame(processed_list)

        # ─── ✍️ 編集フォームの表示 ───
        if st.session_state.editing_index is not None:
            idx = st.session_state.editing_index
            edit_item = st.session_state.password_list[idx]
            st.markdown(
                f"### ✍️ `{edit_item['サービス名']}` の変更フォーム"
            )

            with st.form(key="edit_form"):
                new_service = st.text_input(
                    "サービス名", value=edit_item["サービス名"]
                )
                new_password = st.text_input(
                    "新しいパスワード", value=edit_item["パスワード"]
                )
                current_expiry = datetime.strptime(
                    edit_item["有効期限"], "%Y-%m-%d"
                ).date()
                new_expiry = st.date_input("有効期限", value=current_expiry)

                col1, col2 = st.columns(2)
                with col1:
                    save_edit = st.form_submit_button("変更を保存")
                with col2:
                    cancel_edit = st.form_submit_button("キャンセル")

            if save_edit:
                st.session_state.password_list[idx] = {
                    "サービス名": new_service,
                    "パスワード": new_password,
                    "有効期限": new_expiry.strftime("%Y-%m-%d"),
                }
                save_passwords(st.session_state.password_list)
                st.success("🎉 パスワードを変更しました！")
                st.session_state.editing_index = None
                st.session_state.has_checked_expiry = False
                st.rerun()

            if cancel_edit:
                st.session_state.editing_index = None
                st.rerun()

            st.markdown("---")

        # ─── 一覧データテーブル ───
        st.write(
            "💡 **データの変更・削除:** 左端のチェックを入れて、下のボタンを押してください。"
        )

        event = st.dataframe(
            df,
            column_config={
                "パスワード": st.column_config.TextColumn("パスワード"),
                "状態": st.column_config.TextColumn("状態"),
            },
            hide_index=True,
            use_container_width=True,
            on_select="rerun",
            selection_mode="multi-row",
        )

        selected_rows = event.selection.rows

        if selected_rows:
            selected_services = [
                df.iloc[r]["サービス名"] for r in selected_rows
            ]
            st.write(f"選択中: `{', '.join(selected_services)}`")

            col_btn1, col_btn2 = st.columns(2)

            # 変更ボタン（1つのデータが選択されている時だけ有効）
            with col_btn1:
                if len(selected_rows) == 1:
                    if st.button("✍️ 選択したデータを変更"):
                        st.session_state.editing_index = selected_rows[0]
                        st.rerun()
                else:
                    st.caption("※「変更」はデータを1つだけ選んだ時に押せます")

            # 削除ボタン
            with col_btn2:
                if st.button("🗑️ 選択したデータを削除", type="primary"):
                    new_password_list = [
                        item
                        for i, item in enumerate(
                            st.session_state.password_list
                        )
                        if i not in selected_rows
                    ]
                    st.session_state.password_list = new_password_list
                    save_passwords(new_password_list)
                    st.success("💥 選択されたパスワードを削除しました！")
                    st.session_state.editing_index = None
                    st.rerun()

    else:
        st.info("まだ登録されたパスワードはありません。")


# ─── ページナビゲーションの設定 ───
pg = st.navigation(
    [
        st.Page(register_page, title="パスワード登録", icon="📝"),
        st.Page(list_page, title="パスワード一覧", icon="📋"),
    ]
)

pg.run()
