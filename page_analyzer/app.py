import psycopg2
import os
from flask import Flask, render_template, request, flash, redirect, url_for, abort
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

def get_connection():
    return psycopg2.connect(DATABASE_URL)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route('/', methods = ['GET', 'POST'])
def index_general():
    def url_validate(url):
        parsed_url = urlparse(url)
        if parsed_url.scheme not in ('http', 'https') or not parsed_url.netloc:
            return False, 'Некорректный URL', None
        if len(url)>255:
            return False, 'URL слишком длинный (максимум 255 символов)', None
        url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM urls WHERE name = %s", (url,))
                if cur.fetchone():
                    return False, 'Страница уже существует', None
        return True, 'Страница успешно добавлена', url
    if request.method=='GET':
        return render_template('index.html')
    else:
        form = request.form
        url_orig = form.get('url')
        is_valid, message, url = url_validate(url_orig)
        if is_valid:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO urls (name) VALUES (%s) RETURNING id", (url,))
                    new_id = cur.fetchone()[0]
                    conn.commit()
            flash(message, 'success')
            return redirect(url_for('index_url_id', id=new_id))
        flash(message, 'danger')
        return redirect(url_for('index_general'))

@app.route('/urls', methods = ['GET'])
def index_urls():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, created_at FROM urls ORDER BY id ASC")
            urls = cur.fetchall()
    return render_template('urls/index.html', urls=urls)

@app.route('/urls/<int:id>', methods = ['GET'])
def index_url_id(id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, created_at::date FROM urls WHERE id = %s;", (id,))
            row = cur.fetchone()
            if row is None:
                abort(404)
            url = {
            'id': row[0],
            'name': row[1],
            'created_at': row[2]
            }
            cur.execute("""
                SELECT id, status_code, h1, title, description, created_at::date
                FROM url_checks
                WHERE url_id = %s
                ORDER BY created_at DESC
            """, (id,))
            checks = cur.fetchall()
    return render_template('urls/show.html', url=url, checks=checks)


@app.route('/urls/<int:id>/checks', methods = ['POST'])
def check_urls(id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO url_checks (url_id) VALUES (%s) RETURNING id", (id,))
            check_id = cur.fetchone()[0]
            conn.commit()
    flash('Проверка успешно создана', 'success')
    return redirect(url_for('index_url_id', id=id))


@app.route('/test-db')
def test_db():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT 1;')
                result = cur.fetchone()
        return f'Подключение к БД успешно! Результат запроса: {result[0]}'
    except Exception as e:
        return f'Ошибка подключения к БД: {e}'
