
import os
import hashlib
import oracledb
from flask import Flask, render_template, request, redirect, session, jsonify
from datetime import date, datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)


app.secret_key = os.getenv('SECRET_KEY', 'imsts_secret_key_2026')


# ORACLE CONNECTION POOL

pool = oracledb.create_pool(
    user='C##imsts_user',
    password='admin123',
    dsn='localhost:1521/XE',
    min=2,
    max=5,
    increment=1
)

def get_connection():
    try:
        return pool.acquire()
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# HELPERS


def hash_password(password):
    return generate_password_hash(password)

def verify_password(password, hashed):
    return check_password_hash(hashed, password)

def today():
    return date.today().strftime('%d %B %Y')


# ROLE DECORATOR


def role_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            if 'user_id' not in session:
                return redirect('/login')

            if session.get('role') not in allowed_roles:
                return "Access Denied - Insufficient Permissions", 403

            return func(*args, **kwargs)

        return wrapper
    return decorator

# LOGIN


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():

    error = None

    if request.method == 'POST':

        conn = get_connection()

        if not conn:
            return render_template(
                'login.html',
                error='Database connection failed'
            )

        cursor = conn.cursor()

        try:

            login_input = request.form['username']
            password = request.form['password']

            cursor.execute("""
                SELECT UserID,
                       FullName,
                       Role,
                       IsActive,
                       PasswordHash
                FROM User_Account
                WHERE (UserName = :login OR Email = :login)
            """, {'login': login_input})

            user = cursor.fetchone()

            if user:

                user_id = user[0]
                fullname = user[1]
                role = user[2]
                is_active = user[3]
                stored_hash = user[4]

                if is_active != 1:
                    error = "Account inactive"

                elif verify_password(password, stored_hash):

                    session['user_id'] = user_id
                    session['fullname'] = fullname
                    session['role'] = role

                    cursor.execute("""
                        UPDATE User_Account
                        SET LastLogin = CURRENT_TIMESTAMP
                        WHERE UserID = :uid
                    """, {'uid': user_id})

                    conn.commit()

                    return redirect('/dashboard')

                else:
                    error = "Invalid credentials"

            else:
                error = "Invalid credentials"

        except Exception as e:
            error = f"Login error: {str(e)}"

        finally:
            cursor.close()
            conn.close()

    return render_template('login.html', error=error)


# LOGOUT


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# DASHBOARD


@app.route('/dashboard')
@role_required([
    'Admin',
    'Manager',
    'InventoryManager',
    'SalesSupervisor',
    'SalesClerk'
])
def dashboard():

    conn = get_connection()

    if not conn:
        return "Database connection failed", 500

    cursor = conn.cursor()

    try:

        cursor.execute("SELECT COUNT(*) FROM Product")
        total_products = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM LowStockAlert")
        low_stock_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM Purchase
            WHERE OrderStatus = 'Pending'
        """)
        pending_purchases = cursor.fetchone()[0]

        cursor.execute("""
            SELECT NVL(SUM(TotalAmount), 0)
            FROM Sale
            WHERE TRUNC(SaleDate) = TRUNC(SYSDATE)
        """)

        todays_sales = float(cursor.fetchone()[0])

        cursor.execute("""
            SELECT s.SaleID,
                   TO_CHAR(s.SaleDate, 'DD Mon HH24:MI'),
                   u.FullName,
                   COUNT(sl.LineItemID),
                   s.TotalAmount,
                   s.PaymentMethod
            FROM Sale s
            JOIN User_Account u
                ON s.UserID = u.UserID
            LEFT JOIN SaleLineItem sl
                ON s.SaleID = sl.SaleID
            GROUP BY s.SaleID,
                     s.SaleDate,
                     u.FullName,
                     s.TotalAmount,
                     s.PaymentMethod
            ORDER BY s.SaleDate DESC
            FETCH FIRST 5 ROWS ONLY
        """)

        recent_sales = []

        for r in cursor.fetchall():
            recent_sales.append({
                'sale_id': r[0],
                'sale_date': r[1],
                'fullname': r[2],
                'item_count': r[3] or 0,
                'total_amount': float(r[4]),
                'payment_method': r[5]
            })

        return render_template(
            'dashboard.html',
            fullname=session['fullname'],
            role=session['role'],
            total_products=total_products,
            low_stock_count=low_stock_count,
            pending_purchases=pending_purchases,
            todays_sales=todays_sales,
            recent_sales=recent_sales,
            current_date=today()
        )

    except Exception as e:
        return f"Dashboard error: {str(e)}", 500

    finally:
        cursor.close()
        conn.close()


# PRODUCTS


@app.route('/products')
@role_required(['Admin', 'Manager', 'InventoryManager'])
def products():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT p.ProductID,
                   p.ProductName,
                   p.SKU,
                   c.CategoryName,
                   s.SupplierName,
                   p.UnitPrice,
                   p.CostPrice,
                   p.StockQty,
                   p.ReorderLevel,
                   p.MaxStockLevel,
                   p.Description
            FROM Product p
            LEFT JOIN Category c
                ON p.CategoryID = c.CategoryID
            LEFT JOIN Supplier s
                ON p.SupplierID = s.SupplierID
            ORDER BY p.ProductID
        """)

        products = []

        for r in cursor.fetchall():

            products.append({
                'product_id': r[0],
                'product_name': r[1],
                'sku': r[2],
                'category_name': r[3] or 'Uncategorized',
                'supplier_name': r[4] or 'Unknown',
                'unit_price': float(r[5]),
                'cost_price': float(r[6]),
                'stock_qty': r[7],
                'reorder_level': r[8],
                'max_stock_level': r[9],
                'description': r[10] or ''
            })

        cursor.execute("""
            SELECT CategoryID, CategoryName
            FROM Category
            ORDER BY CategoryName
        """)

        categories = [
            {'id': r[0], 'name': r[1]}
            for r in cursor.fetchall()
        ]

        cursor.execute("""
            SELECT SupplierID, SupplierName
            FROM Supplier
            ORDER BY SupplierName
        """)

        suppliers = [
            {'id': r[0], 'name': r[1]}
            for r in cursor.fetchall()
        ]

        return render_template(
            'products.html',
            products=products,
            categories=categories,
            suppliers=suppliers,
            fullname=session['fullname'],
            role=session['role'],
            current_date=today()
        )

    except Exception as e:
        return f"Products error: {str(e)}", 500

    finally:
        cursor.close()
        conn.close()


