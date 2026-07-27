"""
MenuItem Model for DineFlow Restaurant Management System.
"""

from datetime import datetime, timezone
from app.extensions import db


class MenuItem(db.Model):
    """A food or beverage item available on the restaurant menu."""

    __tablename__ = 'menu_items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(60), nullable=False)   # e.g. Main Course, Appetizer, Beverage, Dessert
    price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(
        db.Enum('Available', 'Unavailable', name='menu_item_status'),
        nullable=False,
        default='Available'
    )
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    order_items = db.relationship('OrderItem', backref='menu_item', lazy='dynamic')

    # ------------------------------------------------------------------ #
    #  Utility
    # ------------------------------------------------------------------ #

    @property
    def is_available(self) -> bool:
        return self.status == 'Available'

    @property
    def price_display(self) -> str:
        return f"{float(self.price):.2f}"

    def __repr__(self) -> str:
        return f'<MenuItem {self.name} @ {self.price}>'
