"""
Setting Model for DineFlow Restaurant Management System.
Singleton table — only one row should ever exist.
"""

from datetime import datetime, timezone
from app.extensions import db


class Setting(db.Model):
    """Global restaurant settings / configuration."""

    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(120), default='DineFlow Restaurant')
    business_address = db.Column(db.String(255), nullable=True)
    business_phone = db.Column(db.String(20), nullable=True)
    business_email = db.Column(db.String(120), nullable=True)
    business_tagline = db.Column(db.String(200), nullable=True)

    receipt_prefix = db.Column(db.String(10), default='RCP-')
    order_prefix = db.Column(db.String(10), default='ORD-')
    currency = db.Column(db.String(10), default='GHS')
    tax_rate = db.Column(db.Numeric(5, 2), default=0.00)

    # Features
    allow_takeaway = db.Column(db.Boolean, default=True)
    allow_delivery = db.Column(db.Boolean, default=False)
    auto_print_receipt = db.Column(db.Boolean, default=False)

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # ------------------------------------------------------------------ #
    #  Class helpers
    # ------------------------------------------------------------------ #

    @classmethod
    def get_settings(cls):
        """Return singleton settings row, creating defaults if none exist."""
        settings = cls.query.first()
        if not settings:
            settings = cls()
            db.session.add(settings)
            db.session.commit()
        return settings

    def __repr__(self) -> str:
        return f'<Setting {self.business_name}>'
