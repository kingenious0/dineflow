"""
Payments Blueprint — Payment processing for DineFlow Restaurant System.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Order, Payment, Receipt, Setting
from datetime import datetime, timezone

payments_bp = Blueprint('payments', __name__, url_prefix='/payments')


def _generate_receipt_number():
    """Generate next sequential receipt number."""
    settings = Setting.get_settings()
    prefix = settings.receipt_prefix or 'RCP-'
    last = Receipt.query.order_by(Receipt.id.desc()).first()
    next_id = (last.id + 1) if last else 1
    return f"{prefix}{next_id:05d}"


@payments_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    method_filter = request.args.get('method', '')

    query = Payment.query
    if method_filter:
        query = query.filter_by(payment_method=method_filter)

    payments = query.order_by(Payment.paid_at.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template('payments/index.html', payments=payments, method_filter=method_filter)


@payments_bp.route('/process/<int:order_id>', methods=['GET', 'POST'])
@login_required
def process(order_id):
    """Process payment for a specific order."""
    order = Order.query.get_or_404(order_id)

    if order.is_paid:
        flash('This order has already been paid.', 'warning')
        return redirect(url_for('orders.view', order_id=order_id))

    if order.status == 'Cancelled':
        flash('Cannot process payment for a cancelled order.', 'danger')
        return redirect(url_for('orders.view', order_id=order_id))

    if request.method == 'POST':
        payment_method = request.form.get('payment_method', 'Cash')
        amount_paid = request.form.get('amount_paid', 0)
        reference = request.form.get('reference', '').strip()
        notes = request.form.get('notes', '').strip()

        try:
            amount_paid = float(amount_paid)
        except (ValueError, TypeError):
            flash('Invalid payment amount.', 'danger')
            return render_template('payments/process.html', order=order)

        if amount_paid < float(order.total_amount):
            flash(f'Amount paid ({amount_paid:.2f}) is less than order total ({float(order.total_amount):.2f}).', 'danger')
            return render_template('payments/process.html', order=order)

        change_given = round(amount_paid - float(order.total_amount), 2)

        # Create Payment record
        payment = Payment(
            order_id=order.id,
            amount_paid=amount_paid,
            change_given=change_given,
            payment_method=payment_method,
            reference=reference,
            notes=notes,
            processed_by=current_user.id,
            status='Completed'
        )
        db.session.add(payment)

        # Generate Receipt
        receipt = Receipt(
            order_id=order.id,
            receipt_number=_generate_receipt_number(),
            subtotal=order.subtotal,
            tax_amount=order.tax_amount,
            discount_amount=order.discount_amount,
            total_amount=order.total_amount,
            payment_method=payment_method,
            amount_paid=amount_paid,
            change_given=change_given,
            issued_by=current_user.id
        )
        db.session.add(receipt)

        # Update order status
        order.status = 'Completed'

        # Free up the table
        if order.table_id:
            from app.models import RestaurantTable
            table = RestaurantTable.query.get(order.table_id)
            if table:
                table.status = 'Available'

        db.session.commit()
        flash(f'Payment processed. Receipt #{receipt.receipt_number} generated.', 'success')
        return redirect(url_for('receipts.view', receipt_id=receipt.id))

    return render_template('payments/process.html', order=order)


@payments_bp.route('/<int:payment_id>/view')
@login_required
def view(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    return render_template('payments/view.html', payment=payment)
