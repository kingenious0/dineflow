"""
Unit tests for DineFlow Orders and Payments logic.
"""

import pytest
from app import create_app
from app.extensions import db
from app.models import User, MenuItem, RestaurantTable, Order, OrderItem, Setting


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        # Seed settings
        setting = Setting(business_name="Test Diner", tax_rate=0.0)
        db.session.add(setting)

        # Seed staff user
        staff = User(full_name="Cashier Test", email="cashier@test.com", role="Cashier")
        staff.set_password("Password123!")
        db.session.add(staff)

        # Seed menu item & table
        item = MenuItem(name="Test Burger", category="Main Course", price=20.00, status="Available")
        table = RestaurantTable(table_number="T10", capacity=4, status="Available")
        db.session.add_all([item, table])

        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_order_creation_and_recalculation(app):
    with app.app_context():
        order = Order(order_number="ORD-99999", order_type="Dine-In", status="Open")
        db.session.add(order)
        db.session.flush()

        item = MenuItem.query.first()
        oi = OrderItem(order_id=order.id, menu_item_id=item.id, quantity=2, unit_price=item.price)
        db.session.add(oi)
        db.session.flush()

        order.recalculate_totals(tax_rate=0.0)
        db.session.commit()

        assert float(order.subtotal) == 40.00
        assert float(order.total_amount) == 40.00
        assert order.total_items == 2
