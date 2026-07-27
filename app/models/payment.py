"""
Payment Model for DineFlow Restaurant Management System.
"""

from datetime import datetime, timezone
from app.extensions import db


class Payment(db.Model):
    """Payment record attached to a completed order."""

    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), unique=True, nullable=False)

    amount_paid = db.Column(db.Numeric(10, 2), nullable=False)
    change_given = db.Column(db.Numeric(10, 2), default=0.00)
    payment_method = db.Column(
        db.Enum('Cash', 'Mobile Money', 'Card', 'Complimentary', name='payment_method'),
        nullable=False,
        default='Cash'
    )
    status = db.Column(
        db.Enum('Completed', 'Refunded', name='payment_status'),
        nullable=False,
        default='Completed'
    )
    reference = db.Column(db.String(100), nullable=True)   # MoMo transaction ID etc.
    notes = db.Column(db.Text, nullable=True)
    processed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    paid_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship to user who processed the payment
    cashier = db.relationship('User', foreign_keys=[processed_by])

    def __repr__(self) -> str:
        return f'<Payment Order#{self.order_id} {self.payment_method} {self.amount_paid}>'
