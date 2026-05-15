try:
    from flask import Flask, render_template, request, redirect, session, url_for, jsonify, flash
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
    # Get filter parameters from URL
    search_query = request.args.get('search', '')
    selected_category = request.args.get('category', '')
    
    # Start with all products
    filtered_products = PRODUCTS.copy()
    
    # Apply search filter
    if search_query:
        search_lower = search_query.lower()
        filtered_products = [p for p in filtered_products 
                            if search_lower in p['name'].lower() 
                            or search_lower in p['sku'].lower()]
    
    # Apply category filter
    if selected_category:
        filtered_products = [p for p in filtered_products 
                            if p['category'] == selected_category]
    
    # Calculate stats from filtered products
    low_stock_items = len([p for p in filtered_products 
                          if p['stock_qty'] <= p['reorder_level'] and p['stock_qty'] > 0])
    categories_used = len(set([p['category'] for p in filtered_products]))
    
    return render_template('products.html',
        active='products',
        page_title='Products',
        current_date=today(),
        low_stock_count=len([p for p in PRODUCTS if p['stock_qty'] <= p['reorder_level']]),
        products=filtered_products,
        categories=CATEGORIES,
        suppliers=SUPPLIERS,
        low_stock_items=low_stock_items,
        categories_used=categories_used,
        search_query=search_query,
        selected_category=selected_category
    )

@app.route('/products/add', methods=['POST'])
def add_product():
    # TODO: Replace with Oracle INSERT when DB is ready
    return redirect('/products')

@app.route('/products/edit/<int:id>', methods=['POST'])
def edit_product(id):
    # TODO: Replace with Oracle UPDATE when DB is ready
    return redirect('/products')

@app.route('/products/delete/<int:id>', methods=['POST'])
def delete_product(id):
    # TODO: Replace with Oracle DELETE when DB is ready
    return redirect('/products')

# ═══════════════════════════════════════════════════════════
# CATEGORIES
# ═══════════════════════════════════════════════════════════

@app.route('/categories')
def categories():
    main_categories = [c for c in CATEGORIES if c['parent_name'] is None]           
    sub_categories = [c for c in CATEGORIES if c['parent_name'] is not None]    


    return render_template('categories.html',
        active          = 'categories',
        page_title      = 'Categories',
        current_date    = today(),
        low_stock_count = len(LOW_STOCK),
        categories      = CATEGORIES,
        main_categories = main_categories,
        sub_categories  = sub_categories,
    )

@app.route('/categories/add', methods=['POST'])
def add_category():
    # TODO: Replace with Oracle INSERT when DB is ready
    return redirect('/categories')

@app.route('/categories/edit/<int:id>', methods=['POST'])
def edit_category(id):
    # TODO: Replace with Oracle UPDATE when DB is ready
    return redirect('/categories')

@app.route('/categories/delete/<int:id>', methods=['POST'])
def delete_category(id):
    # TODO: Replace with Oracle DELETE when DB is ready
    flash('Category deleted successfully.', 'success')
    return redirect('/categories')

# ═══════════════════════════════════════════════════════════
# SUPPLIERS
# ═══════════════════════════════════════════════════════════

@app.route('/supplier')
def suppliers():
    search_query = request.args.get('search', '').strip()
    selected_rating = request.args.get('rating', '').strip()

    filtered_suppliers = SUPPLIERS.copy()
    if search_query:
        sq = search_query.lower()
        filtered_suppliers = [s for s in filtered_suppliers if sq in s['name'].lower()]

    if selected_rating:
        try:
            rating_val = float(selected_rating)
            filtered_suppliers = [s for s in filtered_suppliers if s.get('rating', 0) >= rating_val]
        except ValueError:
            # ignore invalid rating filter
            pass

    return render_template('supplier.html',
        active          = 'supplier',
        page_title      = 'Supplier',
        current_date    = today(),
        low_stock_count = len(LOW_STOCK),
        suppliers       = filtered_suppliers,
        search_query    = search_query,
        selected_rating = selected_rating
    )

@app.route('/supplier/add', methods=['POST'])
def add_supplier():
    # TODO: Replace with Oracle INSERT when DB is ready
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    address = request.form.get('address', '').strip()
    rating_raw = request.form.get('rating', '').strip()
    
  

    new_supplier = {
        'id': len(SUPPLIERS) + 1,
        'name': name,
        'phone': phone,
        'email': email,
        'address': address,
        'rating': float(rating_raw) if rating_raw != '' else 0.0
    }
    SUPPLIERS.append(new_supplier)    
    flash(f'Supplier "{name}" added successfully.', 'success')
    return redirect('/supplier')

