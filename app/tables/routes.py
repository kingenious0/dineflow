"""
Tables Blueprint — Restaurant Tables CRUD for DineFlow.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import RestaurantTable, Order

tables_bp = Blueprint('tables', __name__, url_prefix='/tables')


@tables_bp.route('/')
@login_required
def index():
    tables = RestaurantTable.query.order_by(RestaurantTable.table_number).all()
    return render_template('tables/index.html', tables=tables)


@tables_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.is_manager():
        flash('Access denied. Manager privileges required.', 'danger')
        return redirect(url_for('tables.index'))

    if request.method == 'POST':
        table_number = request.form.get('table_number', '').strip()
        capacity = request.form.get('capacity', 4)

        if not table_number:
            flash('Table number is required.', 'danger')
        elif RestaurantTable.query.filter_by(table_number=table_number).first():
            flash(f'Table "{table_number}" already exists.', 'danger')
        else:
            table = RestaurantTable(table_number=table_number, capacity=int(capacity))
            db.session.add(table)
            db.session.commit()
            flash(f'Table {table_number} added successfully.', 'success')
            return redirect(url_for('tables.index'))

    return render_template('tables/create.html')


@tables_bp.route('/<int:table_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(table_id):
    if not current_user.is_manager():
        flash('Access denied.', 'danger')
        return redirect(url_for('tables.index'))

    table = RestaurantTable.query.get_or_404(table_id)

    if request.method == 'POST':
        table.table_number = request.form.get('table_number', '').strip()
        table.capacity = int(request.form.get('capacity', table.capacity))
        table.status = request.form.get('status', table.status)
        db.session.commit()
        flash(f'Table {table.table_number} updated.', 'success')
        return redirect(url_for('tables.index'))

    return render_template('tables/edit.html', table=table)


@tables_bp.route('/<int:table_id>/delete', methods=['POST'])
@login_required
def delete(table_id):
    if not current_user.is_manager():
        flash('Access denied.', 'danger')
        return redirect(url_for('tables.index'))

    table = RestaurantTable.query.get_or_404(table_id)
    if table.status == 'Occupied':
        flash('Cannot delete an occupied table.', 'danger')
        return redirect(url_for('tables.index'))

    num = table.table_number
    db.session.delete(table)
    db.session.commit()
    flash(f'Table {num} deleted.', 'success')
    return redirect(url_for('tables.index'))
