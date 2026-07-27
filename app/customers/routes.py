"""
Customers Routes for DineFlow Restaurant Management System.
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.customers import customers_bp
from app.models import Customer, Order
from app.extensions import db


@customers_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()

    query = Customer.query
    if search:
        query = query.filter(
            db.or_(
                Customer.full_name.ilike(f'%{search}%'),
                Customer.phone_number.ilike(f'%{search}%'),
                Customer.email.ilike(f'%{search}%')
            )
        )

    customers = query.order_by(Customer.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template('customers/index.html', customers=customers, search=search)


@customers_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone_number', '').strip()
        email = request.form.get('email', '').strip()
        notes = request.form.get('notes', '').strip()

        if not full_name:
            flash('Full name is required.', 'danger')
        else:
            customer = Customer(full_name=full_name, phone_number=phone, email=email, notes=notes)
            db.session.add(customer)
            db.session.commit()
            flash(f'Customer "{full_name}" added successfully.', 'success')
            return redirect(url_for('customers.index'))

    return render_template('customers/create.html')


@customers_bp.route('/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(customer_id):
    customer = Customer.query.get_or_404(customer_id)

    if request.method == 'POST':
        customer.full_name = request.form.get('full_name', '').strip()
        customer.phone_number = request.form.get('phone_number', '').strip()
        customer.email = request.form.get('email', '').strip()
        customer.notes = request.form.get('notes', '').strip()
        db.session.commit()
        flash(f'Customer "{customer.full_name}" updated.', 'success')
        return redirect(url_for('customers.index'))

    return render_template('customers/edit.html', customer=customer)


@customers_bp.route('/<int:customer_id>/delete', methods=['POST'])
@login_required
def delete(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    name = customer.full_name
    db.session.delete(customer)
    db.session.commit()
    flash(f'Customer "{name}" deleted.', 'success')
    return redirect(url_for('customers.index'))


@customers_bp.route('/<int:customer_id>/view')
@login_required
def view(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    orders = Order.query.filter_by(customer_id=customer_id).order_by(Order.created_at.desc()).all()
    return render_template('customers/view.html', customer=customer, orders=orders)
