"""
Unit tests for DineFlow Reports & CSV Export functionality.
"""

import pytest
from app import create_app
from app.extensions import db
from app.models import User, Setting, Order, MenuItem, OrderItem


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        # Seed settings
        setting = Setting(business_name="Test Diner", tax_rate=0.0)
        db.session.add(setting)

        # Seed manager user
        manager = User(full_name="Manager Test", email="manager@test.com", role="Manager")
        manager.set_password("Password123!")
        db.session.add(manager)

        # Seed order
        item = MenuItem(name="Burger", category="Main Course", price=25.00, status="Available")
        db.session.add(item)
        db.session.flush()

        order = Order(order_number="ORD-00001", order_type="Dine-In", status="Completed", total_amount=25.00)
        db.session.add(order)
        db.session.flush()

        oi = OrderItem(order_id=order.id, menu_item_id=item.id, quantity=1, unit_price=25.00)
        db.session.add(oi)

        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    client = app.test_client()
    # Login as manager
    client.post('/auth/login', data={'email': 'manager@test.com', 'password': 'Password123!'})
    return client


def test_sales_report_csv_export(client):
    response = client.get('/reports/sales/export-csv')
    assert response.status_code == 200
    assert response.content_type.startswith('text/csv')
    assert b'DineFlow Restaurant - Sales Report' in response.data


def test_menu_report_csv_export(client):
    response = client.get('/reports/menu/export-csv')
    assert response.status_code == 200
    assert response.content_type.startswith('text/csv')
    assert b'DineFlow Restaurant - Menu Item Performance Report' in response.data
    assert b'Burger' in response.data
