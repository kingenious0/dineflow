"""
Seed script for DineFlow Restaurant Management System - Populates Manager and Staff accounts, menu items, tables, and settings.
"""

import os
import pymysql
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

def auto_create_database():
    db_uri = os.getenv('DATABASE_URL') or os.getenv('SQLALCHEMY_DATABASE_URI', '')
    if not db_uri or 'mysql' not in db_uri:
        return
    try:
        clean_url = db_uri.replace('mysql+pymysql://', 'http://').replace('mysql://', 'http://')
        parsed = urlparse(clean_url)
        db_name = parsed.path.lstrip('/')
        host = parsed.hostname or 'localhost'
        port = parsed.port or 3306
        user = parsed.username or 'root'
        password = parsed.password or ''
        
        if db_name:
            conn = pymysql.connect(host=host, port=port, user=user, password=password)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            conn.commit()
            conn.close()
            print(f"[+] Ensured MySQL database `{db_name}` exists on {host}:{port}.")
    except Exception as e:
        print(f"[!] Database auto-creation notice: {e}")

auto_create_database()

from app import create_app
from app.extensions import db
from app.models import User, MenuItem, RestaurantTable, Setting, Customer

app = create_app()


def seed_database():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("[+] Database tables re-created successfully.")

        # Seed Settings if not exists
        Setting.get_settings()
        print("[+] App settings initialized.")

        # Seed Manager
        manager = User.query.filter_by(email='manager@dineflow.com').first()
        if not manager:
            manager = User(
                full_name='Restaurant Manager',
                email='manager@dineflow.com',
                phone_number='0201111111',
                role='Manager',
                status='Active'
            )
            manager.set_password('manager123')
            db.session.add(manager)
            print("[+] Created Manager: manager@dineflow.com / manager123")
        else:
            manager.role = 'Manager'
            manager.set_password('manager123')

        # Seed Staff
        staff = User.query.filter_by(email='staff@dineflow.com').first()
        if not staff:
            staff = User(
                full_name='Kofi Waiter',
                email='staff@dineflow.com',
                phone_number='0202222222',
                role='Staff',
                status='Active'
            )
            staff.set_password('staff123')
            db.session.add(staff)
            print("[+] Created Staff: staff@dineflow.com / staff123")
        else:
            staff.role = 'Staff'
            staff.set_password('staff123')

        db.session.commit()

        # Seed Restaurant Tables if empty
        if RestaurantTable.query.count() == 0:
            tables = [
                RestaurantTable(table_number='T-01', capacity=2, status='Available'),
                RestaurantTable(table_number='T-02', capacity=4, status='Available'),
                RestaurantTable(table_number='T-03', capacity=4, status='Available'),
                RestaurantTable(table_number='T-04', capacity=6, status='Available'),
            ]
            db.session.add_all(tables)
            db.session.commit()
            print(f"[+] Populated sample tables: {len(tables)}")

        # Seed Menu Items if empty
        if MenuItem.query.count() == 0:
            menu_items = [
                MenuItem(name='Jollof Rice with Fried Chicken', category='Main Course', price=45.00, status='Available', description='Smoky Ghanaian Jollof rice served with spicy fried chicken and kelewele.'),
                MenuItem(name='Banku with Tilapia', category='Main Course', price=60.00, status='Available', description='Fresh grilled Tilapia served with hot pepper sauce and corn banku.'),
                MenuItem(name='Fried Plantain & Kelewele', category='Starters', price=20.00, status='Available', description='Crispy spiced fried plantain cubes.'),
                MenuItem(name='Fresh Pineapple Juice', category='Beverages', price=15.00, status='Available', description='100% natural freshly squeezed pineapple juice.'),
                MenuItem(name='Chilled Club Beer (600ml)', category='Beverages', price=25.00, status='Available', description='Cold Club Premium Lager.'),
            ]
            db.session.add_all(menu_items)
            db.session.commit()
            print(f"[+] Populated sample menu items: {len(menu_items)}")

        # Seed Customers if empty
        if Customer.query.count() == 0:
            customers = [
                Customer(full_name='Ama Mensah', phone_number='0241002003', email='ama@gmail.com'),
                Customer(full_name='Kojo Boateng', phone_number='0277334455', email='kojo@yahoo.com'),
            ]
            db.session.add_all(customers)
            db.session.commit()
            print(f"[+] Populated sample customers: {len(customers)}")

        print("[+] DineFlow database seeding completed successfully!")

if __name__ == '__main__':
    seed_database()
