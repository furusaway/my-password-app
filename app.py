import streamlit as st
import pandas as pd

# ページ全体の初期設定
st.set_page_config(page_title="🔐 パスワード管理アプリ", page_icon="🔐", layout="centered")

# ─── 🔑 セキュリティ設定 ───
# あなただけの「マスターパスワード（暗証番号）」をここで決めます。
# ※ 以下の "1234" を、あなただけが知っている好きな数字や英単語に書き換えてください！
MASTER_PASSWORD = "1234"


# データを保存するデータ箱（セッション状態）の準備
if "password_list" not in st.session_state:
    st.session_state.password_list = []

# ロック状態を管理するフラグ（最初はロックされている状態）
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
            new_data = {"サービス名": service_name, "パスワード": password}
            st.session_state.password_list.append(new_data)
            st.success(f"🎉 {service_name} のパスワードを登録しました！")
        else:
            st.warning("⚠️ サービス名とパスワードの両方を入力してください。")


# ─── ページ2: パスワード一覧画面（ロック機能付き） ───
def list_page():
    st.title("📋 登録済みパスワード一覧")
    
    # 【重要】ロックが解除されていない場合、入力フォームを表示する
    if not st.session_state.is_unlocked:
        st.warning("🔒 このページを表示するには暗証番号が必要です。")
        
        # 暗証番号の入力欄（入力中は非表示になります）
        input_pin = st.text_input("マスターパスワードを入力してください", type="password")
        unlocked_button = st.button("ロックを解除")
        
        if unlocked_button:
            if input_pin == MASTER_PASSWORD:
                st.session_state.is_unlocked = True
                st.rerun()  # 画面を再描画して一覧を表示
            else:
                st.error("❌ 暗証番号が違います。アクセスを拒否しました。")
                
        # ロック中はこの下のコード（一覧表示）を絶対に実行させない
        return 

    # ─── ここから下は、ロックが解除された時だけ表示される ───
    st.success("🔓 ロックが解除されました。")
    
    # 簡易的な「再ロック」ボタン（見終わったらすぐ隠せる）
    if st.button("🔴 すぐに再ロックする"):
        st.session_state.is_unlocked = False
        st.rerun()
        
    st.markdown("---")

    if st.session_state.password_list:
        df = pd.DataFrame(st.session_state.password_list)
        
        st.dataframe(
            df,
            column_config={
                "パスワード": st.column_config.TextColumn("パスワード")
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
