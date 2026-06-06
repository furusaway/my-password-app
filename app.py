import streamlit as st
import pandas as pd

# ページ全体の初期設定
st.set_page_config(page_title="🔐 パスワード管理アプリ", page_icon="🔐", layout="centered")

# 1. データを保存するデータ箱（セッション状態）の準備
# ページを切り替えても、このデータ箱の中身は維持されます
if "password_list" not in st.session_state:
    st.session_state.password_list = []


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
            new_data = {"サービス名": service_name, "パスワード": password}
            st.session_state.password_list.append(new_data)
            st.success(f"🎉 {service_name} のパスワードを登録しました！「一覧画面」で確認できます。")
        else:
            st.warning("⚠️ サービス名とパスワードの両方を入力してください。")


# ─── ページ2: パスワード一覧画面 ───
def list_page():
    st.title("📋 登録済みパスワード一覧")
    st.write("これまでに登録されたパスワードの確認・管理ができます。")
    
    if st.session_state.password_list:
        # 表（データフレーム）として表示
        df = pd.DataFrame(st.session_state.password_list)
        st.dataframe(df, use_container_width=True)
        
        # パスワードを隠しテキストで確認するエリア
        with st.expander("👁️ パスワードを文字で確認する"):
            for item in st.session_state.password_list:
                st.text(f"【{item['サービス名']}】: {item['パスワード']}")
    else:
        st.info("まだ登録されたパスワードはありません。「登録画面」から追加してください。")


# ─── 2. ページナビゲーションの設定 ───
# 左側のサイドバーにメニューが表示され、クリックで切り替えられるようになります
pg = st.navigation([
    st.Page(register_page, title="パスワード登録", icon="📝"),
    st.Page(list_page, title="パスワード一覧", icon="📋")
])

# 選択されたページを実行（表示）する
pg.run()
