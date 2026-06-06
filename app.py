import streamlit as st

st.title("🔐 パスワード管理アプリ（試作版）")

service_name = st.text_input("サービス名（例: Google）")
password = st.text_input("パスワード", type="password")

if st.button("保存する"):
    if service_name and password:
        st.success(f"【デモ】{service_name} のパスワードを一時的に受け付けました！")
    else:
        st.error("入力してください。")
