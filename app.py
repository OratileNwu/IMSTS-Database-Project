try:
    from flask import Flask, render_template, request, redirect, session, url_for, jsonify
except Exception as e:
    raise RuntimeError(
        "Missing dependency: Flask is not installed or cannot be resolved. "
        "Install it in your environment with: pip install Flask\n"
        f"Original import error: {e}"
    )
from datetime import date

app = Flask(__name__)
app.secret_key = 'imsts_secret_key_2026'

# ═══════════════════════════════════════════════════════════
# DUMMY DATA — Replace with Oracle queries when DB is ready
# ═══════════════════════════════════════════════════════════

PRODUCTS = [
    {'id': 1, 'name': 'Coca Cola 500ml', 'sku': 'SKU-001',
     'category': 'Beverages', 'supplier': 'ABC Distributors',
     'unit_price': 15.00, 'cost_price': 10.00,
     'stock_qty': 50, 'reorder_level': 20, 'max_stock': 200},
    {'id': 2, 'name': "Lay's Chips 120g", 'sku': 'SKU-002',
     'category': 'Snacks', 'supplier': 'XYZ Suppliers',
     'unit_price': 22.00, 'cost_price': 15.00,
     'stock_qty': 8, 'reorder_level': 15, 'max_stock': 150},
    {'id': 3, 'name': 'Aquelle Water 1L', 'sku': 'SKU-003',
     'category': 'Beverages', 'supplier': 'ABC Distributors',
     'unit_price': 12.00, 'cost_price': 7.00,
     'stock_qty': 5, 'reorder_level': 30, 'max_stock': 300},
    {'id': 4, 'name': 'Simba Chips 120g', 'sku': 'SKU-004',
     'category': 'Snacks', 'supplier': 'XYZ Suppliers',
     'unit_price': 20.00, 'cost_price': 13.00,
     'stock_qty': 100, 'reorder_level': 25, 'max_stock': 200},
    {'id': 5, 'name': 'Ricoffy 250g', 'sku': 'SKU-005',
     'category': 'Hot Drinks', 'supplier': 'Fresh Supplies',
     'unit_price': 65.00, 'cost_price': 45.00,
     'stock_qty': 3, 'reorder_level': 10, 'max_stock': 100},
    {'id': 6, 'name': 'Lipton Tea 100s', 'sku': 'SKU-006',
     'category': 'Hot Drinks', 'supplier': 'Fresh Supplies',
     'unit_price': 45.00, 'cost_price': 30.00,
     'stock_qty': 60, 'reorder_level': 15, 'max_stock': 120},
    {'id': 7, 'name': 'Albany Bread 700g', 'sku': 'SKU-007',
     'category': 'Bakery', 'supplier': 'ABC Distributors',
     'unit_price': 18.00, 'cost_price': 12.00,
     'stock_qty': 25, 'reorder_level': 20, 'max_stock': 100},
    {'id': 8, 'name': 'Clover Full Cream Milk 1L', 'sku': 'SKU-008',
     'category': 'Dairy', 'supplier': 'XYZ Suppliers',
     'unit_price': 24.00, 'cost_price': 18.00,
     'stock_qty': 4, 'reorder_level': 20, 'max_stock': 150},
]

CATEGORIES = [
    {'id': 1, 'name': 'Beverages',
     'description': 'All drinks and beverages',
     'parent_name': None},
    {'id': 2, 'name': 'Snacks',
     'description': 'All snack foods',
     'parent_name': None},
    {'id': 3, 'name': 'Hot Drinks',
     'description': 'Tea and coffee products',
     'parent_name': 'Beverages'},
    {'id': 4, 'name': 'Cold Drinks',
     'description': 'Fizzy and cold drinks',
     'parent_name': 'Beverages'},
    {'id': 5, 'name': 'Chips',
     'description': 'All chip varieties',
     'parent_name': 'Snacks'},
    {'id': 6, 'name': 'Bakery',
     'description': 'Bread and baked goods',
     'parent_name': None},
    {'id': 7, 'name': 'Dairy',
     'description': 'Milk and dairy products',
     'parent_name': None},
]

