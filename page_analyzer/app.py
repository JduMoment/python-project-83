from flask import Flask, render_template, request, url_for, redirect
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
        spread_url = urlparse(url)
        prepared_url = '://'.join([spread_url.scheme, spread_url.netloc])
        with conn.cursor() as cursor:
            if len(prepared_url) < 255:
                cursor.execute("""
                    INSERT INTO urls (name, created_at)
                    VALUES (%s, %s);
                    """, (url, datetime.today()))
                conn.commit()
    return redirect(url_for('show_all_urls'), code=200)

@app.get('/urls')
def show_all_urls():
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT id, name FROM urls
            ORDER BY id DESC""")
        all_urls = cursor.fetchall()
        return render_template('urls/urls.html',
                                urls=all_urls)


@app.get('/urls/<id>')
def show_url(id):
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute("""
        SELECT name, created_at FROM urls
        WHERE id=%s; """, (id,))
        url = cursor.fetchall()
        name_url, created_at_url = url[0]
        cursor.execute("""
        SELECT id, created_at FROM url_checks
        WHERE url_id=%s; """, (id,))
        url_check = cursor.fetchall()
        id_check, created_at_check = url_check[0]
        return render_template(
            'urls/show_url.html',
            id_url=id,
            name_url=name_url,
            created_at_url=created_at_url,
            id_check=id_check,
            created_at_check=created_at_check,
        )

@app.get('urls/<id>/checks')
def check_url(id):
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute("""
        INSERT INTO urls (url_id,created_at)
        VALUES (%s, %s);
        """, (id, datetime.today()))
        conn.commit()
    return redirect(url_for('show_url'), code=200)




if __name__ == '__main__':
    app.run(port=8080, debug=True)
