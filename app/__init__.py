"""
Application Factory for DineFlow Restaurant Management System.
"""

import os
import click
from flask import Flask, render_template
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from app.config import Config, config_by_name
from app.extensions import db, migrate, login_manager, csrf


def create_app(config_name=None):
    """
    Flask Application Factory.
    Initializes configuration, extensions, blueprints, error handlers, and CLI commands.
    """
    app = Flask(__name__)

    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app_config = config_by_name.get(config_name, Config)
    app.config.from_object(app_config)

    # Automatic Database Connection Health Check & Fallback to SQLite
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri.startswith('mysql'):
        try:
            test_engine = create_engine(db_uri, connect_args={'connect_timeout': 3})
            with test_engine.connect() as conn:
                pass
            test_engine.dispose()
        except OperationalError as e:
            sqlite_db_path = os.path.abspath(os.path.join(app.root_path, '..', 'instance', 'dineflow.db'))
            app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{sqlite_db_path}'
            app.logger.warning(
                f"MySQL connection failed ({e}). Falling back to SQLite: {app.config['SQLALCHEMY_DATABASE_URI']}"
            )

    # Ensure required directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.root_path, '..', 'instance'), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, '..', 'logs'), exist_ok=True)

    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register Flask-Login user loader
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register Blueprints
    from app.dashboard import dashboard_bp
    from app.auth import auth_bp
    from app.users import users_bp
    from app.customers import customers_bp
    from app.menu.routes import menu_bp
    from app.tables.routes import tables_bp
    from app.orders.routes import orders_bp
    from app.payments.routes import payments_bp
    from app.receipts.routes import receipts_bp
    from app.reports.routes import reports_bp
    from app.settings.routes import settings_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(tables_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(receipts_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500

    # CLI: seed admin command
    @app.cli.command("seed-admin")
    def seed_admin():
        """Seeds default administrator account."""
        db.create_all()
        admin_email = "admin@dineflow.com"
        existing = User.query.filter_by(email=admin_email).first()
        if not existing:
            admin = User(
                full_name="System Administrator",
                email=admin_email,
                phone_number="0200000000",
                role="Administrator",
                status="Active"
            )
            admin.set_password("Admin123!")
            db.session.add(admin)
            db.session.commit()
            click.echo(f"Created administrator: {admin_email} / Admin123!")
        else:
            click.echo(f"Administrator '{admin_email}' already exists.")

    # CLI: seed sample data
    @app.cli.command("seed-data")
    def seed_data():
        """Seeds sample menu items and a restaurant table for demo."""
        db.create_all()
        from app.models import MenuItem, RestaurantTable, Setting

        # Settings
        if not Setting.query.first():
            s = Setting(
                business_name='DineFlow Restaurant',
                business_phone='0200000000',
                business_email='info@dineflow.com',
                receipt_prefix='RCP-',
                currency='GHS',
                tax_rate=0.00
            )
            db.session.add(s)

        # Menu Items
        if not MenuItem.query.first():
            items = [
                MenuItem(name='Jollof Rice & Chicken', category='Main Course', price=35.00, status='Available'),
                MenuItem(name='Fried Rice & Beef', category='Main Course', price=30.00, status='Available'),
                MenuItem(name='Banku & Tilapia', category='Main Course', price=45.00, status='Available'),
                MenuItem(name='Waakye Special', category='Main Course', price=25.00, status='Available'),
                MenuItem(name='Kelewele', category='Appetizer', price=10.00, status='Available'),
                MenuItem(name='Spring Rolls (4 pcs)', category='Appetizer', price=15.00, status='Available'),
                MenuItem(name='Malt Drink', category='Beverage', price=8.00, status='Available'),
                MenuItem(name='Mineral Water', category='Beverage', price=5.00, status='Available'),
                MenuItem(name='Sobolo (Cup)', category='Beverage', price=6.00, status='Available'),
                MenuItem(name='Chocolate Cake Slice', category='Dessert', price=12.00, status='Available'),
            ]
            for item in items:
                db.session.add(item)

        # Tables
        if not RestaurantTable.query.first():
            tables = [
                RestaurantTable(table_number='T01', capacity=2, status='Available'),
                RestaurantTable(table_number='T02', capacity=4, status='Available'),
                RestaurantTable(table_number='T03', capacity=4, status='Available'),
                RestaurantTable(table_number='T04', capacity=6, status='Available'),
                RestaurantTable(table_number='T05', capacity=8, status='Available'),
                RestaurantTable(table_number='VIP-01', capacity=4, status='Available'),
            ]
            for t in tables:
                db.session.add(t)

        db.session.commit()
        click.echo("Sample data seeded successfully.")

    return app