@app.route('/supplier/edit/<int:id>', methods=['GET', 'POST'])
def edit_supplier(id):
    # TODO: Replace with Oracle UPDATE when DB is ready
    supplier = next((s for s in SUPPLIERS if s['id'] == id), None)
    if not supplier:
        flash(f'Supplier "{id}" not found.', 'danger')
        return redirect('/supplier')

    if request.method == 'POST':
        supplier['name'] = request.form.get('name', supplier.get('name'))
        supplier['phone'] = request.form.get('phone', supplier.get('phone'))
        supplier['email'] = request.form.get('email', supplier.get('email'))
        supplier['address'] = request.form.get('address', supplier.get('address'))
        rating_raw = request.form.get('rating', '')
        try:
            supplier['rating'] = float(rating_raw) if rating_raw != '' else supplier.get('rating', 0.0)
        except ValueError:
            supplier['rating'] = supplier.get('rating', 0.0)
        flash(f'Supplier "{supplier["name"]}" updated successfully.', 'success')
        return redirect('/supplier')

    return render_template(
        'edit_supplier.html', 
        supplier = supplier,
        active = 'supplier',
        page_title = f'Edit Supplier - {supplier["name"]}',
        current_date = today(),
        low_stock_count = len(LOW_STOCK)
        )

@app.route('/supplier/delete/<int:id>', methods=['POST'])
def delete_supplier(id):
    # TODO: Replace with Oracle DELETE when DB is ready
    global SUPPLIERS
    supplier = next((s for s in SUPPLIERS if s['id'] == id), None)
    if not supplier:
        flash(f'Supplier "{id}" not found.', 'danger')
        return redirect('/supplier')

    SUPPLIERS = [s for s in SUPPLIERS if s['id'] != id]
    flash(f'Supplier "{supplier["name"]}" deleted successfully.', 'success')
    return redirect('/supplier')

# ═══════════════════════════════════════════════════════════
# USERS
# ═══════════════════════════════════════════════════════════

@app.route('/users')
def users():
    # Get search parameter
    search_query = request.args.get('search', '').strip()
    
    # Filter users
    filtered_users = USERS.copy()
    if search_query:
        sq = search_query.lower()
        filtered_users = [u for u in filtered_users 
                         if sq in u['fullname'].lower() 
                         or sq in u['username'].lower()]
    
    return render_template('users.html',
        active='users',
        page_title='Users',
        current_date=today(),
        low_stock_count=len(LOW_STOCK),
        users=filtered_users,
        search_query=search_query
    )

@app.route('/users/add', methods=['POST'])
def add_user():
    # TODO: Replace with Oracle INSERT when DB is ready
    fullname = request.form.get('fullname')
    username = request.form.get('username')
    role = request.form.get('role')
    is_active = 1 if request.form.get('is_active') == '1' else 0
    
    new_user = {
        'id': len(USERS) + 1,
        'fullname': fullname,
        'username': username,
        'role': role,
        'is_active': is_active,
        'date_created': today()
    }
    USERS.append(new_user)
    flash(f'User "{fullname}" added successfully!', 'success')
    return redirect('/users')

@app.route('/users/edit/<int:id>', methods=['POST'])
def edit_user(id):
    # TODO: Replace with Oracle UPDATE when DB is ready
    user = next((u for u in USERS if u['id'] == id), None)
    if user:
        user['fullname'] = request.form.get('fullname', user['fullname'])
        user['username'] = request.form.get('username', user['username'])
        user['role'] = request.form.get('role', user['role'])
        user['is_active'] = 1 if request.form.get('is_active') == '1' else user['is_active']
        flash(f'User "{user["fullname"]}" updated successfully!', 'success')
    else:
        flash(f'User not found!', 'danger')
    return redirect('/users')

