"""
Receipt Model for DineFlow Restaurant Management System.
"""

from datetime import datetime, timezone
from app.extensions import db


class Receipt(db.Model):
    """A formal receipt document generated after payment."""

    __tablename__ = 'receipts'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), unique=True, nullable=False)
    receipt_number = db.Column(db.String(30), unique=True, nullable=False, index=True)

    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), default=0.00)
    discount_amount = db.Column(db.Numeric(10, 2), default=0.00)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)

    payment_method = db.Column(db.String(30), nullable=False)
    amount_paid = db.Column(db.Numeric(10, 2), nullable=False)
    change_given = db.Column(db.Numeric(10, 2), default=0.00)

    issued_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    issued_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationship
    cashier = db.relationship('User', foreign_keys=[issued_by])

    def __repr__(self) -> str:
        return f'<Receipt {self.receipt_number}>'
