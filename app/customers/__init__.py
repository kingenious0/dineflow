"""
Customers Blueprint for DineFlow Restaurant Management System.
"""

from flask import Blueprint

customers_bp = Blueprint('customers', __name__, url_prefix='/customers')

from app.customers import routes  # noqa: E402, F401
