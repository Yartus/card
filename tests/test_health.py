from app.main import create_app

def test_healthz():
    app = create_app()
    client = app.test_client()
    res = client.get('/healthz')
    assert res.status_code == 200