"""
Orders Blueprint — Order management for DineFlow Restaurant System.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Order, OrderItem, MenuItem, RestaurantTable, Customer, Setting
from datetime import datetime, timezone

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')


def _generate_order_number():
    """Generate the next sequential order number."""
    settings = Setting.get_settings()
    prefix = settings.order_prefix or 'ORD-'
    last = Order.query.order_by(Order.id.desc()).first()
    next_id = (last.id + 1) if last else 1
    return f"{prefix}{next_id:05d}"


@orders_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    type_filter = request.args.get('order_type', '')
    search = request.args.get('search', '').strip()

    query = Order.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if type_filter:
        query = query.filter_by(order_type=type_filter)
    if search:
        query = query.filter(Order.order_number.ilike(f'%{search}%'))

    orders = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template('orders/index.html', orders=orders, status_filter=status_filter,
                           type_filter=type_filter, search=search)


@orders_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    tables = RestaurantTable.query.filter_by(status='Available').order_by(RestaurantTable.table_number).all()
    customers = Customer.query.order_by(Customer.full_name).all()
    menu_items = MenuItem.query.filter_by(status='Available').order_by(MenuItem.category, MenuItem.name).all()

    if request.method == 'POST':
        order_type = request.form.get('order_type', 'Dine-In')
        table_id = request.form.get('table_id') or None
        customer_id = request.form.get('customer_id') or None
        notes = request.form.get('notes', '').strip()

        # Collect items from form: item_ids[] and qtys[]
        item_ids = request.form.getlist('item_ids[]')
        quantities = request.form.getlist('quantities[]')

        if not item_ids:
            flash('Please add at least one menu item to the order.', 'danger')
            return render_template('orders/create.html', tables=tables, customers=customers, menu_items=menu_items)

        settings = Setting.get_settings()
        order = Order(
            order_number=_generate_order_number(),
            order_type=order_type,
            table_id=int(table_id) if table_id else None,
            customer_id=int(customer_id) if customer_id else None,
            user_id=current_user.id,
            notes=notes,
            status='Open'
        )
        db.session.add(order)
        db.session.flush()  # get order.id

        for item_id, qty in zip(item_ids, quantities):
            try:
                qty = int(qty)
                if qty <= 0:
                    continue
            except (ValueError, TypeError):
                continue

            menu_item = MenuItem.query.get(int(item_id))
            if not menu_item:
                continue

            oi = OrderItem(
                order_id=order.id,
                menu_item_id=menu_item.id,
                quantity=qty,
                unit_price=menu_item.price
            )
            db.session.add(oi)

        db.session.flush()
        order.recalculate_totals(tax_rate=float(settings.tax_rate))

        # Mark table occupied
        if order.table_id:
            table = RestaurantTable.query.get(order.table_id)
            if table:
                table.status = 'Occupied'

        db.session.commit()
        flash(f'Order {order.order_number} created successfully.', 'success')
        return redirect(url_for('orders.view', order_id=order.id))

    return render_template('orders/create.html', tables=tables, customers=customers, menu_items=menu_items)


@orders_bp.route('/<int:order_id>/view')
@login_required
def view(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('orders/view.html', order=order)


@orders_bp.route('/<int:order_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(order_id):
    order = Order.query.get_or_404(order_id)

    if order.status in ('Completed', 'Cancelled'):
        flash('Cannot edit a completed or cancelled order.', 'warning')
        return redirect(url_for('orders.view', order_id=order.id))

    menu_items = MenuItem.query.filter_by(status='Available').order_by(MenuItem.category, MenuItem.name).all()
    customers = Customer.query.order_by(Customer.full_name).all()
    tables = RestaurantTable.query.order_by(RestaurantTable.table_number).all()

    if request.method == 'POST':
        order.notes = request.form.get('notes', '').strip()
        order.customer_id = request.form.get('customer_id') or None
        order.status = request.form.get('status', order.status)

        # Re-build items
        item_ids = request.form.getlist('item_ids[]')
        quantities = request.form.getlist('quantities[]')

        if item_ids:
            # Delete existing items
            OrderItem.query.filter_by(order_id=order.id).delete()
            for item_id, qty in zip(item_ids, quantities):
                try:
                    qty = int(qty)
                    if qty <= 0:
                        continue
                except (ValueError, TypeError):
                    continue
                menu_item = MenuItem.query.get(int(item_id))
                if not menu_item:
                    continue
                oi = OrderItem(order_id=order.id, menu_item_id=menu_item.id,
                               quantity=qty, unit_price=menu_item.price)
                db.session.add(oi)

        settings = Setting.get_settings()
        db.session.flush()
        order.recalculate_totals(tax_rate=float(settings.tax_rate))
        db.session.commit()
        flash(f'Order {order.order_number} updated.', 'success')
        return redirect(url_for('orders.view', order_id=order.id))

    return render_template('orders/edit.html', order=order, menu_items=menu_items,
                           customers=customers, tables=tables)


@orders_bp.route('/<int:order_id>/update-status', methods=['POST'])
@login_required
def update_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')

    valid = ['Open', 'In Progress', 'Ready', 'Completed', 'Cancelled']
    if new_status not in valid:
        flash('Invalid status.', 'danger')
        return redirect(url_for('orders.view', order_id=order_id))

    order.status = new_status

    # Free table when order completed or cancelled
    if new_status in ('Completed', 'Cancelled') and order.table_id:
        table = RestaurantTable.query.get(order.table_id)
        if table:
            table.status = 'Available'

    db.session.commit()
    flash(f'Order {order.order_number} status updated to {new_status}.', 'success')
    return redirect(url_for('orders.view', order_id=order_id))


@orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status in ('Completed',):
        flash('Cannot cancel a completed order.', 'danger')
    else:
        order.status = 'Cancelled'
        if order.table_id:
            table = RestaurantTable.query.get(order.table_id)
            if table:
                table.status = 'Available'
        db.session.commit()
        flash(f'Order {order.order_number} cancelled.', 'info')
    return redirect(url_for('orders.index'))
