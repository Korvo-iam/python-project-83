from page_analyzer import app
app.config['SECRET_KEY'] = 'test_secret_key'


def test_index():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    html_response = response.data.decode('utf-8')
    assert "Анализатор страниц" in html_response


def test_add_url(monkeypatch):
    
    class url:
        def __init__(self, id):
            self.id = id
    mock_url = url(id=2)
    client = app.test_client()
    monkeypatch.setattr('page_analyzer.sql_commands.check_if_in_db', lambda url: None)  # noqa: E501
    monkeypatch.setattr('page_analyzer.sql_commands.add_in_db', lambda url: 999)
    monkeypatch.setattr('page_analyzer.sql_commands.return_url_checks', lambda id:(mock_url,[]))  # noqa: E501
    response = client.post('/', data={'url': 'https://example.com'}, follow_redirects=True)  # noqa: E501
    assert response.status_code == 200
    assert "Страница успешно добавлена" in response.data.decode('utf-8')


def test_add_incorrect_url():
    client = app.test_client()
    response = client.post('/', data={'url': 'not a url'}, follow_redirects=True)
    assert response.status_code == 200
    assert "Некорректный URL" in response.data.decode('utf-8')


def test_urls_list(monkeypatch):
    client = app.test_client()
    fake_urls = [(1, 'https://example.com', '2025-07-27', 200)]
    monkeypatch.setattr('page_analyzer.sql_commands.return_urls', lambda: fake_urls)
    response = client.get('/urls')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert "https://example.com" in html


def test_url_detail(monkeypatch):
    client = app.test_client()
    
    class url:
        def __init__(self, id):
            self.id = id
    mock_url = url(id=69)
    mock_checks = [(1, 200, 'Анализатор страниц', 'Page analyzer', 'h1teg', '2025-07-28')]
    monkeypatch.setattr('page_analyzer.sql_commands.return_url_checks', lambda id: (mock_url, mock_checks))  # noqa: E501
    response = client.get('/urls/69')
    assert response.status_code == 200
    assert 'Анализатор страниц' in response.data.decode('utf-8')
    assert 'Page analyzer' in response.data.decode('utf-8')
    assert 'h1teg' in response.data.decode('utf-8')
