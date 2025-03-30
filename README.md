# 企業分析アプリケーション

このプロジェクトは、企業の株価データを取得し、分析するためのアプリケーションです。Streamlitを使用してインタラクティブなUIを提供し、GoogleのGenerative AIを利用して企業情報を取得します。

## 環境設定手順

1. 必要なパッケージのインストール:
   ```bash
   pip install -r requirements.txt
   ```

2. 環境変数の設定:
   - `.env`ファイルを作成し、Google APIキーを設定します。
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

3. データファイルの配置:
   - `data/data_j.csv`をプロジェクトディレクトリに配置します。

## アプリケーションの実行方法

1. Streamlitアプリの起動:
   ```bash
   streamlit run src/app.py
   ```

## 使用方法

- Streamlitアプリを起動すると、企業名を選択し、株価データや企業情報を表示することができます。
- 企業情報はGoogle Generative AIを使用して取得され、マークダウン形式で表示されます。
- 株価データはyfinanceを使用して取得され、グラフとして表示されます。

## 依存関係

- Python 3.x
- Streamlit
- yfinance
- google-generativeai
- dotenv
- pandas
- matplotlib

このアプリケーションは、企業の株価と情報を簡単に比較・分析するためのツールです。