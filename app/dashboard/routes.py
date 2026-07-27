"""
Dashboard Routes for DineFlow Restaurant Management System.
"""

from flask import render_template
from flask_login import login_required, current_user
from app.dashboard import dashboard_bp
from app.models import Order, MenuItem, RestaurantTable, Customer, Payment
from app.extensions import db
from datetime import datetime, timezone, timedelta
from sqlalchemy import func


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Main dashboard with KPI cards and summary widgets."""
    today = datetime.now(timezone.utc).date()
    month_start = today.replace(day=1)

    # ── KPI Cards ──────────────────────────────────────────────────────── #
    today_orders = Order.query.filter(
        func.date(Order.created_at) == today
    ).count()

    today_revenue = db.session.query(
        func.coalesce(func.sum(Order.total_amount), 0)
    ).filter(
        func.date(Order.created_at) == today,
        Order.status.in_(['Completed'])
    ).scalar()

    pending_orders = Order.query.filter(
        Order.status.in_(['Open', 'In Progress', 'Ready'])
    ).count()

    available_tables = RestaurantTable.query.filter_by(status='Available').count()
    total_tables = RestaurantTable.query.count()

    # ── Monthly Stats ──────────────────────────────────────────────────── #
    month_revenue = db.session.query(
        func.coalesce(func.sum(Order.total_amount), 0)
    ).filter(
        func.date(Order.created_at) >= month_start,
        Order.status == 'Completed'
    ).scalar()

    month_orders = Order.query.filter(
        func.date(Order.created_at) >= month_start
    ).count()

    # ── Recent Orders ──────────────────────────────────────────────────── #
    recent_orders = (
        Order.query
        .order_by(Order.created_at.desc())
        .limit(8)
        .all()
    )

    # ── Active Table Overview ──────────────────────────────────────────── #
    occupied_tables = RestaurantTable.query.filter_by(status='Occupied').all()

    # ── Top Menu Items ─────────────────────────────────────────────────── #
    from app.models import OrderItem
    top_items = (
        db.session.query(
            MenuItem.name,
            func.sum(OrderItem.quantity).label('qty')
        )
        .join(OrderItem, OrderItem.menu_item_id == MenuItem.id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(func.date(Order.created_at) >= month_start)
        .group_by(MenuItem.id, MenuItem.name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5)
        .all()
    )

    return render_template(
        'dashboard/index.html',
        today_orders=today_orders,
        today_revenue=float(today_revenue),
        pending_orders=pending_orders,
        available_tables=available_tables,
        total_tables=total_tables,
        month_revenue=float(month_revenue),
        month_orders=month_orders,
        recent_orders=recent_orders,
        occupied_tables=occupied_tables,
        top_items=top_items,
    )
