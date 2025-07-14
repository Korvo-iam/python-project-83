from page_analyzer import app

def test_index():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b'Project 83 has been deployed' in response.data