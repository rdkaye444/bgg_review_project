from fastapi.testclient import TestClient

def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to FastAPI MonsterUI App" in response.text

def test_static_css(client):
    response = client.get("/static/css/style.css")
    assert response.status_code == 200
    assert "container" in response.text 