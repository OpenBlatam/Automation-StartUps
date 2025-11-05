import os
from app import create_app

def make_app():
    os.environ.setdefault('FLASK_ENV', 'testing')
    app = create_app('testing') if 'testing' in ('testing',) else create_app()
    return app

def login_get_token(c):
    rv = c.post('/api/auth/login', json={'username': 'admin', 'password': 'admin123'})
    assert rv.status_code == 200
    data = rv.get_json()
    return data['token']

def test_products_requires_auth():
    app = make_app()
    with app.test_client() as c:
        rv = c.get('/api/products')
        assert rv.status_code in (401, 403)

def test_products_with_auth():
    app = make_app()
    with app.test_client() as c:
        token = login_get_token(c)
        rv = c.get('/api/products', headers={'Authorization': f'Bearer {token}'})
        assert rv.status_code == 200
        # Response can be list or paginated dict
        if rv.is_json:
            data = rv.get_json()
            assert isinstance(data, (list, dict))
