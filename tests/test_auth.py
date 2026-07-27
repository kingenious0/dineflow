"""
Unit tests for DineFlow Authentication and RBAC.
"""

import pytest
from app import create_app
from app.extensions import db
from app.models import User


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        admin = User(full_name="Admin Test", email="admin@test.com", role="Administrator")
        admin.set_password("Password123!")
        db.session.add(admin)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_login_logout(client):
    # Test valid login
    response = client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'Password123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Dashboard' in response.data or b'Welcome back' in response.data

    # Test logout
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Sign In' in response.data


def test_invalid_login(client):
    response = client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'WrongPassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data