SUPPLIERS = [
    {'id': 1, 'name': 'ABC Distributors',
     'phone': '011 123 4567',
     'email': 'orders@abcdist.co.za',
     'address': '12 Main Street, Johannesburg',
     'rating': 4.5},
    {'id': 2, 'name': 'XYZ Suppliers',
     'phone': '012 987 6543',
     'email': 'supply@xyz.co.za',
     'address': '5 Church Street, Pretoria',
     'rating': 3.2},
    {'id': 3, 'name': 'Fresh Supplies',
     'phone': '031 555 7890',
     'email': 'info@freshsupplies.co.za',
     'address': '8 Beach Road, Durban',
     'rating': 1.8},
    {'id': 4, 'name': 'Metro Wholesale',
     'phone': '021 444 3210',
     'email': 'metro@wholesale.co.za',
     'address': '3 Bree Street, Cape Town',
     'rating': 4.0},
    {'id': 5, 'name': 'Rapid Deliveries',
     'phone': '011 777 8888',
     'email': 'rapid@deliveries.co.za',
     'address': '99 Industrial Road, Germiston',
     'rating': 2.7},
]

USERS = [
    {'id': 1, 'fullname': 'Oratile Riet',
     'username': 'oriet',
     'role': 'Admin',
     'date_created': '01 Jan 2026',
     'is_active': 1},
    {'id': 2, 'fullname': 'Kamo Mohapanele',
     'username': 'kmohapanele',
     'role': 'Manager',
     'date_created': '01 Jan 2026',
     'is_active': 1},
    {'id': 3, 'fullname': 'Refilwe Sekgotha',
     'username': 'rsekgotha',
     'role': 'Inventory Clerk',
     'date_created': '01 Jan 2026',
     'is_active': 1},
    {'id': 4, 'fullname': 'Kamo Semara',
     'username': 'ksemara',
     'role': 'Sales Cashier',
     'date_created': '01 Jan 2026',
     'is_active': 1},
    {'id': 5, 'fullname': 'Musa Mazibuko',
     'username': 'mmazibuko',
     'role': 'Sales Cashier',
     'date_created': '01 Jan 2026',
     'is_active': 0},
    {'id': 6, 'fullname': 'Noma Boyise',
     'username': 'nboyise',
     'role': 'Inventory Clerk',
     'date_created': '15 Jan 2026',
     'is_active': 1},
]

SALES = [
    {'id': 1, 'date': '09 May 2026 08:45',
     'cashier': 'Kamo Semara',
     'item_count': 3, 'total': 49.00,
     'payment': 'Cash'},
    {'id': 2, 'date': '09 May 2026 10:12',
     'cashier': 'Kamo Semara',
     'item_count': 1, 'total': 15.00,
     'payment': 'Card'},
    {'id': 3, 'date': '08 May 2026 14:30',
     'cashier': 'Noma Boyise',
     'item_count': 5, 'total': 120.00,
     'payment': 'EFT'},
    {'id': 4, 'date': '08 May 2026 09:00',
     'cashier': 'Kamo Semara',
     'item_count': 2, 'total': 37.00,
     'payment': 'Cash'},
    {'id': 5, 'date': '07 May 2026 16:20',
     'cashier': 'Noma Boyise',
     'item_count': 4, 'total': 88.00,
     'payment': 'Card'},
    {'id': 6, 'date': '07 May 2026 11:05',
     'cashier': 'Kamo Semara',
     'item_count': 6, 'total': 215.00,
     'payment': 'EFT'},
    {'id': 7, 'date': '06 May 2026 13:45',
     'cashier': 'Noma Boyise',
     'item_count': 2, 'total': 44.00,
     'payment': 'Cash'},
    {'id': 8, 'date': '06 May 2026 10:30',
     'cashier': 'Kamo Semara',
     'item_count': 3, 'total': 67.00,
     'payment': 'Card'},
]