@app.route('/users/delete/<int:id>', methods=['POST'])
def delete_user(id):
    # TODO: Replace with Oracle DELETE when DB is ready
    global USERS
    user = next((u for u in USERS if u['id'] == id), None)
    if user:
        USERS = [u for u in USERS if u['id'] != id]
        flash(f'User "{user["fullname"]}" deleted successfully!', 'success')
    else:
        flash(f'User not found!', 'danger')
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
    search   = request.args.get('search', '').lower()
    status   = request.args.get('status', '')
    supplier = request.args.get('supplier', '')

    filtered = PURCHASES

    if search:
        filtered = [p for p in filtered
                    if search in p['supplier'].lower()
                    or search in p['status'].lower()
                    or search in p['created_by'].lower()]
    if status:
        filtered = [p for p in filtered
                    if p['status'] == status]
    if supplier:
        filtered = [p for p in filtered
                    if p['supplier'] == supplier]

    total_purchases = len(filtered)
    pending_orders  = len([p for p in filtered
                           if p['status'] == 'Pending'])
    received_orders = len([p for p in filtered
                           if p['status'] == 'Received'])

    return render_template('purchases.html',
        active          = 'purchases',
        page_title      = 'Purchases',
        current_date    = today(),
        low_stock_count = len(LOW_STOCK),
        purchases       = filtered,
        suppliers       = SUPPLIERS,
        products        = PRODUCTS,
        total_purchases = total_purchases,
        pending_orders  = pending_orders,
        received_orders = received_orders,
        selected_status   = status,
        selected_supplier = supplier,
        search_query      = search
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
    # Get filter parameters
    search = request.args.get('search', '')
    txn_type = request.args.get('type', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    page = request.args.get('page', 1, type=int)
    
    # Start with all transactions
    filtered = TRANSACTIONS.copy()
    
    # Apply search filter
    if search:
        search_lower = search.lower()
        filtered = [t for t in filtered 
                   if search_lower in t['product'].lower()
                   or search_lower in t.get('notes', '').lower()]
    
    # Apply type filter
    if txn_type:
        type_map = {
            'IN': 'Stock In',
            'OUT': 'Stock Out', 
            'ADJ': 'Adjustment',
            'RTN': 'Return',
            'TRF': 'Transfer'
        }
        mapped_type = type_map.get(txn_type, txn_type)
        filtered = [t for t in filtered if t['type'] == mapped_type]
    
    # Calculate summary
    today_str = today()
    summary = {
        'total_transactions': len(TRANSACTIONS),
        'stock_in_today': len([t for t in TRANSACTIONS if t['type'] == 'Stock In' and t['date'].startswith(today_str[:6])]),
        'stock_out_today': len([t for t in TRANSACTIONS if t['type'] == 'Stock Out' and t['date'].startswith(today_str[:6])]),
        'adjustments_today': len([t for t in TRANSACTIONS if t['type'] == 'Adjustment' and t['date'].startswith(today_str[:6])])
    }
    
    # Prepare transactions for template
    transactions = []
    for t in filtered:
        # Determine quantity sign
        qty = t['quantity']
        if t['type'] == 'Stock Out':
            qty = -abs(qty)
        
        transactions.append({
            'id': t['id'],
            'reference': f'TXN-{t["id"]:04d}',
            'created_at': t['date'],  # Will be handled in template
            'product_name': t['product'],
            'sku': f'SKU-{t["id"]:03d}',  # Generate from product or ID
            'category': 'General',  # You can add category to your data
            'transaction_type': 'IN' if t['type'] == 'Stock In' else ('OUT' if t['type'] == 'Stock Out' else 'ADJ'),
            'qty_before': 0,  # You'd need stock history to calculate this
            'quantity': abs(qty),
            'qty_after': 0,  # You'd need stock history to calculate this
            'warehouse': 'Main',
            'user_name': t['performed_by'],
            'notes': t.get('notes', ''),
            'type_display': t['type']
        })
    
    # Simple pagination
    per_page = 20
    total = len(transactions)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = transactions[start:end]
    
    pagination = {
        'page': page,
        'pages': (total + per_page - 1) // per_page,
        'total': total,
        'has_prev': page > 1,
        'has_next': end < total,
        'prev_num': page - 1,
        'next_num': page + 1,
        'first': start + 1 if total > 0 else 0,
        'last': min(end, total)
    }
    
    filters = {
        'search': search,
        'type': txn_type,
        'date_from': date_from,
        'date_to': date_to
    }
    
    return render_template('stock_transactions.html',
        active='stock',
        page_title='Stock Transactions',
        current_date=today(),
        low_stock_count=len(LOW_STOCK),
        transactions=paginated,
        products=PRODUCTS,
        summary=summary,
        filters=filters,
        pagination=pagination
    )

@app.route('/stock/transaction/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        # TODO: Add transaction logic
        flash('Transaction added successfully!', 'success')
        return redirect('/stock-transactions')
    return render_template('add_transaction.html',
        active='stock',
        page_title='Add Transaction',
        current_date=today(),
        low_stock_count=len(LOW_STOCK),
        products=PRODUCTS
    )

@app.route('/stock/transaction/view/<int:id>')
def view_transaction(id):
    transaction = next((t for t in TRANSACTIONS if t['id'] == id), None)
    if not transaction:
        flash('Transaction not found!', 'danger')
        return redirect('/stock-transactions')
    return render_template('view_transaction.html',
        active='stock',
        page_title='View Transaction',
        current_date=today(),
        low_stock_count=len(LOW_STOCK),
        transaction=transaction
    )

@app.route('/stock/transaction/edit/<int:id>', methods=['GET', 'POST'])
def edit_transaction(id):
    transaction = next((t for t in TRANSACTIONS if t['id'] == id), None)
    if not transaction:
        flash('Transaction not found!', 'danger')
        return redirect('/stock-transactions')
    
    if request.method == 'POST':
        # TODO: Update transaction logic
        flash('Transaction updated successfully!', 'success')
        return redirect('/stock-transactions')
    
    return render_template('edit_transaction.html',
        active='stock',
        page_title='Edit Transaction',
        current_date=today(),
        low_stock_count=len(LOW_STOCK),
        transaction=transaction,
        products=PRODUCTS
    )

@app.route('/stock/transactions/export')
def export_transactions():
    # TODO: Generate CSV export
    flash('Export feature coming soon!', 'info')
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
    # Read filter values from URL
    period    = request.args.get('period', 'this_month')
    date_from = request.args.get('date_from', '')
    date_to   = request.args.get('date_to', '')

    return render_template('reports.html',
        active          = 'reports',
        page_title      = 'Reports',
        current_date    = today(),
        low_stock_count = len(LOW_STOCK),

        # KPI strip
        kpi = {
            'total_revenue':   sum(s['total'] for s in SALES),
            'total_purchases': sum(p['total'] for p in PURCHASES),
            'gross_profit':    round(sum(s['total'] for s in SALES) -
                               sum(p['total'] for p in PURCHASES), 2),
            'profit_margin':   0,
            'stock_value':     round(sum(
                               p['stock_qty'] * p['cost_price']
                               for p in PRODUCTS), 2),
            'total_sku':       len(PRODUCTS),
            'revenue_growth':  0,
            'purchase_growth': 0,
        },

        # Sales tab
        sales = {
            'total_amount':       sum(s['total'] for s in SALES),
            'total_orders':       len(SALES),
            'avg_order_value':    round(
                                  sum(s['total'] for s in SALES) /
                                  len(SALES), 2) if SALES else 0,
            'top_product':        'Coca Cola 500ml',
            'top_product_qty':    50,
            'total_returns':      0,
            'return_count':       0,
            'total_units':        sum(s['item_count'] for s in SALES),
            'total_revenue':      sum(s['total'] for s in SALES),
            'total_cogs':         0,
            'total_gross_profit': 0,
            'overall_margin':     0,
            'items':              [],
            'customers':          [],
        },

        # Purchases tab
        purchases = {
            'total_amount':         sum(p['total'] for p in PURCHASES),
            'total_orders':         len(PURCHASES),
            'total_units':          0,
            'top_supplier':         'ABC Distributors',
            'pending_orders':       len([p for p in PURCHASES
                                    if p['status'] == 'Pending']),
            'grand_units_ordered':  0,
            'grand_units_received': 0,
            'grand_total_cost':     sum(p['total'] for p in PURCHASES),
            'items':                [],
            'suppliers':            [],
        },

        # Inventory valuation tab
        valuation = {
            'total_value':        round(sum(
                                  p['stock_qty'] * p['cost_price']
                                  for p in PRODUCTS), 2),
            'retail_value':       round(sum(
                                  p['stock_qty'] * p['unit_price']
                                  for p in PRODUCTS), 2),
            'low_stock_count':    len(LOW_STOCK),
            'dead_stock_count':   0,
            'method':             'Weighted Average Cost (WAC)',
            'as_at':              today(),
            'total_qty':          sum(p['stock_qty'] for p in PRODUCTS),
            'total_cost_value':   round(sum(
                                  p['stock_qty'] * p['cost_price']
                                  for p in PRODUCTS), 2),
            'total_retail_value': round(sum(
                                  p['stock_qty'] * p['unit_price']
                                  for p in PRODUCTS), 2),
            'in_stock_count':     len([p for p in PRODUCTS
                                  if p['stock_qty'] > p['reorder_level']]),
            'out_of_stock_count': len([p for p in PRODUCTS
                                  if p['stock_qty'] == 0]),
            'items':              [],
        },

        # Filters — now reads from URL so dropdowns remember selection
        filters = {
            'period':    period,
            'date_from': date_from,
            'date_to':   date_to,
        },
    )
# ═══════════════════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    app.run(debug=True)