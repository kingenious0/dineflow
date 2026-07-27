"""
Menu Blueprint — Menu Items CRUD for DineFlow.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import MenuItem

menu_bp = Blueprint('menu', __name__, url_prefix='/menu')


@menu_bp.route('/')
@login_required
def index():
    search = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '')
    status_filter = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)

    query = MenuItem.query
    if search:
        query = query.filter(MenuItem.name.ilike(f'%{search}%'))
    if category_filter:
        query = query.filter_by(category=category_filter)
    if status_filter:
        query = query.filter_by(status=status_filter)

    items = query.order_by(MenuItem.category, MenuItem.name).paginate(page=page, per_page=15, error_out=False)

    categories = db.session.query(MenuItem.category).distinct().order_by(MenuItem.category).all()
    categories = [c[0] for c in categories]

    return render_template('menu/index.html', items=items, categories=categories,
                           search=search, category_filter=category_filter, status_filter=status_filter)


@menu_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.is_manager():
        flash('Access denied. Manager privileges required.', 'danger')
        return redirect(url_for('menu.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        price = request.form.get('price', 0)
        status = request.form.get('status', 'Available')

        errors = []
        if not name:
            errors.append('Item name is required.')
        if not category:
            errors.append('Category is required.')
        try:
            price = float(price)
            if price <= 0:
                errors.append('Price must be greater than zero.')
        except (ValueError, TypeError):
            errors.append('Invalid price format.')

        if errors:
            for e in errors:
                flash(e, 'danger')
        else:
            item = MenuItem(name=name, description=description, category=category,
                            price=price, status=status)
            db.session.add(item)
            db.session.commit()
            flash(f'Menu item "{name}" added successfully.', 'success')
            return redirect(url_for('menu.index'))

    return render_template('menu/create.html')


@menu_bp.route('/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(item_id):
    if not current_user.is_manager():
        flash('Access denied.', 'danger')
        return redirect(url_for('menu.index'))

    item = MenuItem.query.get_or_404(item_id)

    if request.method == 'POST':
        item.name = request.form.get('name', '').strip()
        item.description = request.form.get('description', '').strip()
        item.category = request.form.get('category', '').strip()
        item.status = request.form.get('status', item.status)
        try:
            item.price = float(request.form.get('price', item.price))
        except (ValueError, TypeError):
            flash('Invalid price.', 'danger')
            return render_template('menu/edit.html', item=item)

        db.session.commit()
        flash(f'Menu item "{item.name}" updated.', 'success')
        return redirect(url_for('menu.index'))

    return render_template('menu/edit.html', item=item)


@menu_bp.route('/<int:item_id>/toggle-status', methods=['POST'])
@login_required
def toggle_status(item_id):
    if not current_user.is_manager():
        flash('Access denied.', 'danger')
        return redirect(url_for('menu.index'))

    item = MenuItem.query.get_or_404(item_id)
    item.status = 'Unavailable' if item.status == 'Available' else 'Available'
    db.session.commit()
    flash(f'"{item.name}" is now {item.status}.', 'info')
    return redirect(url_for('menu.index'))


@menu_bp.route('/<int:item_id>/delete', methods=['POST'])
@login_required
def delete(item_id):
    if not current_user.is_manager():
        flash('Access denied.', 'danger')
        return redirect(url_for('menu.index'))

    item = MenuItem.query.get_or_404(item_id)
    name = item.name
    db.session.delete(item)
    db.session.commit()
    flash(f'Menu item "{name}" deleted.', 'success')
    return redirect(url_for('menu.index'))
