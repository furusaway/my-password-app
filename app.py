import streamlit as st
import pandas as pd

# ページの設定
st.set_page_config(page_title="パスワード管理アプリ", page_icon="🔐")

st.title("🔐 パスワード管理アプリ（試作版）")

# 1. データを保存するデータ箱（セッション状態）の準備
if "password_list" not in st.session_state:
    st.session_state.password_list = []

# 2. 入力フォームの作成
with st.form(key="password_form", clear_on_submit=True):
    service_name = st.text_input("サービス名（例: Google, Twitter）")
    # type="password" にすることで、入力中に伏せ字（●●●）になります
    password = st.text_input("パスワード", type="password")
    
    submit_button = st.form_submit_button(label="パスワードを保存")

# 3. ボタンが押された時の処理
if submit_button:
    if service_name and password:
        # 新しいデータを追加
        new_data = {"サービス名": service_name, "パスワード": password}
        st.session_state.password_list.append(new_data)
        st.success(f"🎉 {service_name} のパスワードを保存しました！")
    else:
        st.warning("⚠️ サービス名とパスワードの両方を入力してください。")

# ─── 画面の区切り線 ───
st.markdown("---")

# 4. 保存されたパスワードの一覧表示
st.subheader("📋 保存されたパスワード一覧")

if st.session_state.password_list:
    # データを表（DataFrame）の形式に変換
    df = pd.DataFrame(st.session_state.password_list)
    
    # 画面に表として表示
    st.dataframe(df, use_container_width=True)
    
    # おまけ：パスワードを見られたくない時のために、テキストとして確認するエリア
    with st.expander("👁️ パスワードを文字で確認する"):
        for item in st.session_state.password_list:
            st.text(f"【{item['サービス名']}】: {item['password_list' if 'password_list' in item else 'パスワード']}")
else:
    st.info("まだ保存されたパスワードはありません。上のフォームから追加してください。")