# ADD PRODUCT


@app.route('/add-product', methods=['GET', 'POST'])
@role_required(['Admin', 'InventoryManager'])
def add_product():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        if request.method == 'GET':

            cursor.execute("""
                SELECT CategoryID, CategoryName
                FROM Category
                ORDER BY CategoryName
            """)

            categories = [
                {'id': r[0], 'name': r[1]}
                for r in cursor.fetchall()
            ]

            cursor.execute("""
                SELECT SupplierID, SupplierName
                FROM Supplier
                ORDER BY SupplierName
            """)

            suppliers = [
                {'id': r[0], 'name': r[1]}
                for r in cursor.fetchall()
            ]

            return render_template(
                'add_product.html',
                categories=categories,
                suppliers=suppliers,
                fullname=session['fullname'],
                role=session['role']
            )

        sku = request.form.get('sku', '').strip()

        if not sku:
            sku = f"SKU_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        cursor.execute("""
            INSERT INTO Product (
                ProductName,
                Description,
                SKU,
                CategoryID,
                SupplierID,
                UnitPrice,
                CostPrice,
                StockQty,
                ReorderLevel,
                MaxStockLevel
            )
            VALUES (
                :name,
                :desc,
                :sku,
                :cat,
                :sup,
                :price,
                :cost,
                0,
                :reorder,
                :maxstock
            )
        """, {
            'name': request.form['product_name'],
            'desc': request.form.get('description', ''),
            'sku': sku,
            'cat': int(request.form['category_id']),
            'sup': int(request.form['supplier_id']),
            'price': float(request.form['unit_price']),
            'cost': float(request.form['cost_price']),
            'reorder': int(request.form['reorder_level']),
            'maxstock': int(request.form['max_stock_level'])
        })

        conn.commit()

        return redirect('/products')

    except Exception as e:

        conn.rollback()
        return f"Add product error: {str(e)}", 500

    finally:
        cursor.close()
        conn.close()


# REPORTS


@app.route('/reports')
@role_required(['Admin', 'Manager'])
def reports():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT *
            FROM DailySalesSummary
            FETCH FIRST 30 ROWS ONLY
        """)

        daily_sales = []

        for r in cursor.fetchall():

            daily_sales.append({
                'sale_day': r[0],
                'number_of_transactions': r[1],
                'total_sales': float(r[2] or 0),
                'average_transaction': float(r[3] or 0),
                'active_cashiers': r[4]
            })

        cursor.execute("""
            SELECT *
            FROM ProductPerformance
            FETCH FIRST 20 ROWS ONLY
        """)

        product_performance = []

        for r in cursor.fetchall():

            product_performance.append({
                'product_id': r[0],
                'product_name': r[1],
                'sku': r[2],
                'category_name': r[3],
                'stock_qty': r[4],
                'unit_price': float(r[5]),
                'total_units_sold': r[6] or 0,
                'total_revenue': float(r[7] or 0),
                'gross_profit': float(r[10] or 0)
            })

        # FIXED SUPPLIER PERFORMANCE INDEXING

        cursor.execute("""
            SELECT *
            FROM SupplierPerformance
        """)

        supplier_performance = []

        for r in cursor.fetchall():

            supplier_performance.append({
                'supplier_id': r[0],
                'supplier_name': r[1],
                'total_orders': r[4] or 0,
                'total_spent': float(r[5] or 0),
                'performance_rating': r[8]
            })

        return render_template(
            'reports.html',
            daily_sales=daily_sales,
            product_performance=product_performance,
            supplier_performance=supplier_performance,
            fullname=session['fullname'],
            role=session['role'],
            current_date=today()
        )

    except Exception as e:
        return f"Reports error: {str(e)}", 500

    finally:
        cursor.close()
        conn.close()


# API ROUTES 


@app.route('/api/low-stock')
@role_required([
    'Admin',
    'Manager',
    'InventoryManager'
])
def low_stock_api():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT ProductName,
                   StockQty,
                   ReorderLevel,
                   AlertLevel
            FROM LowStockAlert
            FETCH FIRST 10 ROWS ONLY
        """)

        results = []

        for r in cursor.fetchall():

            results.append({
                'product_name': r[0],
                'stock_qty': r[1],
                'reorder_level': r[2],
                'alert_level': r[3]
            })

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ERROR HANDLERS


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500


# MAIN


if __name__ == '__main__':

    print("=" * 50)
    print("IMSTS Flask Application Starting...")
    print("=" * 50)

    test_conn = get_connection()

    if test_conn:
        print("✓ Database connection successful")
        test_conn.close()
    else:
        print("✗ Database connection failed")

    print("\nStarting Flask server...")
    print("http://127.0.0.1:5000")

    app.run(
        debug=False,
        host='127.0.0.1',
        port=5000
    )
