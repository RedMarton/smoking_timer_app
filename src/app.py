import os
import time
import psycopg2
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta

# Flaskアプリケーションのインスタンスをここで定義します
app = Flask(__name__)

# 環境変数からデータベース接続情報を取得
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')

def get_db_connection():
    """データベース接続を確立する関数 (リトライロジック付き)"""
    max_retries = 5
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                dbname=db_name
            )
            print(f"データベースに接続しました！ (試行回数: {i + 1})")
            return conn
        except psycopg2.OperationalError as e:
            print(f"データベース接続エラーが発生しました: {e}")
            if i < max_retries - 1:
                print(f"{i + 1}回目: 接続を再試行します...")
                time.sleep(2) # 2秒待機
            else:
                print("最大試行回数に達しました。")
                raise # 再試行しても失敗した場合は例外を再スロー

def get_last_smoking_time():
    """データベースから前回の喫煙時間を取得する関数"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # 最新の記録を1件取得
        cur.execute("SELECT timestamp FROM smoking_records ORDER BY timestamp DESC LIMIT 1")
        result = cur.fetchone()
        cur.close()
        if result:
            return result[0]
        else:
            return None
    except Exception as e:
        print(f"データベースから前回の喫煙時間の取得に失敗しました: {e}")
        return None
    finally:
        if conn:
            conn.close()

@app.route('/')
def index():
    """トップページを表示する関数"""
    last_time = get_last_smoking_time()
    return render_template('index.html', last_time=last_time)

@app.route('/record_smoking', methods=['POST'])
def record_smoking():
    """喫煙記録をデータベースに保存する関数"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # テーブルが存在しなければ作成
        cur.execute("""
            CREATE TABLE IF NOT EXISTS smoking_records (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # 記録を挿入
        cur.execute("INSERT INTO smoking_records DEFAULT VALUES")
        conn.commit()
        cur.close()
        return jsonify(message="記録が保存されました！"), 200
    except Exception as e:
        print(f"データベースエラー: {e}")
        return jsonify(message="記録の保存に失敗しました。"), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0')