PURCHASES = [
    {'id': 1, 'date': '05 May 2026',
     'supplier': 'ABC Distributors',
     'created_by': 'Refilwe Sekgotha',
     'total': 500.00, 'status': 'Received'},
    {'id': 2, 'date': '07 May 2026',
     'supplier': 'XYZ Suppliers',
     'created_by': 'Refilwe Sekgotha',
     'total': 320.00, 'status': 'Pending'},
    {'id': 3, 'date': '08 May 2026',
     'supplier': 'Fresh Supplies',
     'created_by': 'Kamo Mohapanele',
     'total': 180.00, 'status': 'Pending'},
    {'id': 4, 'date': '01 May 2026',
     'supplier': 'ABC Distributors',
     'created_by': 'Refilwe Sekgotha',
     'total': 750.00, 'status': 'Cancelled'},
    {'id': 5, 'date': '03 May 2026',
     'supplier': 'Metro Wholesale',
     'created_by': 'Kamo Mohapanele',
     'total': 1200.00, 'status': 'Received'},
]

TRANSACTIONS = [
    {'id': 1, 'product': 'Coca Cola 500ml',
     'type': 'Stock In', 'quantity': 100,
     'date': '05 May 2026 09:00',
     'performed_by': 'Refilwe Sekgotha',
     'reference_id': 1,
     'notes': 'Purchase order received'},
    {'id': 2, 'product': 'Coca Cola 500ml',
     'type': 'Stock Out', 'quantity': -5,
     'date': '09 May 2026 08:45',
     'performed_by': 'Kamo Semara',
     'reference_id': 1,
     'notes': 'Sale processed'},
    {'id': 3, 'product': "Lay's Chips 120g",
     'type': 'Stock In', 'quantity': 50,
     'date': '05 May 2026 09:00',
     'performed_by': 'Refilwe Sekgotha',
     'reference_id': 1,
     'notes': 'Purchase order received'},
    {'id': 4, 'product': 'Ricoffy 250g',
     'type': 'Adjustment', 'quantity': -2,
     'date': '06 May 2026 14:00',
     'performed_by': 'Kamo Mohapanele',
     'reference_id': None,
     'notes': 'Damaged stock removed'},
    {'id': 5, 'product': 'Aquelle Water 1L',
     'type': 'Stock In', 'quantity': 200,
     'date': '03 May 2026 10:00',
     'performed_by': 'Refilwe Sekgotha',
     'reference_id': 5,
     'notes': 'Purchase order received'},
    {'id': 6, 'product': 'Clover Full Cream Milk 1L',
     'type': 'Stock Out', 'quantity': -8,
     'date': '08 May 2026 14:30',
     'performed_by': 'Noma Boyise',
     'reference_id': 3,
     'notes': 'Sale processed'},
]

AUDIT_LOGS = [
    {'id': 1, 'username': 'Oratile Riet',
     'action': 'INSERT', 'table_affected': 'Product',
     'record_id': 1,
     'action_date': '01 May 2026 08:00',
     'old_value': None,
     'new_value': '{"name": "Coca Cola 500ml", "price": 15.00}'},
    {'id': 2, 'username': 'Kamo Mohapanele',
     'action': 'UPDATE', 'table_affected': 'Product',
     'record_id': 1,
     'action_date': '03 May 2026 10:30',
     'old_value': '{"unit_price": 14.00}',
     'new_value': '{"unit_price": 15.00}'},
    {'id': 3, 'username': 'Refilwe Sekgotha',
     'action': 'DELETE', 'table_affected': 'Supplier',
     'record_id': 6,
     'action_date': '04 May 2026 14:15',
     'old_value': '{"name": "Old Supplier Co"}',
     'new_value': None},
    {'id': 4, 'username': 'Oratile Riet',
     'action': 'INSERT', 'table_affected': 'User',
     'record_id': 6,
     'action_date': '15 Jan 2026 09:00',
     'old_value': None,
     'new_value': '{"fullname": "Noma Boyise", "role": "Inventory Clerk"}'},
    {'id': 5, 'username': 'Kamo Mohapanele',
     'action': 'UPDATE', 'table_affected': 'Purchase',
     'record_id': 1,
     'action_date': '05 May 2026 11:00',
     'old_value': '{"status": "Pending"}',
     'new_value': '{"status": "Received"}'},
    {'id': 6, 'username': 'Oratile Riet',
     'action': 'UPDATE', 'table_affected': 'User',
     'record_id': 5,
     'action_date': '20 Apr 2026 16:00',
     'old_value': '{"is_active": 1}',
     'new_value': '{"is_active": 0}'},
]

