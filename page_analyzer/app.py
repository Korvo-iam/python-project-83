import os
from . import sql_commands
from flask import Flask, render_template, request, flash, redirect, url_for
from dotenv import load_dotenv
from urllib.parse import urlparse
from bs4 import BeautifulSoup
#import validators
import requests


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

def url_validate(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme not in ('http', 'https') or not parsed_url.netloc:
        return False, 'Некорректный URL', None
    if len(url)>255:
        return False, 'URL слишком длинный (максимум 255 символов)', None
    url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    existing_id = sql_commands.check_if_in_db(url)
    if sql_commands.check_if_in_db(url):
        return False, 'Страница уже существует', existing_id
    return True, 'Страница успешно добавлена', url

@app.route('/', methods = ['GET', 'POST'])
def index_general():
    if request.method=='GET':
        return render_template('index.html')
    else:
        url_orig = request.form.get('url')
        is_valid, message, result = url_validate(url_orig)
        if is_valid:
            new_id = sql_commands.add_in_db(result)
            flash(message, 'success')
            return redirect(url_for('index_url_id', id=new_id))
        else:
            if result is not None:  # id существующего сайта
                flash(message, 'info')
                return redirect(url_for('index_url_id', id=result))
            flash(message, 'danger')
            return redirect(url_for('index_general'))


@app.route('/urls', methods = ['GET'])
def index_urls():
    urls = sql_commands.return_urls()
    return render_template('urls/index.html', urls=urls)

@app.route('/urls/<int:id>', methods = ['GET'])
def index_url_id(id):
    url, checks = sql_commands.return_url_checks(id)
    return render_template('urls/show.html', url=url, checks=checks)

@app.route('/urls/<int:id>/checks', methods = ['POST'])
def check_urls(id):
    url = sql_commands.get_url(id)
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        h1 = soup.h1.string if soup.h1 else ''
        title = soup.title.string if soup.title else ''
        description_tag = soup.find('meta', attrs={'name': 'description'})
        description = description_tag['content'] if description_tag and 'content' in description_tag.attrs else ''
        sql_commands.insert_into_url_checks(id, response.status_code, h1, title, description)
        flash('Страница успешно проверена', 'success')
        return redirect(url_for('index_url_id', id=id))
    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('index_url_id', id=id))

@app.route('/test-db')
def test_db():
    try:
        with sql_commands.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT 1;')
                result = cur.fetchone()
        return f'Подключение к БД успешно! Результат запроса: {result[0]}'
    except Exception as e:
        return f'Ошибка подключения к БД: {e}'
