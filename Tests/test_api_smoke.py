import os
import json
from app import create_app

def make_app():
    os.environ.setdefault('FLASK_ENV', 'testing')
    app = create_app('testing') if 'testing' in ('testing',) else create_app()
    return app

def test_health_endpoint():
    app = make_app()
    with app.test_client() as c:
        rv = c.get('/api/health')
        assert rv.status_code in (200, 503)
        data = rv.get_json()
        assert 'status' in data

def test_openapi_and_docs():
    app = make_app()
    with app.test_client() as c:
        rv = c.get('/api/openapi.json')
        assert rv.status_code == 200
        data = rv.get_json()
        assert data.get('openapi', '').startswith('3')
        rv2 = c.get('/api/docs')
        assert rv2.status_code == 200
        assert b'SwaggerUIBundle' in rv2.data