LOW_STOCK = [
    {'id': 2, 'name': "Lay's Chips 120g",
     'category': 'Snacks', 'stock_qty': 8,
     'reorder_level': 15, 'stock_pct': 16,
     'supplier': 'XYZ Suppliers'},
    {'id': 3, 'name': 'Aquelle Water 1L',
     'category': 'Beverages', 'stock_qty': 5,
     'reorder_level': 30, 'stock_pct': 10,
     'supplier': 'ABC Distributors'},
    {'id': 5, 'name': 'Ricoffy 250g',
     'category': 'Hot Drinks', 'stock_qty': 3,
     'reorder_level': 10, 'stock_pct': 6,
     'supplier': 'Fresh Supplies'},
    {'id': 8, 'name': 'Clover Full Cream Milk 1L',
     'category': 'Dairy', 'stock_qty': 4,
     'reorder_level': 20, 'stock_pct': 8,
     'supplier': 'XYZ Suppliers'},
]

# ═══════════════════════════════════════════════════════════
# HELPER FUNCTION
# ═══════════════════════════════════════════════════════════

def today():
    return date.today().strftime('%d %B %Y')

# ═══════════════════════════════════════════════════════════
# LOGIN & LOGOUT
# ═══════════════════════════════════════════════════════════

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Dummy login — replace with Oracle query later
        if username == 'admin' and password == 'admin':
            session['user_id']  = 1
            session['fullname'] = 'Oratile Riet'
            session['role']     = 'Admin'
            return redirect('/dashboard')
        elif username == 'cashier' and password == 'cashier':
            session['user_id']  = 4
            session['fullname'] = 'Kamo Semara'
            session['role']     = 'Sales Cashier'
            return redirect('/dashboard')
        elif username == 'manager' and password == 'manager':
            session['user_id']  = 2
            session['fullname'] = 'Kamo Mohapanele'
            session['role']     = 'Manager'
            return redirect('/dashboard')
        else:
            error = 'Invalid username or password. Please try again.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ═══════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html',
        active            = 'dashboard',
        page_title        = 'Dashboard',
        current_date      = today(),
        total_products    = len(PRODUCTS),
        todays_sales      = 4820,
        low_stock_count   = len(LOW_STOCK),
        pending_purchases = 3,
        recent_sales      = SALES[:5],
        low_stock         = LOW_STOCK
    )

# ── CHART JSON ENDPOINTS (for Chart.js) ─────────────────

@app.route('/api/sales-chart')
def sales_chart():
    return jsonify({
        'labels':    ['01 May','02 May','03 May','04 May',
                      '05 May','06 May','07 May','08 May','09 May'],
        'sales':     [320, 480, 250, 600, 420, 380, 510, 290, 480],
        'purchases': [200, 150, 400, 100, 300, 250, 180, 320, 150]
    })

@app.route('/api/payment-chart')
def payment_chart():
    return jsonify({
        'labels': ['Cash', 'Card', 'EFT'],
        'values': [48, 33, 19]
    })

@app.route('/api/stock-chart')
def stock_chart():
    return jsonify({
        'labels':    ['03 May','04 May','05 May',
                      '06 May','07 May','08 May','09 May'],
        'stock_in':  [50, 0, 100, 0, 30, 0, 20],
        'stock_out': [10, 15, 8,  20, 12, 18, 9]
    })

