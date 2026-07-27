"""
Reports Blueprint — Sales, analytics, print styling, and CSV exports for DineFlow.
"""

import csv
import io
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, make_response
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Order, OrderItem, MenuItem, Payment, Customer, Setting
from datetime import datetime, timezone, timedelta
from sqlalchemy import func

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


def _manager_required():
    if not current_user.is_manager():
        flash('Access denied. Manager privileges required.', 'danger')
        return redirect(url_for('dashboard.index'))
    return None


@reports_bp.route('/')
@login_required
def index():
    deny = _manager_required()
    if deny:
        return deny
    return render_template('reports/index.html')


@reports_bp.route('/sales')
@login_required
def sales():
    deny = _manager_required()
    if deny:
        return deny

    start_str = request.args.get('start', '')
    end_str = request.args.get('end', '')

    today = datetime.now(timezone.utc).date()
    try:
        start_date = datetime.strptime(start_str, '%Y-%m-%d').date() if start_str else today.replace(day=1)
        end_date = datetime.strptime(end_str, '%Y-%m-%d').date() if end_str else today
    except ValueError:
        start_date = today.replace(day=1)
        end_date = today

    # Summary KPIs
    total_revenue = db.session.query(
        func.coalesce(func.sum(Order.total_amount), 0)
    ).filter(
        func.date(Order.created_at).between(start_date, end_date),
        Order.status == 'Completed'
    ).scalar()

    total_orders = Order.query.filter(
        func.date(Order.created_at).between(start_date, end_date)
    ).count()

    completed_orders = Order.query.filter(
        func.date(Order.created_at).between(start_date, end_date),
        Order.status == 'Completed'
    ).count()

    cancelled_orders = Order.query.filter(
        func.date(Order.created_at).between(start_date, end_date),
        Order.status == 'Cancelled'
    ).count()

    avg_order = float(total_revenue) / completed_orders if completed_orders else 0

    # Daily sales breakdown
    daily_sales = db.session.query(
        func.date(Order.created_at).label('day'),
        func.count(Order.id).label('orders'),
        func.coalesce(func.sum(Order.total_amount), 0).label('revenue')
    ).filter(
        func.date(Order.created_at).between(start_date, end_date),
        Order.status == 'Completed'
    ).group_by(func.date(Order.created_at)).order_by(func.date(Order.created_at)).all()

    # Payment method breakdown
    payment_methods = db.session.query(
        Payment.payment_method,
        func.count(Payment.id).label('count'),
        func.sum(Payment.amount_paid).label('total')
    ).join(Order).filter(
        func.date(Order.created_at).between(start_date, end_date)
    ).group_by(Payment.payment_method).all()

    # Order type breakdown
    order_types = db.session.query(
        Order.order_type,
        func.count(Order.id).label('count'),
        func.coalesce(func.sum(Order.total_amount), 0).label('revenue')
    ).filter(
        func.date(Order.created_at).between(start_date, end_date),
        Order.status == 'Completed'
    ).group_by(Order.order_type).all()

    settings = Setting.get_settings()

    return render_template(
        'reports/sales.html',
        start_date=start_date,
        end_date=end_date,
        total_revenue=float(total_revenue),
        total_orders=total_orders,
        completed_orders=completed_orders,
        cancelled_orders=cancelled_orders,
        avg_order=avg_order,
        daily_sales=daily_sales,
        payment_methods=payment_methods,
        order_types=order_types,
        settings=settings,
    )


@reports_bp.route('/sales/export-csv')
@login_required
def export_sales_csv():
    deny = _manager_required()
    if deny:
        return deny

    start_str = request.args.get('start', '')
    end_str = request.args.get('end', '')

    today = datetime.now(timezone.utc).date()
    try:
        start_date = datetime.strptime(start_str, '%Y-%m-%d').date() if start_str else today.replace(day=1)
        end_date = datetime.strptime(end_str, '%Y-%m-%d').date() if end_str else today
    except ValueError:
        start_date = today.replace(day=1)
        end_date = today

    daily_sales = db.session.query(
        func.date(Order.created_at).label('day'),
        func.count(Order.id).label('orders'),
        func.coalesce(func.sum(Order.total_amount), 0).label('revenue')
    ).filter(
        func.date(Order.created_at).between(start_date, end_date),
        Order.status == 'Completed'
    ).group_by(func.date(Order.created_at)).order_by(func.date(Order.created_at)).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Headers & Summary
    writer.writerow(['DineFlow Restaurant - Sales Report'])
    writer.writerow([f'Period: {start_date} to {end_date}'])
    writer.writerow([])
    writer.writerow(['Date', 'Completed Orders', 'Daily Revenue (GHS)'])

    total_rev = 0
    total_ord = 0
    for day, orders_count, rev in daily_sales:
        rev_val = float(rev)
        total_rev += rev_val
        total_ord += orders_count
        writer.writerow([day, orders_count, f"{rev_val:.2f}"])

    writer.writerow([])
    writer.writerow(['TOTALS', total_ord, f"{total_rev:.2f}"])

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename=dineflow_sales_{start_date}_to_{end_date}.csv"
    response.headers["Content-type"] = "text/csv; charset=utf-8"
    return response


