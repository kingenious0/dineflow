"""
RestaurantTable Model for DineFlow Restaurant Management System.
"""

from datetime import datetime, timezone
from app.extensions import db


class RestaurantTable(db.Model):
    """Physical dining table in the restaurant."""

    __tablename__ = 'restaurant_tables'

    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.String(20), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=4)
    status = db.Column(
        db.Enum('Available', 'Occupied', 'Reserved', name='table_status'),
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
    orders = db.relationship('Order', backref='restaurant_table', lazy='dynamic')

    # ------------------------------------------------------------------ #
    #  Utility
    # ------------------------------------------------------------------ #

    @property
    def is_available(self) -> bool:
        return self.status == 'Available'

    @property
    def active_order(self):
        """Return the current active (open) order for this table, if any."""
        from app.models.order import Order
        return (
            Order.query
            .filter_by(table_id=self.id)
            .filter(Order.status.in_(['Open', 'In Progress']))
            .first()
        )

    def __repr__(self) -> str:
        return f'<RestaurantTable {self.table_number} [{self.status}]>'
