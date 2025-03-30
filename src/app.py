import streamlit as st
import pandas as pd
import yfinance as yf
import google.generativeai as genai
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import json
from datetime import datetime

# ページ設定
st.set_page_config(layout="wide")

# カスタムCSSの追加
st.markdown("""
    <style>
    .main {
        background-color: #f9f9f9;  /* 背景色を淡いグレーに設定 */
    }
    .stButton>button {
        background-color: #007BFF;  /* ボタンを青色に設定 */
        color: white;
        font-size: 16px;  /* フォントサイズを大きく */
        border-radius: 5px;  /* ボタンの角を丸く */
    }
    .stSelectbox, .stNumberInput {
        background-color: #ffffff;  /* 入力フィールドを白に設定 */
        font-size: 16px;  /* フォントサイズを大きく */
    }
    .highlight {
        color: #FF5733;  /* 強調したい文字の色 */
        font-weight: bold;  /* 太字 */
    }
    h1, h2, h3, h4, h5, h6 {
        color: #333333;  /* 見出しの色を濃いグレーに設定 */
    }
    </style>
    """, unsafe_allow_html=True)

# .envファイルから環境変数をロード
load_dotenv()

# 定数の定義
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-1.5-flash"  # モデル名を定数として定義

# Gemini API の設定
genai.configure(api_key=GOOGLE_API_KEY)

# 企業リストの読み込み
try:
    stocklist = pd.read_csv("./data/data_j.csv", encoding="shift_jis")
    # print(stocklist)
    # stocklist = stocklist.loc[stocklist["市場・商品区分"]=="市場第一部（内国株）",
    stocklist = stocklist.loc[stocklist["市場・商品区分"]=="プライム（内国株式）",
                  ["コード","銘柄名","33業種コード","33業種区分","規模コード","規模区分"]
                 ]
    stocklist["銘柄名"] = stocklist["銘柄名"].str.strip()
except FileNotFoundError:
    st.error("銘柄リストファイル 'data_j.csv' が見つかりません。")
    st.stop()
except Exception as e:
    st.error(f"銘柄リストファイルの読み込み中にエラーが発生しました: {e}")
    st.stop()
# print(stocklist)

def get_company_info(company_name):
    """
    Gemini APIを使用して企業情報を取得し、マークダウン形式で返す。
    """
    model = genai.GenerativeModel(MODEL_NAME)
    prompt = f"""
    {company_name}について、以下の情報をマークダウン形式で出力してください。各項目は200文字程度にし、強調したい部分は**で囲んでください。
    - **事業概要**: 事業概要の内容
    - **来歴**: 来歴の内容
    - **企業特色**: 企業特色の内容
    - **主力製品**: 主力製品の内容
    """
    try:
        response = model.generate_content(prompt)
        return response.text  # マークダウン形式のテキストをそのまま返す
    except Exception as e:
        return f"企業情報の取得に失敗しました: {e}"

def get_ticker_symbol(company_code):
    """
    企業コードからティッカーシンボルを生成する。

    Args:
        company_code (str): 企業コード。

    Returns:
        str: ティッカーシンボル。
    """
    return str(company_code) + ".T"

def get_stock_data(ticker, start_year, end_year):
    """
    yfinance APIを使用して株価データを取得する（年度指定）。

    Args:
        ticker (str): 企業のティッカーシンボル。
        start_year (int): 開始年度 (例: 2023)。
        end_year (int): 終了年度 (例: 2024, 空欄の場合は開始年度と同年度)。

    Returns:
        pandas.DataFrame: 株価データを含むDataFrame。
        str: エラーメッセージ。見つからない場合は None。
    """
    if end_year is None:
        end_year = start_year

    start_date = f"{start_year-1}-04-01"
    end_date = f"{end_year}-03-31"
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            return None, f"データ取得エラー: {ticker} の {start_year}年度から{end_year}年度のデータが見つかりませんでした。"
        return data, None
    except Exception as e:
        return None, f"データ取得エラー: {e}"

def plot_stock_data(data, ticker):
    """
    株価データをグラフ化する。

    Args:
        data (pandas.DataFrame): 株価データを含むDataFrame。
        ticker (str): 企業のティッカーシンボル。
    """
    if data is None or data.empty:
        return None

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(data['Close'], label='終値')
    ax.set_title(f'{ticker}の株価推移', fontname="MS Gothic")
    ax.set_xlabel('日付', fontname="MS Gothic")
    ax.set_ylabel('株価 (USD)', fontname="MS Gothic")
    ax.legend(prop={'family': 'MS Gothic'})
    ax.grid(True)
    return fig

def generate_graph_title(company_name, start_date, end_date):
    """
    Gemini APIを使用してグラフのタイトルを生成する。

    Args:
        company_name (str): 企業名。
        start_date (str): データの開始日 (YYYY-MM-DD形式)。
        end_date (str): データの終了日 (YYYY-MM-DD形式)。

    Returns:
        str: グラフのタイトル。
    """
    model = genai.GenerativeModel(MODEL_NAME)
    prompt = f"{company_name}の{start_date}から{end_date}までの株価推移を示すグラフのタイトルを考えてください。"
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "グラフタイトルの生成に失敗しました。"

def compare_companies(company1_info_md, company2_info_md):
    """
    2つの企業の情報を比較する。

    Args:
        company1_info_md (str): 1社目の企業情報（マークダウン形式）。
        company2_info_md (str): 2社目の企業情報（マークダウン形式）。

    Returns:
        str: 比較結果。
    """
    model = genai.GenerativeModel(MODEL_NAME)
    prompt = f"""
    以下の2社の相違点と共通点を比較してください。
    比較する項目は、事業内容、規模、経営理念です。
    強調したい部分は**で囲んでください。

    1社目:
    {company1_info_md}

    2社目:
    {company2_info_md}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # エラーの詳細をログに記録
        print(f"Error during comparison: {e}")
        return "企業情報の比較に失敗しました。"

def fetch_company_data(ticker):
    """
    指定されたティッカーシンボルの企業データを取得する。
    """
    try:
        # データ取得の処理
        data = get_data_from_source(ticker)
