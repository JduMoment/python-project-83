from flask import Flask, render_template, request, url_for, redirect, flash
from dotenv import load_dotenv
from validators import url as is_correct
import os
import psycopg2
from urllib.parse import urlparse
from datetime import date
import requests
from bs4 import BeautifulSoup

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
            cursor.execute("""SELECT name FROM urls
            WHERE name = %s;""", (prepared_url,))
            added_earlier = cursor.fetchall()
            if not added_earlier and len(prepared_url) < 255:
                cursor.execute("""
                    INSERT INTO urls (name, created_at)
                    VALUES (%s, %s);
                    """, (url, date.today()))
                conn.commit()
                flash('Страница успешно добавлена', 'success')
                return redirect(url_for('show_all_urls'), code=200)
            else:
                flash('Страница уже добавлена', 'warning')
                return redirect(url_for('show_all_urls'), code=200)
    flash('Некорректный URL', 'error')
    return redirect(url_for('index'))


@app.get('/urls')
def show_all_urls():
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute("""
        SELECT DISTINCT urls.id, urls.name as ulr, url_checks.created_at as last_check
        FROM urls
        LEFT JOIN url_checks ON urls.id = url_checks.url_id
        ORDER BY url_checks.created_at DESC""")
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
        SELECT id, status_code, h1, title, description, created_at FROM url_checks
        WHERE url_id=%s; """, (id,))
        url_check = cursor.fetchall()
        return render_template(
            'urls/show_url.html',
            id_url=id,
            name_url=name_url,
            created_at_url=created_at_url,
            url_check=url_check,
        )


@app.post('/urls/<id>/checks')
def check_url(id):
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute("""
        SELECT name FROM urls
        WHERE id=%s;""", (id,))
        url = cursor.fetchone()[0]
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text)
        content = str(soup.find('meta', {'name': 'description'})['content'])
        cursor.execute("""
        INSERT INTO url_checks (url_id, status_code, h1, title, description, created_at)
        VALUES (%s, %s, %s, %s, %s, %s);
        """, (id, response.status_code, soup.h1.get_text(),
              soup.title.get_text(), content, date.today()))
        conn.commit()
    return redirect(url_for('show_url', id=id), code=200)


if __name__ == '__main__':
    app.run(port=8080, debug=True)
