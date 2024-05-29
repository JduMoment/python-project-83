import os
from datetime import date

from flask import Flask, render_template, request, url_for, redirect, flash
from dotenv import load_dotenv
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from psycopg2 import pool   # noqa
import psycopg2
import requests

from page_analyzer.sql_queries import (
    get_url_id,
    insert_url,
    get_url_list,
    get_url_name_and_date,
    get_url_info,
    insert_url_check,
    get_url_name,
)
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
        return render_template('index.html'), 422
    spread_url = urlparse(url)
    prepared_url = '://'.join([spread_url.scheme, spread_url.netloc])
    with conn_pull.getconn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(get_url_id(prepared_url))
            added = cursor.fetchall()
            if added:
                url_id, = added[0]
                flash('Страница уже существует', 'warning')
                return redirect(url_for('show_url', id=url_id), code=302)
            cursor.execute(insert_url(prepared_url, date.today()))
            conn.commit()
            cursor.execute(get_url_id(prepared_url))
            added = cursor.fetchall()
            url_id, = added[0]
            flash('Страница успешно добавлена', 'success')
    return redirect(url_for('show_url', id=url_id), code=302)


@app.get('/urls')
def show_all_urls():
    with conn_pull.getconn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(get_url_list())
            all_urls = cursor.fetchall()
    return render_template('urls/urls.html',
                           urls=all_urls)


@app.get('/urls/<id>')
def show_url(id):
    with conn_pull.getconn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(get_url_name_and_date(id))
            url = cursor.fetchall()
            name_url, created_at_url = url[0]
            cursor.execute(get_url_info(id))
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
    with conn_pull.getconn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(get_url_name(id))
            url = cursor.fetchone()[0]
            response = requests.get(url)
            try:
                response.raise_for_status()
            except requests.HTTPError:
                flash('Произошла ошибка при проверке', 'error')
                conn_pull.putconn(conn)
                return redirect(url_for('show_url', id=id), code=302)
            soup = BeautifulSoup(response.text, features="html.parser")
            content = str(soup.find('meta', {'name': 'description'})['content'])
            cursor.execute(insert_url_check(id, response.status_code, soup.h1.string,
                                            soup.title.string, content, date.today()))
            conn.commit()
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('show_url', id=id), code=302)
