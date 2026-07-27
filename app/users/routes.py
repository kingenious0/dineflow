"""
Users Routes for DineFlow Restaurant Management System.
Full CRUD with RBAC — Administrators only.
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.users import users_bp
from app.models import User
from app.extensions import db


def admin_required(f):
    """Decorator: restrict to Administrator role."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_administrator():
            flash('Access denied. Administrator privileges required.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated


def manager_required(f):
    """Decorator: restrict to Manager or Administrator role."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_manager():
            flash('Access denied. Manager privileges required.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated


@users_bp.route('/')
@login_required
@admin_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    role_filter = request.args.get('role', '')
    status_filter = request.args.get('status', '')

    query = User.query

    if search:
        query = query.filter(
            db.or_(
                User.full_name.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )
    if role_filter:
        query = query.filter_by(role=role_filter)
    if status_filter:
        query = query.filter_by(status=status_filter)

    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template('users/index.html', users=users, search=search,
                           role_filter=role_filter, status_filter=status_filter)


@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone_number', '').strip()
        role = request.form.get('role', 'Cashier')
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        errors = []
        if not full_name:
            errors.append('Full name is required.')
        if not email:
            errors.append('Email is required.')
        elif User.query.filter_by(email=email).first():
            errors.append('A user with this email already exists.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm:
            errors.append('Passwords do not match.')

        if errors:
            for e in errors:
                flash(e, 'danger')
        else:
            user = User(full_name=full_name, email=email, phone_number=phone, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash(f'User "{full_name}" created successfully.', 'success')
            return redirect(url_for('users.index'))

    return render_template('users/create.html')


@users_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.full_name = request.form.get('full_name', '').strip()
        user.email = request.form.get('email', '').strip().lower()
        user.phone_number = request.form.get('phone_number', '').strip()
        user.role = request.form.get('role', user.role)
        user.status = request.form.get('status', user.status)

        new_password = request.form.get('new_password', '').strip()
        if new_password:
            if len(new_password) < 6:
                flash('Password must be at least 6 characters.', 'danger')
                return render_template('users/edit.html', user=user)
            user.set_password(new_password)

        db.session.commit()
        flash(f'User "{user.full_name}" updated successfully.', 'success')
        return redirect(url_for('users.index'))

    return render_template('users/edit.html', user=user)


@users_bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('users.index'))
    name = user.full_name
    db.session.delete(user)
    db.session.commit()
    flash(f'User "{name}" deleted.', 'success')
    return redirect(url_for('users.index'))


@users_bp.route('/<int:user_id>/view')
@login_required
@admin_required
def view(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('users/view.html', user=user)
