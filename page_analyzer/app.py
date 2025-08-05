import os
import requests
from . import database
from .parser import get_url_elems
from .validate import url_validate
from flask import Flask, render_template, request, flash, redirect, url_for, make_response  # noqa: E501
from dotenv import load_dotenv


load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/', methods=['GET'])
def index_general():
    return render_template('index.html', url_value='')


@app.route('/', methods=['POST'])
def post_to_root():
    return create_url()


@app.route('/urls', methods=['GET'])
def index_urls():
    urls = database.return_urls()
    return render_template('urls/index.html', urls=urls)


@app.route('/urls', methods=['POST'])
def create_url():
    url_orig = request.form.get('url')
    is_valid, message, result = url_validate(url_orig)
    if is_valid:
        new_id = database.add_in_db(result)
        flash(message, 'success')
        return redirect(url_for('index_url_id', id=new_id))
    else:
        if result is not None:
            flash(message, 'info')
            return redirect(url_for('index_url_id', id=result))
        flash(message, 'danger')
        if request.path == '/':
            return render_template('index.html', url_value=url_orig), 200
        return make_response(render_template('index.html', url_value=url_orig), 422)  # noqa: E501


@app.route('/urls/<int:id>', methods=['GET'])
def index_url_id(id):
    url, checks = database.return_url_checks(id)
    return render_template('urls/show.html', url=url, checks=checks)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_urls(id):
    url = database.get_url(id)
    try:
        h1, title, description, code = get_url_elems(url=url)
        database.insert_into_url_checks(id, code, h1, title, description)
        flash('Страница успешно проверена', 'success')
        return redirect(url_for('index_url_id', id=id))
    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('index_url_id', id=id))
