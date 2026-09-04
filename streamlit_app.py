import pandas as pd
import streamlit as st

# ページの基本設定
st.set_page_config(
    page_title="カンタン収支・請求書アプリ", page_icon="💰", layout="wide"
)

# セッション状態の初期化（データ保存用）
if "transactions" not in st.session_state:
  st.session_state.transactions = pd.DataFrame(
      columns=["日付", "種類", "勘定科目", "摘要", "金額"]
  )

if "invoices" not in st.session_state:
  st.session_state.invoices = pd.DataFrame(
      columns=[
          "請求書ID",
          "宛先",
          "金額",
          "支払期限",
          "ステータス",
      ]
  )

st.title("💰 カンタン収支・請求書管理アプリ")

# タブで機能を分割
tab1, tab2, tab3 = st.tabs(
    ["📥 入出金・家計簿", "📄 請求書作成", "✅ 入金消込"]
)

# --- 1. 入出金タブ ---
with tab1:
  st.header("入出金・家計簿の入力")
  col1, col2 = st.columns(2)

  with col1:
    with st.form("tx_form"):
      t_date = st.date_input("日付")
      t_type = st.selectbox("種別", ["支出", "収入"])
      t_category = st.selectbox(
          "勘定科目",
          [
              "売上高",
              "消耗品費",
              "旅費交通費",
              "通信費",
              "水道光熱費",
              "その他",
          ],
      )
      t_memo = st.text_input("摘要（メモ）")
      t_amount = st.number_input("金額（円）", min_value=0, step=1000)

      submitted = st.form_submit_button("登録する")
      if submitted:
        new_row = pd.DataFrame({
            "日付": [t_date],
            "種類": [t_type],
            "勘定科目": [t_category],
            "摘要": [t_memo],
            "金額": [t_amount],
        })
        st.session_state.transactions = pd.concat(
            [st.session_state.transactions, new_row], ignore_index=True
        )
        st.success("登録しました！")

  with col2:
    st.subheader("履歴一覧")
    if not st.session_state.transactions.empty:
      st.dataframe(
          st.session_state.transactions, use_container_width=True, hide_index=True
      )
    else:
      st.info("まだデータがありません。")

# --- 2. 請求書タブ ---
with tab2:
  st.header("請求書の作成")
  with st.form("invoice_form"):
    inv_id = st.text_input("請求書番号（例: INV-001）")
    inv_to = st.text_input("宛先（取引先名）")
    inv_amount = st.number_input("請求金額（円）", min_value=0, step=10000)
    inv_limit = st.date_input("支払期限")

    inv_submitted = st.form_submit_button("請求書を発行する")
    if inv_submitted and inv_id and inv_to:
      new_inv = pd.DataFrame({
          "請求書ID": [inv_id],
          "宛先": [inv_to],
          "金額": [inv_amount],
          "支払期限": [inv_limit],
          "ステータス": ["未入金"],
      })
      st.session_state.invoices = pd.concat(
          [st.session_state.invoices, new_inv], ignore_index=True
      )
      st.success(f"請求書 {inv_id} を発行しました（未入金として登録）")

  st.subheader("発行済み請求書一覧")
  if not st.session_state.invoices.empty:
    st.dataframe(
        st.session_state.invoices, use_container_width=True, hide_index=True
    )
  else:
    st.info("発行済みの請求書はありません。")

# --- 3. 消込タブ ---
with tab3:
  st.header("入金消込（マッチング）")
  st.write("未入金の請求書を1クリックで「入金済」に変えます。")

  if not st.session_state.invoices.empty:
    # 未入金のものをフィルタリング
    unpaid_df = st.session_state.invoices[
        st.session_state.invoices["ステータス"] == "未入金"
    ]

    if not unpaid_df.empty:
      for index, row in unpaid_df.iterrows():
        col_a, col_b, col_c = st.columns([3, 3, 2])
        col_a.write(
            f"**{row['請求書ID']}** / 宛先: {row['宛先']} / 金額:"
            f" {row['金額']:,}円"
        )
        col_b.write(f"支払期限: {row['支払期限']}")

        if col_c.button("入金済みにする", key=f"match_{index}"):
          # ステータスを入金済みに変更
          st.session_state.invoices.loc[index, "ステータス"] = "入金済"

          # 自動的に入出金（収入・売上高）データにも反映させる
          auto_income = pd.DataFrame({
              "日付": [pd.Timestamp.today().date()],
              "種類": ["収入"],
              "勘定科目": ["売上高"],
              "摘要": [f"請求書 {row['請求書ID']} の入金"],
              "金額": [row["金額"]],
          })
          st.session_state.transactions = pd.concat(
              [st.session_state.transactions, auto_income], ignore_index=True
          )
          st.rerun()
    else:
      st.success("すべての請求書が入金済みです！ 🎉")
  else:
    st.info("消込対象の請求書がありません。")