# ═══════════════════════════════════════════════════════════
# PRODUCTS
# ═══════════════════════════════════════════════════════════

@app.route('/products')
def products():
    return render_template('products.html',
        active          = 'products',
        page_title      = 'Products',
        current_date    = today(),
        low_stock_count = len(LOW_STOCK),
        products        = PRODUCTS,
        categories      = CATEGORIES,
        suppliers       = SUPPLIERS
    )

@app.route('/products/add', methods=['POST'])
def add_product():
    # TODO: Replace with Oracle INSERT when DB is ready
    return redirect('/products')

@app.route('/products/edit/<int:id>', methods=['POST'])
def edit_product(id):
    # TODO: Replace with Oracle UPDATE when DB is ready
    return redirect('/products')

@app.route('/products/delete/<int:id>')
def delete_product(id):
    # TODO: Replace with Oracle DELETE when DB is ready
    return redirect('/products')

# ═══════════════════════════════════════════════════════════
# CATEGORIES
# ═══════════════════════════════════════════════════════════

@app.route('/categories')
def categories():
    return render_template('categories.html',
        active          = 'categories',
        page_title      = 'Categories',
        current_date    = today(),
        low_stock_count = len(LOW_STOCK),
        categories      = CATEGORIES
    )

@app.route('/categories/add', methods=['POST'])
def add_category():
    # TODO: Replace with Oracle INSERT when DB is ready
    return redirect('/categories')

@app.route('/categories/edit/<int:id>', methods=['POST'])
def edit_category(id):
    # TODO: Replace with Oracle UPDATE when DB is ready
    return redirect('/categories')

@app.route('/categories/delete/<int:id>')
def delete_category(id):
    # TODO: Replace with Oracle DELETE when DB is ready
    return redirect('/categories')

# ═══════════════════════════════════════════════════════════
# SUPPLIERS
# ═══════════════════════════════════════════════════════════

@app.route('/supplier')
def suppliers():
    return render_template('supplier.html',
        active          = 'suppliers',
        page_title      = 'Suppliers',
        current_date    = today(),
        low_stock_count = len(LOW_STOCK),
        suppliers       = SUPPLIERS
    )

@app.route('/supplier/add', methods=['POST'])
def add_supplier():
    # TODO: Replace with Oracle INSERT when DB is ready
    return redirect('/supplier')

@app.route('/supplier/edit/<int:id>', methods=['POST'])
def edit_supplier(id):
    # TODO: Replace with Oracle UPDATE when DB is ready
    return redirect('/supplier')

@app.route('/supplier/delete/<int:id>')
def delete_supplier(id):
    # TODO: Replace with Oracle DELETE when DB is ready
    return redirect('/supplier')

# ═══════════════════════════════════════════════════════════
# USERS
# ═══════════════════════════════════════════════════════════

@app.route('/users')
def users():
    return render_template('users.html',
        active          = 'users',
        page_title      = 'Users',
        current_date    = today(),
        low_stock_count = len(LOW_STOCK),
        users           = USERS
    )

@app.route('/users/add', methods=['POST'])
def add_user():
    # TODO: Replace with Oracle INSERT when DB is ready
    return redirect('/users')

@app.route('/users/edit/<int:id>', methods=['POST'])
def edit_user(id):
    # TODO: Replace with Oracle UPDATE when DB is ready
    return redirect('/users')

@app.route('/users/toggle/<int:id>')
def toggle_user(id):
    # TODO: Replace with Oracle UPDATE when DB is ready
    return redirect('/users')

# ═══════════════════════════════════════════════════════════
# SALES
# ═══════════════════════════════════════════════════════════

@app.route('/sales')
def sales():
    return render_template('sales.html',
        active          = 'sales',
        page_title      = 'Sales',
        current_date    = today(),
        low_stock_count = len(LOW_STOCK),
        sales           = SALES,
        products        = PRODUCTS
    )

