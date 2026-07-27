# DineFlow — Restaurant Management System

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-black.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-orange.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**DineFlow** is a modern, web-based Restaurant Management System designed for dining establishments, cafes, and eateries. It streamlines restaurant operations — from table management and menu ordering to bill settlement, payment processing, and daily sales analytics.

---

## 🌟 Key Features

| Feature | Description |
|---------|-------------|
| **User & Role Management** | Multi-role authentication (`Administrator`, `Manager`, `Waiter/Waitress`, `Cashier`). |
| **Table Management** | Manage dining tables, capacities, and real-time availability status (`Available`, `Occupied`, `Reserved`). |
| **Menu Catalog** | Manage categorized food & beverage items with prices formatted in Ghana Cedi (`GH₵`). |
| **Order Processing** | Support Dine-In, Takeaway, and Delivery orders with live order status tracking (`Open`, `In Progress`, `Ready`, `Completed`, `Cancelled`). |
| **Payments & Receipts** | Process cash, Mobile Money, and bank card payments with automatic printable receipts. |
| **Reports & Analytics** | Detailed revenue reports, item sales breakdown, and performance dashboards. |

---

## 🏗️ Tech Stack

- **Backend Framework:** Python Flask (Blueprint architecture, Application Factory pattern)
- **Database:** MySQL / MariaDB via SQLAlchemy ORM (PyMySQL driver)
- **Authentication:** Flask-Login with secure password hashing (`werkzeug.security`)
- **Frontend:** HTML5, CSS3, Bootstrap 5, FontAwesome icons, Chart.js analytics

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- MySQL Server (version 8.0 or MariaDB equivalent)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kingenious0/dineflow.git
   cd dineflow
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables:**
   Create a `.env` file in the root directory:
   ```env
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=dineflow-super-secret-key
   DATABASE_URL=mysql+pymysql://root:1234@localhost:3306/dineflow_db
   ```

5. **Seed Database:**
   ```bash
   python seed.py
   ```

6. **Run the Application:**
   ```bash
   python run.py
   ```
   Open your browser at `http://127.0.0.1:5000`.

---

## 🔑 Demo Login Credentials

| Role | Username / Email | Password |
|------|------------------|----------|
| Administrator | `admin@dineflow.com` | `admin123` |
| Manager | `manager@dineflow.com` | `manager123` |
| Cashier | `cashier@dineflow.com` | `cashier123` |
| Waiter | `waiter@dineflow.com` | `waiter123` |

---

## 📄 License

This project is open-source under the MIT License.
