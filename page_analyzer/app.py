import os
from datetime import date

from flask import Flask, render_template, request, url_for, redirect, flash
from dotenv import load_dotenv
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from psycopg2 import pool   # noqa
import psycopg2
import requests

from page_analyzer.validate import url_is_correct

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

conn_pull = psycopg2.pool.SimpleConnectionPool(1, 20, DATABASE_URL)


@app.get('/')
def index():
    return render_template('index.html')


@app.post('/urls')
def add_url():
    url = request.form.get('url')
    if not url_is_correct(url):
        flash('Некорректный URL', 'error')
        return render_template('index.html'), 422
    spread_url = urlparse(url)
    prepared_url = '://'.join([spread_url.scheme, spread_url.netloc])
    conn = conn_pull.getconn()
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name FROM urls
            WHERE name=%s;
            """,
            (prepared_url,)
        )
        added = cursor.fetchall()
        if not added:
            cursor.execute(
                """
                INSERT INTO urls (name, created_at)
                VALUES (%s, %s);
                """,
                (prepared_url, date.today())
            )
            conn.commit()
            cursor.execute(
                """
                SELECT id FROM urls
                WHERE name=%s;
                """,
                (prepared_url,)
            )
            added = cursor.fetchall()
            user_id, = added[0]
            flash('Страница успешно добавлена', 'success')
        else:
            user_id, _ = added[0]
            flash('Страница уже существует', 'warning')
    conn_pull.putconn(conn)
    return redirect(url_for('show_url', id=user_id), code=302)


@app.get('/urls')
def show_all_urls():
    conn = conn_pull.getconn()
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT
            urls.id,
            urls.name AS ulr,
            url_checks.created_at AS last_check,
            url_checks.status_code
            FROM urls
            LEFT JOIN url_checks ON urls.id = url_checks.url_id
            ORDER BY url_checks.created_at DESC;
            """)
        all_urls = cursor.fetchall()
    conn_pull.putconn(conn)
    return render_template('urls/urls.html',
                           urls=all_urls)


@app.get('/urls/<id>')
def show_url(id):
    conn = conn_pull.getconn()
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT name, created_at FROM urls
            WHERE id=%s;
            """,
            (id,)
        )
        url = cursor.fetchall()
        name_url, created_at_url = url[0]
        cursor.execute(
            """
            SELECT id, status_code, h1, title, description, created_at
            FROM url_checks
            WHERE url_id=%s
            ORDER BY created_at DESC;
            """,
            (id,)
        )
        url_check = cursor.fetchall()
    conn_pull.putconn(conn)
    return render_template(
        'urls/show_url.html',
        id_url=id,
        name_url=name_url,
        created_at_url=created_at_url,
        url_check=url_check,
    )


@app.post('/urls/<id>/checks')
def check_url(id):
    conn = conn_pull.getconn()
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT name FROM urls
            WHERE id=%s;
            """,
            (id,)
        )
        url = cursor.fetchone()[0]
        response = requests.get(url)
        try:
            response.raise_for_status()
        except requests.HTTPError:
            flash('Произошла ошибка при проверке', 'error')
            return redirect(url_for('show_url', id=id), code=302)
        soup = BeautifulSoup(response.text, features="html.parser")
        content = str(soup.find('meta', {'name': 'description'})['content'])
        cursor.execute(
            """
            INSERT INTO url_checks
            (url_id, status_code, h1, title, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (
                id, response.status_code, soup.h1.get_text(),
                soup.title.get_text(), content, date.today()
            )
        )
        conn.commit()
    flash('Страница успешно проверена', 'success')
    conn_pull.putconn(conn)
    return redirect(url_for('show_url', id=id), code=302)
