from flask import Flask, render_template, request, url_for
from dotenv import load_dotenv
from validators import url as is_correct
import os
import psycopg2
from urllib.parse import urlparse
from datetime import datetime

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.get('/')
def index():
    return render_template('index.html')

@app.post('/urls')
def add_url():
    url = request.form.get('url')
    if is_correct(url):
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cursor:
            spread_url = urlparse(url)
            prepared_url = '://'.join([spread_url.scheme, spread_url.netloc])
            cursor.execute("""
                INSERT INTO urls (name, created_at)
                VALUES (%s, %s);
                """,
                (url, datetime.now()))
            conn.commit()
    return request(url_for('index'))



if __name__ == '__main__':
    app.run(port=8080, debug=True)