@reports_bp.route('/menu')
@login_required
def menu_performance():
    deny = _manager_required()
    if deny:
        return deny

    start_str = request.args.get('start', '')
    end_str = request.args.get('end', '')
    today = datetime.now(timezone.utc).date()
    try:
        start_date = datetime.strptime(start_str, '%Y-%m-%d').date() if start_str else today.replace(day=1)
        end_date = datetime.strptime(end_str, '%Y-%m-%d').date() if end_str else today
    except ValueError:
        start_date = today.replace(day=1)
        end_date = today

    top_items = db.session.query(
        MenuItem.name,
        MenuItem.category,
        MenuItem.price,
        func.sum(OrderItem.quantity).label('qty_sold'),
        func.sum(OrderItem.quantity * OrderItem.unit_price).label('revenue')
    ).join(OrderItem, OrderItem.menu_item_id == MenuItem.id
    ).join(Order, Order.id == OrderItem.order_id
    ).filter(
        func.date(Order.created_at).between(start_date, end_date),
        Order.status == 'Completed'
    ).group_by(MenuItem.id, MenuItem.name, MenuItem.category, MenuItem.price
    ).order_by(func.sum(OrderItem.quantity).desc()).all()

    category_summary = db.session.query(
        MenuItem.category,
        func.sum(OrderItem.quantity).label('qty'),
        func.sum(OrderItem.quantity * OrderItem.unit_price).label('revenue')
    ).join(OrderItem, OrderItem.menu_item_id == MenuItem.id
    ).join(Order, Order.id == OrderItem.order_id
    ).filter(
        func.date(Order.created_at).between(start_date, end_date),
        Order.status == 'Completed'
    ).group_by(MenuItem.category).order_by(func.sum(OrderItem.quantity * OrderItem.unit_price).desc()).all()

    settings = Setting.get_settings()

    return render_template(
        'reports/menu.html',
        start_date=start_date,
        end_date=end_date,
        top_items=top_items,
        category_summary=category_summary,
        settings=settings,
    )


@reports_bp.route('/menu/export-csv')
@login_required
def export_menu_csv():
    deny = _manager_required()
    if deny:
        return deny

    start_str = request.args.get('start', '')
    end_str = request.args.get('end', '')
    today = datetime.now(timezone.utc).date()
    try:
        start_date = datetime.strptime(start_str, '%Y-%m-%d').date() if start_str else today.replace(day=1)
        end_date = datetime.strptime(end_str, '%Y-%m-%d').date() if end_str else today
    except ValueError:
        start_date = today.replace(day=1)
        end_date = today

    top_items = db.session.query(
        MenuItem.name,
        MenuItem.category,
        MenuItem.price,
        func.sum(OrderItem.quantity).label('qty_sold'),
        func.sum(OrderItem.quantity * OrderItem.unit_price).label('revenue')
    ).join(OrderItem, OrderItem.menu_item_id == MenuItem.id
    ).join(Order, Order.id == OrderItem.order_id
    ).filter(
        func.date(Order.created_at).between(start_date, end_date),
        Order.status == 'Completed'
    ).group_by(MenuItem.id, MenuItem.name, MenuItem.category, MenuItem.price
    ).order_by(func.sum(OrderItem.quantity).desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['DineFlow Restaurant - Menu Item Performance Report'])
    writer.writerow([f'Period: {start_date} to {end_date}'])
    writer.writerow([])
    writer.writerow(['Rank', 'Dish Name', 'Category', 'Unit Price (GHS)', 'Quantity Sold', 'Total Revenue (GHS)'])

    for idx, (name, cat, price, qty, rev) in enumerate(top_items, 1):
        writer.writerow([idx, name, cat, f"{float(price):.2f}", qty, f"{float(rev):.2f}"])

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename=dineflow_menu_performance_{start_date}_to_{end_date}.csv"
    response.headers["Content-type"] = "text/csv; charset=utf-8"
    return response
