"""
User Model for DineFlow Restaurant Management System.
Supports RBAC with roles: Administrator, Manager, Cashier, Waiter.
"""

from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db


class User(UserMixin, db.Model):
    """System user account with role-based access control."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone_number = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default='Staff')
    status = db.Column(db.String(20), nullable=False, default='Active')
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    orders = db.relationship('Order', backref='served_by', lazy='dynamic', foreign_keys='Order.user_id')

    # ------------------------------------------------------------------ #
    #  Password Management
    # ------------------------------------------------------------------ #

    def set_password(self, password: str) -> None:
        """Hash and store the given plaintext password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify plaintext password against stored hash."""
        return check_password_hash(self.password_hash, password)

    # ------------------------------------------------------------------ #
    #  RBAC helpers
    # ------------------------------------------------------------------ #

    def is_administrator(self) -> bool:
        return self.role == 'Manager'

    def is_manager(self) -> bool:
        return self.role == 'Manager'

    def is_cashier(self) -> bool:
        return True

    def is_staff(self) -> bool:
        return self.role in ('Manager', 'Staff')

    def has_role(self, *roles) -> bool:
        return self.role in roles

    # ------------------------------------------------------------------ #
    #  Utility
    # ------------------------------------------------------------------ #

    @property
    def is_active_account(self) -> bool:
        return self.status == 'Active'

    def update_last_login(self) -> None:
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()

    def __repr__(self) -> str:
        return f'<User {self.email} [{self.role}]>'
