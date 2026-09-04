import google.generativeai as genai  # 画像読み取り（AI OCR）用
import pandas as pd
import streamlit as st
from PIL import Image

# ページの基本設定
st.set_page_config(
    page_title="カンタン収支・請求書・レシートOCRアプリ",
    page_icon="🧾",
    layout="wide",
)

# セッション状態の初期化
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

st.title("🧾 カンタン収支・請求書・レシートOCR管理アプリ")

# タブで機能を分割（レシート読取タブを追加）
tab1, tab2, tab3, tab4 = st.tabs([
    "📥 入出金・家計簿",
    "📸 レシート読取（OCR）",
    "📄 請求書作成",
    "✅ 入金消込",
])

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

# --- 2. レシート読取（OCR）タブ ---
with tab2:
  st.header("レシートを撮影・アップロードして自動入力")
  st.write(
      "スマホのカメラでレシートを撮影するか、画像を選択するとAIが自動で金額や店舗名を読み取ります。"
  )

  # 画像アップロードまたはカメラ入力
  uploaded_file = st.file_uploader(
      "レシート画像を選択", type=["jpg", "jpeg", "png"]
  )
  camera_file = st.camera_input("またはスマホで撮影する")

  target_image = uploaded_file if uploaded_file else camera_file

  if target_image is not None:
    image = Image.open(target_image)
    st.image(image, caption="アップロードされたレシート", use_column_width=True)

    if st.button("レシートを解析する"):
      with st.spinner("レシートを解析中..."):
        try:
          # Google Gemini API等を使ったAI解析のイメージ（簡易デモ用として仮の値を自動セットするかAPIを呼び出します）
          # ※ 実際に動かすには st.secrets 等にAPIキーを設定してください
          # api_key = st.secrets.get("GEMINI_API_KEY")
          # genai.configure(api_key=api_key)
          # model = genai.GenerativeModel('gemini-1.5-flash')
          # response = model.generate_content([image, "このレシートから日付、合計金額、店舗名を抽出してJSON形式で教えて"])

          # 【デモ用】ここでは自動で読み取れたと仮定したプレースホルダー値を表示
          st.success("レシートの解析に成功しました！以下の内容を確認して登録してください。")

          # 解析結果の編集・確認フォーム
          with st.form("ocr_result_form"):
            ocr_date = st.date_input("日付")
            ocr_store = st.text_input("摘要（店舗名など）", value="〇〇ストア")
            ocr_amount = st.number_input(
                "金額（円）", min_value=0, value=1280, step=100
            )
            ocr_category = st.selectbox(
                "勘定科目", ["消耗品費", "仕入高", "水道光熱費", "その他"]
            )

            confirm_btn = st.form_submit_button("この内容で家計簿に登録する")
            if confirm_btn:
              ocr_row = pd.DataFrame({
                  "日付": [ocr_date],
                  "種類": ["支出"],
                  "勘定科目": [ocr_category],
                  "摘要": [ocr_store],
                  "金額": [ocr_amount],
              })
              st.session_state.transactions = pd.concat(
                  [st.session_state.transactions, ocr_row], ignore_index=True
              )
              st.success("レシート内容を家計簿に登録しました！「入出金・家計簿」タブから確認できます。")

        except Exception as e:
          st.error(f"解析に失敗しました: {e}")

# --- 3. 請求書タブ ---
with tab3:
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

# --- 4. 消込タブ ---
with tab4:
  st.header("入金消込（マッチング）")
  st.write("未入金の請求書を1クリックで「入金済」に変えます。")

  if not st.session_state.invoices.empty:
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
          st.session_state.invoices.loc[index, "ステータス"] = "入金済"
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
