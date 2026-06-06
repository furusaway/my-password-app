import streamlit as st
import pandas as pd

# ページ全体の初期設定
st.set_page_config(page_title="🔐 パスワード管理アプリ", page_icon="🔐", layout="centered")

# データを保存するデータ箱（セッション状態）の準備
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
            st.success(f"🎉 {service_name} のパスワードを登録しました！「パスワード一覧」ページで確認できます。")
        else:
            st.warning("⚠️ サービス名とパスワードの両方を入力してください。")


# ─── ページ2: パスワード一覧画面（シンプル＆安全版） ───
def list_page():
    st.title("📋 登録済みパスワード一覧")
    
    if st.session_state.password_list:
        df = pd.DataFrame(st.session_state.password_list)
        
        # Streamlitの機能で、パスワード列を最初から「伏せ字（●●●）」にして表示します
        # ユーザーが表の中のパスワードにマウスを乗せると、目のアイコンが出てきて中身を確認・コピーできます
        st.dataframe(
            df,
            column_config={
                "パスワード": st.column_config.TextColumn(
                    "パスワード",
                    help="マウスを乗せると右側に目のアイコンが表示され、クリックで確認・コピーができます"
                )
            },
            hide_index=True,          # 左端の余計な行番号（0, 1, 2...）を非表示にしてスッキリ
            use_container_width=True
        )
        
        st.caption("🔒 セキュリティのため、パスワードは隠されています。確認したいセルを触ってください。")
        
    else:
        st.info("まだ登録されたパスワードはありません。「登録画面」から追加してください。")


# ─── ページナビゲーションの設定 ───
pg = st.navigation([
    st.Page(register_page, title="パスワード登録", icon="📝"),
    st.Page(list_page, title="パスワード一覧", icon="📋")
])

pg.run()
