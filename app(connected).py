import os
import oracledb
from flask import Flask, render_template, request, redirect, session, jsonify
from datetime import date, datetime
from functools import wraps
from werkzeug.security import check_password_hash
from contextlib import contextmanager


# APP CONFIG


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change_this_in_production")

DB_USER = os.getenv("DB_USER", "C##IMSTS_USER")
DB_PASS = os.getenv("DB_PASS", "admin123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 1521))
DB_SERVICE = os.getenv("DB_SERVICE", "orcl")


# ORACLE CONNECTION POOL


pool = oracledb.create_pool(
    user=DB_USER,
    password=DB_PASS,
    dsn=oracledb.makedsn(DB_HOST, DB_PORT, service_name=DB_SERVICE),
    min=2,
    max=5,
    increment=1
)


# DB CONTEXT MANAGER


@contextmanager
def db_cursor():
    conn = pool.acquire()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()



# HELPERS


def today():
    return date.today().strftime('%d %B %Y')


def role_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return redirect("/login")

            if session.get("role") not in allowed_roles:
                return "Access Denied", 403

            return func(*args, **kwargs)
        return wrapper
    return decorator



# LOGIN


@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        try:
            login_input = request.form["username"]
            password = request.form["password"]

            with db_cursor() as cursor:
                cursor.execute("""
                    SELECT UserID, FullName, Role, IsActive, PasswordHash
                    FROM User_Account
                    WHERE UserName = :login OR Email = :login
                """, {"login": login_input})

                user = cursor.fetchone()

            if not user:
                error = "Invalid credentials"
            else:
                user_id, fullname, role, is_active, stored_hash = user

                if is_active != 1:
                    error = "Account inactive"

                elif stored_hash and check_password_hash(stored_hash, password):

                    session["user_id"] = user_id
                    session["fullname"] = fullname
                    session["role"] = role

                    with db_cursor() as cursor:
                        cursor.execute("""
                            UPDATE User_Account
                            SET LastLogin = CURRENT_TIMESTAMP
                            WHERE UserID = :uid
                        """, {"uid": user_id})

                    return redirect("/dashboard")

                else:
                    error = "Invalid credentials"

        except Exception as e:
            app.logger.error(str(e))
            error = "Login failed"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# DASHBOARD


@app.route("/dashboard")
@role_required(["Admin", "Manager", "InventoryManager", "SalesSupervisor", "SalesClerk"])
def dashboard():
    try:
        with db_cursor() as cursor:
            cursor.execute("""
                SELECT
                    (SELECT COUNT(*) FROM Product),
                    (SELECT COUNT(*) FROM LowStockAlert),
                    (SELECT COUNT(*) FROM Purchase WHERE OrderStatus='Pending')
                FROM dual
            """)
            total_products, low_stock_count, pending_purchases = cursor.fetchone()

            cursor.execute("""
                SELECT NVL(SUM(TotalAmount), 0)
                FROM Sale
                WHERE TRUNC(SaleDate) = TRUNC(SYSDATE)
            """)
            todays_sales = float(cursor.fetchone()[0] or 0)

            cursor.execute("""
                SELECT s.SaleID,
                       TO_CHAR(s.SaleDate, 'DD Mon HH24:MI'),
                       u.FullName,
                       COUNT(sl.LineItemID),
                       s.TotalAmount,
                       s.PaymentMethod
                FROM Sale s
                JOIN User_Account u ON s.UserID = u.UserID
                LEFT JOIN SaleLineItem sl ON s.SaleID = sl.SaleID
                GROUP BY s.SaleID, s.SaleDate, u.FullName, s.TotalAmount, s.PaymentMethod
                ORDER BY s.SaleDate DESC
                FETCH FIRST 5 ROWS ONLY
            """)

            recent_sales = [
                {
                    "sale_id": r[0],
                    "sale_date": r[1],
                    "fullname": r[2],
                    "item_count": r[3] or 0,
                    "total_amount": float(r[4] or 0),
                    "payment_method": r[5]
                }
                for r in cursor.fetchall()
            ]

        return render_template(
            "dashboard.html",
            fullname=session["fullname"],
            role=session["role"],
            total_products=total_products,
            low_stock_count=low_stock_count,
            pending_purchases=pending_purchases,
            todays_sales=todays_sales,
            recent_sales=recent_sales,
            current_date=today()
        )

    except Exception as e:
        return f"Dashboard error: {str(e)}", 500



# PRODUCTS


@app.route("/products")
@role_required(["Admin", "Manager", "InventoryManager"])
def products():
    try:
        with db_cursor() as cursor:
            cursor.execute("""
                SELECT p.ProductID, p.ProductName, p.SKU,
                       c.CategoryName, s.SupplierName,
                       p.UnitPrice, p.CostPrice,
                       p.StockQty, p.ReorderLevel,
                       p.MaxStockLevel, p.Description
                FROM Product p
                LEFT JOIN Category c ON p.CategoryID = c.CategoryID
                LEFT JOIN Supplier s ON p.SupplierID = s.SupplierID
                ORDER BY p.ProductID
            """)

            products = [
                {
                    "product_id": r[0],
                    "product_name": r[1],
                    "sku": r[2],
                    "category_name": r[3] or "Uncategorized",
                    "supplier_name": r[4] or "Unknown",
                    "unit_price": float(r[5]),
                    "cost_price": float(r[6]),
                    "stock_qty": r[7],
                    "reorder_level": r[8],
                    "max_stock_level": r[9],
                    "description": r[10] or ""
                }
                for r in cursor.fetchall()
            ]

        return render_template(
            "products.html",
            products=products,
            fullname=session["fullname"],
            role=session["role"],
            current_date=today()
        )

    except Exception as e:
        return f"Products error: {str(e)}", 500



# SALES PAGE


@app.route("/sales")
@role_required(["Admin", "Manager", "SalesSupervisor", "SalesClerk"])
def sales():
    try:
        with db_cursor() as cursor:
            cursor.execute("""
                SELECT s.SaleID,
                       TO_CHAR(s.SaleDate, 'DD Mon YYYY HH24:MI') AS SaleDate,
                       u.FullName,
                       COUNT(sl.LineItemID) AS ItemCount,
                       s.TotalAmount,
                       s.PaymentMethod
                FROM Sale s
                JOIN User_Account u ON s.UserID = u.UserID
                LEFT JOIN SaleLineItem sl ON s.SaleID = sl.SaleID
                GROUP BY s.SaleID, s.SaleDate, u.FullName, s.TotalAmount, s.PaymentMethod
                ORDER BY s.SaleDate DESC
            """)
            
            sales_list = [
                {
                    "sale_id": r[0],
                    "sale_date": r[1],
                    "fullname": r[2],
                    "item_count": r[3] or 0,
                    "total_amount": float(r[4]),
                    "payment_method": r[5]
                }
                for r in cursor.fetchall()
            ]
            
            cursor.execute("""
                SELECT ProductID, ProductName, UnitPrice, StockQty
                FROM Product
                WHERE StockQty > 0
                ORDER BY ProductName
            """)
            
            products = [
                {
                    "product_id": r[0],
                    "product_name": r[1],
                    "unit_price": float(r[2]),
                    "stock_qty": r[3]
                }
                for r in cursor.fetchall()
            ]
            
        return render_template(
            "sales.html",
            sales=sales_list,
            products=products,
            fullname=session["fullname"],
            role=session["role"],
            current_date=today()
        )
                             
    except Exception as e:
        return f"Sales page error: {str(e)}", 500



# CREATE SALE


@app.route("/create-sale", methods=["POST"])
@role_required(["Admin", "SalesSupervisor", "SalesClerk"])
def create_sale():
    try:
        product_id = int(request.form["product_id"])
        quantity = int(request.form["quantity"])
        payment_method = request.form["payment_method"]

        with db_cursor() as cursor:
            # Lock row and check stock
            cursor.execute("""
                SELECT StockQty, UnitPrice
                FROM Product
                WHERE ProductID = :pid
                FOR UPDATE
            """, {"pid": product_id})

            product = cursor.fetchone()

            if not product:
                return "Product not found", 404

            stock_qty, unit_price = product

            if quantity > stock_qty:
                return f"Insufficient stock: {stock_qty}", 400

            # Insert Sale
            sale_id_var = cursor.var(oracledb.NUMBER)
            cursor.execute("""
                INSERT INTO Sale (SaleID, UserID, TotalAmount, PaymentMethod)
                VALUES (sale_seq.NEXTVAL, :uid, 0, :pm)
                RETURNING SaleID INTO :sid
            """, {
                "uid": session["user_id"],
                "pm": payment_method,
                "sid": sale_id_var
            })

            sale_id = sale_id_var.getvalue()[0]

            # Insert Line Item
            cursor.execute("""
                INSERT INTO SaleLineItem
                (LineItemID, SaleID, ProductID, Quantity, UnitPrice)
                VALUES
                (sale_lineitem_seq.NEXTVAL, :sid, :pid, :qty, :price)
            """, {
                "sid": sale_id,
                "pid": product_id,
                "qty": quantity,
                "price": unit_price
            })

            # Update Stock
            cursor.execute("""
                UPDATE Product
                SET StockQty = StockQty - :qty
                WHERE ProductID = :pid
            """, {
                "qty": quantity,
                "pid": product_id
            })

        return redirect("/sales")

    except Exception as e:
        app.logger.error(str(e))
        return f"Sale failed: {str(e)}", 500



# PURCHASES PAGE


@app.route("/purchases")
@role_required(["Admin", "Manager", "InventoryManager"])
def purchases():
    try:
        with db_cursor() as cursor:
            cursor.execute("""
                SELECT p.PurchaseID,
                       TO_CHAR(p.PurchaseDate, 'DD Mon YYYY') AS PurchaseDate,
                       s.SupplierName,
                       u.FullName,
                       p.TotalAmount,
                       p.OrderStatus
                FROM Purchase p
                JOIN Supplier s ON p.SupplierID = s.SupplierID
                JOIN User_Account u ON p.UserID = u.UserID
                ORDER BY p.PurchaseDate DESC
            """)
            
            purchases_list = [
                {
                    "purchase_id": r[0],
                    "purchase_date": r[1],
                    "supplier_name": r[2],
                    "fullname": r[3],
                    "total_amount": float(r[4]),
                    "order_status": r[5]
                }
                for r in cursor.fetchall()
            ]
            
        return render_template(
            "purchases.html",
            purchases=purchases_list,
            fullname=session["fullname"],
            role=session["role"],
            current_date=today()
        )
                             
    except Exception as e:
        return f"Purchases error: {str(e)}", 500



# CREATE PURCHASE


@app.route("/create-purchase", methods=["POST"])
@role_required(["Admin", "InventoryManager"])
def create_purchase():
    try:
        supplier_id = int(request.form["supplier_id"])
        product_id = int(request.form["product_id"])
        quantity = int(request.form["quantity"])
        cost_price = float(request.form["cost_price"])
        
        with db_cursor() as cursor:
            cursor.execute("""
                INSERT INTO Purchase (PurchaseID, SupplierID, UserID, TotalAmount, OrderStatus)
                VALUES (purchase_seq.NEXTVAL, :sup, :uid, 0, 'Pending')
            """, {
                "sup": supplier_id,
                "uid": session["user_id"]
            })
            
            cursor.execute("""
                INSERT INTO PurchaseLineItem (PLineItemID, PurchaseID, ProductID, Quantity, CostPrice)
                VALUES (purchase_lineitem_seq.NEXTVAL, purchase_seq.CURRVAL, :prod, :qty, :cost)
            """, {
                "prod": product_id,
                "qty": quantity,
                "cost": cost_price
            })
            
        return redirect("/purchases")
        
    except Exception as e:
        return f"Error creating purchase: {str(e)}", 500



# RECEIVE PURCHASE


@app.route("/receive-purchase/<int:purchase_id>", methods=["POST"])
@role_required(["Admin", "InventoryManager"])
def receive_purchase(purchase_id):
    try:
        with db_cursor() as cursor:
            cursor.execute("SELECT OrderStatus FROM Purchase WHERE PurchaseID = :pid", 
                          {"pid": purchase_id})
            result = cursor.fetchone()
            
            if not result:
                return "Purchase order not found", 404
            
            if result[0] != "Pending":
                return "Only pending orders can be received", 400
            
            cursor.execute("""
                UPDATE Purchase 
                SET OrderStatus = 'Received'
                WHERE PurchaseID = :pid
            """, {"pid": purchase_id})
            
        return redirect("/purchases")
        
    except Exception as e:
        return f"Error receiving purchase: {str(e)}", 500


# STOCK TRANSACTIONS


@app.route("/stock-transactions")
@role_required(["Admin", "Manager", "InventoryManager"])
def stock_transactions():
    try:
        with db_cursor() as cursor:
            cursor.execute("""
                SELECT st.TransactionID,
                       p.ProductName,
                       st.TransactionType,
                       st.Quantity,
                       TO_CHAR(st.TransactionDate, 'DD Mon YYYY HH24:MI') AS TransDate,
                       u.FullName,
                       st.Notes
                FROM StockTransaction st
                JOIN Product p ON st.ProductID = p.ProductID
                JOIN User_Account u ON st.UserID = u.UserID
                ORDER BY st.TransactionDate DESC
                FETCH FIRST 200 ROWS ONLY
            """)
            
            transactions = [
                {
                    "transaction_id": r[0],
                    "product_name": r[1],
                    "transaction_type": r[2],
                    "quantity": r[3],
                    "transaction_date": r[4],
                    "fullname": r[5],
                    "notes": r[6] or ""
                }
                for r in cursor.fetchall()
            ]
            
        return render_template(
            "stock_transactions.html",
            transactions=transactions,
            fullname=session["fullname"],
            role=session["role"],
            current_date=today()
        )
                             
    except Exception as e:
        return f"Stock transactions error: {str(e)}", 500



# LOW STOCK ALERTS


@app.route("/low-stock")
@role_required(["Admin", "Manager", "InventoryManager"])
def low_stock():
    try:
        with db_cursor() as cursor:
            cursor.execute("SELECT * FROM LowStockAlert ORDER BY StockQty ASC")
            
            columns = [col[0].lower() for col in cursor.description]
            
            low_stock_items = []
            for row in cursor.fetchall():
                item = {}
                for i, col in enumerate(columns):
                    item[col] = row[i]
                low_stock_items.append(item)
            
        return render_template(
            "low_stock.html",
            low_stock=low_stock_items,
            fullname=session["fullname"],
            role=session["role"],
            current_date=today()
        )
                             
    except Exception as e:
        return f"Low stock error: {str(e)}", 500



# REPORTS


@app.route("/reports")
@role_required(["Admin", "Manager"])
def reports():
    try:
        with db_cursor() as cursor:
            cursor.execute("SELECT * FROM DailySalesSummary FETCH FIRST 30 ROWS ONLY")
            daily_sales = [dict(zip([col[0].lower() for col in cursor.description], r)) for r in cursor.fetchall()]

            cursor.execute("SELECT * FROM ProductPerformance FETCH FIRST 20 ROWS ONLY")
            product_performance = [dict(zip([col[0].lower() for col in cursor.description], r)) for r in cursor.fetchall()]

        return render_template(
            "reports.html",
            daily_sales=daily_sales,
            product_performance=product_performance,
            fullname=session["fullname"],
            role=session["role"],
            current_date=today()
        )

    except Exception as e:
        return f"Reports error: {str(e)}", 500



# API ROUTES


@app.route("/api/low-stock")
@role_required(["Admin", "Manager", "InventoryManager"])
def low_stock_api():
    try:
        with db_cursor() as cursor:
            cursor.execute("""
                SELECT ProductName, StockQty, ReorderLevel, AlertLevel
                FROM LowStockAlert
                FETCH FIRST 10 ROWS ONLY
            """)

            results = [
                {
                    "product_name": r[0],
                    "stock_qty": r[1],
                    "reorder_level": r[2],
                    "alert_level": r[3]
                }
                for r in cursor.fetchall()
            ]

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sales-chart")
@role_required(["Admin", "Manager", "SalesSupervisor"])
def sales_chart_api():
    try:
        with db_cursor() as cursor:
            cursor.execute("""
                SELECT TO_CHAR(SaleDate, 'DD Mon') AS Day,
                       SUM(TotalAmount) AS TotalSales
                FROM Sale
                WHERE SaleDate >= TRUNC(SYSTIMESTAMP) - 7
                GROUP BY TO_CHAR(SaleDate, 'DD Mon'), TRUNC(SaleDate)
                ORDER BY TRUNC(SaleDate)
            """)
            
            labels = []
            sales = []
            
            for r in cursor.fetchall():
                labels.append(r[0])
                sales.append(float(r[1]) if r[1] else 0)
            
        return jsonify({"labels": labels, "sales": sales})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ERROR HANDLERS


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500



# RUN APP


if __name__ == "__main__":
    print("=" * 50)
    print("IMSTS Flask Application Starting...")
    print("=" * 50)

    try:
        with db_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM User_Account")
            user_count = cursor.fetchone()[0]
            print(f" Database connection successful")
            print(f" Found {user_count} user accounts")

    except Exception as e:
        print(f" DB ERROR: {e}")

    print("\n" + "=" * 50)
    print("Server running at: http://127.0.0.1:5000")
    print("=" * 50 + "\n")

    app.run(host="127.0.0.1", port=5000, debug=False)
