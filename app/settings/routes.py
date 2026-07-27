"""
Settings Blueprint — Restaurant configuration for DineFlow.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Setting

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if not current_user.is_administrator():
        flash('Access denied. Administrator privileges required.', 'danger')
        return redirect(url_for('dashboard.index'))

    settings = Setting.get_settings()

    if request.method == 'POST':
        settings.business_name = request.form.get('business_name', '').strip()
        settings.business_address = request.form.get('business_address', '').strip()
        settings.business_phone = request.form.get('business_phone', '').strip()
        settings.business_email = request.form.get('business_email', '').strip()
        settings.business_tagline = request.form.get('business_tagline', '').strip()
        settings.receipt_prefix = request.form.get('receipt_prefix', 'RCP-').strip()
        settings.order_prefix = request.form.get('order_prefix', 'ORD-').strip()
        settings.currency = request.form.get('currency', 'GHS').strip()

        try:
            tax_rate = float(request.form.get('tax_rate', 0))
            if tax_rate < 0 or tax_rate > 100:
                raise ValueError
            settings.tax_rate = tax_rate
        except (ValueError, TypeError):
            flash('Invalid tax rate. Enter a value between 0 and 100.', 'danger')
            return render_template('settings/index.html', settings=settings)

        settings.allow_takeaway = bool(request.form.get('allow_takeaway'))
        settings.allow_delivery = bool(request.form.get('allow_delivery'))
        settings.auto_print_receipt = bool(request.form.get('auto_print_receipt'))

        db.session.commit()
        flash('Settings saved successfully.', 'success')
        return redirect(url_for('settings.index'))

    return render_template('settings/index.html', settings=settings)
