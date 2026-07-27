"""
Order Model for DineFlow Restaurant Management System.
"""

from datetime import datetime, timezone
from app.extensions import db


class Order(db.Model):
    """A customer order — dine-in, takeaway, or delivery."""

    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False, index=True)

    # Foreign Keys
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    table_id = db.Column(db.Integer, db.ForeignKey('restaurant_tables.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    order_type = db.Column(
        db.Enum('Dine-In', 'Takeaway', 'Delivery', name='order_type'),
        nullable=False,
        default='Dine-In'
    )
    status = db.Column(
        db.Enum('Open', 'In Progress', 'Ready', 'Completed', 'Cancelled', name='order_status'),
        nullable=False,
        default='Open'
    )

    subtotal = db.Column(db.Numeric(10, 2), default=0.00)
    tax_amount = db.Column(db.Numeric(10, 2), default=0.00)
    discount_amount = db.Column(db.Numeric(10, 2), default=0.00)
    total_amount = db.Column(db.Numeric(10, 2), default=0.00)

    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy='select', cascade='all, delete-orphan')
    payment = db.relationship('Payment', backref='order', uselist=False, cascade='all, delete-orphan')
    receipt = db.relationship('Receipt', backref='order', uselist=False, cascade='all, delete-orphan')

    # ------------------------------------------------------------------ #
    #  Utility
    # ------------------------------------------------------------------ #

    @property
    def is_paid(self) -> bool:
        return self.payment is not None and self.payment.status == 'Completed'

    @property
    def total_items(self) -> int:
        return sum(item.quantity for item in self.items)

    def recalculate_totals(self, tax_rate: float = 0.00) -> None:
        """Recalculate subtotal, tax, and total from line items."""
        subtotal = sum(item.line_total for item in self.items)
        tax = round(subtotal * tax_rate, 2)
        self.subtotal = subtotal
        self.tax_amount = tax
        self.total_amount = round(subtotal + tax - float(self.discount_amount or 0), 2)

    def __repr__(self) -> str:
        return f'<Order {self.order_number} [{self.status}]>'
