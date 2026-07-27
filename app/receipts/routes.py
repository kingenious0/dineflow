"""
Receipts Blueprint — Receipt viewing and printing for DineFlow.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import Receipt, Setting

receipts_bp = Blueprint('receipts', __name__, url_prefix='/receipts')


@receipts_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()

    from app.extensions import db
    query = Receipt.query
    if search:
        query = query.filter(Receipt.receipt_number.ilike(f'%{search}%'))

    receipts = query.order_by(Receipt.issued_at.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template('receipts/index.html', receipts=receipts, search=search)


@receipts_bp.route('/<int:receipt_id>/view')
@login_required
def view(receipt_id):
    receipt = Receipt.query.get_or_404(receipt_id)
    settings = Setting.get_settings()
    return render_template('receipts/view.html', receipt=receipt, settings=settings)


@receipts_bp.route('/<int:receipt_id>/print')
@login_required
def print_receipt(receipt_id):
    receipt = Receipt.query.get_or_404(receipt_id)
    settings = Setting.get_settings()
    return render_template('receipts/print.html', receipt=receipt, settings=settings)
