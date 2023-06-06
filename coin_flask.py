from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    message = "가상화폐추천 서비스입니다."
    return render_template('index.html', message=message)

@app.route('/data')
def data():
    # SQLite3 데이터베이스 연결
    conn = sqlite3.connect('coin_data.db')
    cursor = conn.cursor()

    # 코인 테이블 목록 조회
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    coin_tables = [table[0] for table in cursor.fetchall()]

    all_data = []
    
    for coin_name in coin_tables:
        # 데이터 조회
        query = f"SELECT * FROM {coin_name}"
        cursor.execute(query)
        rows = cursor.fetchall()

        # 데이터 가공
        table_data = []
        for row in rows:
            table_data.append({'name': row[0], 'price': row[1], 'volume': row[2], 'timestamp': row[3]})
        
        all_data.append({'coin_name': coin_name, 'data': table_data})

    # 테이블로 데이터 반환
    return render_template('data.html', all_data=all_data)

@app.route('/graph')
def graph_page():
    return render_template('graph.html')

@app.route('/graph/<coin_name>')
def graph_coin(coin_name):
    return render_template('graph_coin.html', coin_name=coin_name)


@app.route('/get_data_json')
def get_data_json():
    conn = sqlite3.connect('coin_data.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    coin_tables = [table[0] for table in cursor.fetchall()]

    all_data = []
    
    for coin_name in coin_tables:
        query = f"SELECT * FROM {coin_name}"
        cursor.execute(query)
        rows = cursor.fetchall()

        table_data = []
        for row in rows:
            table_data.append({'name': row[0], 'price': row[1], 'volume': row[2], 'timestamp': row[3]})
        
        all_data.append({'coin_name': coin_name, 'data': table_data})

    return jsonify(all_data)

    
if __name__ == '__main__':
    app.run()