@app.route('/sales/add', methods=['POST'])
def add_sale():
    # TODO: Replace with Oracle INSERT when DB is ready
    return redirect('/sales')

@app.route('/sales/<int:id>')
def view_sale(id):
    # TODO: Return sale line items when DB is ready
    return redirect('/sales')

# ═══════════════════════════════════════════════════════════
# PURCHASES
# ═══════════════════════════════════════════════════════════

@app.route('/purchases')
def purchases():
    total_purchases = len(PURCHASES)
    pending_orders = len([p for p in PURCHASES if p['status'] == 'Pending'])
    received_orders = len([p for p in PURCHASES if p['status'] == 'Received'])


    return render_template('purchases.html',
        active          = 'purchases',
        page_title      = 'Purchases',
        current_date    = today(),
        low_stock_count = len(LOW_STOCK),
        purchases       = PURCHASES,
        suppliers       = SUPPLIERS,
        products        = PRODUCTS,
        total_purchases = total_purchases,
        pending_orders  = pending_orders,
                received_orders = received_orders
    )

@app.route('/purchases/add', methods=['POST'])
def add_purchase():
    # TODO: Replace with Oracle INSERT when DB is ready
    return redirect('/purchases')

@app.route('/purchases/receive/<int:id>')
def receive_purchase(id):
    # TODO: Update status + stock qty in Oracle when DB is ready
    return redirect('/purchases')

@app.route('/purchases/cancel/<int:id>')
def cancel_purchase(id):
    # TODO: Update status in Oracle when DB is ready
    return redirect('/purchases')

# ═══════════════════════════════════════════════════════════
# STOCK TRANSACTIONS
# ═══════════════════════════════════════════════════════════

@app.route('/stock-transactions')
def stock_transactions():
    return render_template('stock_transactions.html',
        active          = 'stock',
        page_title      = 'Stock Transactions',
        current_date    = today(),
        low_stock_count = len(LOW_STOCK),
        transactions    = TRANSACTIONS,
        products        = PRODUCTS
    )

@app.route('/stock/adjust', methods=['POST'])
def stock_adjust():
    # TODO: INSERT into StockTransaction + UPDATE Product in Oracle
    return redirect('/stock-transactions')

# ═══════════════════════════════════════════════════════════
# AUDIT LOG
# ═══════════════════════════════════════════════════════════

@app.route('/audit-log')
def audit_log():
    return render_template('audit_log.html',
        active          = 'audit',
        page_title      = 'Audit Log',
        current_date    = today(),
        low_stock_count = len(LOW_STOCK),
        audit_logs      = AUDIT_LOGS
    )

# ═══════════════════════════════════════════════════════════
# LOW STOCK ALERTS
# ═══════════════════════════════════════════════════════════

@app.route('/low-stock')
def low_stock():
    out_of_stock = len([p for p in PRODUCTS if p['stock_qty'] == 0])
    suppliers_needed = len(set(p['supplier'] for p in LOW_STOCK))

    return render_template('low_stock.html',
        active          = 'lowstock',
        page_title      = 'Low Stock Alerts',
        current_date    = today(),
        low_stock_count = len(LOW_STOCK),
        low_stock = LOW_STOCK,
        out_of_stock    = out_of_stock,
        suppliers_needed = suppliers_needed 
    )

# ═══════════════════════════════════════════════════════════
# REPORTS
# ═══════════════════════════════════════════════════════════

@app.route('/reports')
def reports():
    return render_template('reports.html',
        active           = 'reports',
        page_title       = 'Reports',
        current_date     = today(),
        low_stock_count  = len(LOW_STOCK),
        sales_report     = SALES,
        sales_total      = sum(s['total'] for s in SALES),
        purchases_report = PURCHASES,
        purchases_total  = sum(p['total'] for p in PURCHASES),
        inventory        = PRODUCTS,
        inventory_total  = round(sum(
            p['stock_qty'] * p['cost_price'] for p in PRODUCTS
        ), 2)
    )

# ═══════════════════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    app.run(debug=True)