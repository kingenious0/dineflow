"""
OrderItem Model for DineFlow Restaurant Management System.
"""

from app.extensions import db


class OrderItem(db.Model):
    """A single line item (menu item + quantity) within an order."""

    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=False)

    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)   # Price at time of order
    notes = db.Column(db.String(200), nullable=True)            # e.g. "No chilli"

    # ------------------------------------------------------------------ #
    #  Computed helpers
    # ------------------------------------------------------------------ #

    @property
    def line_total(self) -> float:
        return round(float(self.unit_price) * self.quantity, 2)

    @property
    def item_name(self) -> str:
        return self.menu_item.name if self.menu_item else 'Unknown Item'

    def __repr__(self) -> str:
        return f'<OrderItem {self.item_name} x{self.quantity}>'
