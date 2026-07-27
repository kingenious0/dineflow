"""
Customer Model for DineFlow Restaurant Management System.
"""

from datetime import datetime, timezone
from app.extensions import db


class Customer(db.Model):
    """Walk-in or registered restaurant customer."""

    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    orders = db.relationship('Order', backref='customer', lazy='dynamic')

    # ------------------------------------------------------------------ #
    #  Utility
    # ------------------------------------------------------------------ #

    @property
    def total_orders(self) -> int:
        return self.orders.count()

    @property
    def total_spent(self):
        from app.models.order import Order
        result = (
            db.session.query(db.func.sum(Order.total_amount))
            .filter(Order.customer_id == self.id, Order.status.in_(['Completed', 'Paid']))
            .scalar()
        )
        return result or 0.0

    def __repr__(self) -> str:
        return f'<Customer {self.full_name}>'
