from page_analyzer import app

def test_index():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    html_response = response.data.decode('utf-8')
    assert "Анализатор страниц" in html_response
