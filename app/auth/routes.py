"""
Authentication Routes for DineFlow Restaurant Management System.
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth_bp
from app.models import User
from app.extensions import db
from datetime import datetime, timezone


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if user.status != 'Active':
                flash('Your account has been deactivated. Please contact the administrator.', 'danger')
                return render_template('auth/login.html')

            login_user(user, remember=remember)
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()

            next_page = request.args.get('next')
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    flash('You have been signed out successfully.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Allow the current user to change their own password."""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
        elif new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
        elif len(new_password) < 6:
            flash('New password must be at least 6 characters.', 'danger')
        else:
            current_user.set_password(new_password)
            db.session.commit()
            flash('Password updated successfully.', 'success')
            return redirect(url_for('dashboard.index'))

    return render_template('auth/change_password.html')
