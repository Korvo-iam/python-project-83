import validators
from . import database
from urllib.parse import urlparse


def url_validate(url):
    MAX_URL_LENGTH = 255
    if not validators.url(url):
        return False, 'Некорректный URL', None
    if len(url) > MAX_URL_LENGTH:
        return False, f'URL слишком длинный (максимум {MAX_URL_LENGTH} символов)', None  # noqa: E501
    parsed_url = urlparse(url)
    short_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    existing_id = database.check_if_in_db(short_url)
    if existing_id:
        return False, 'Страница уже существует', existing_id
    return True, 'Страница успешно добавлена', short_url
