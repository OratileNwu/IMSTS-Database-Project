CREATE TABLE Category (
    CategoryID      NUMBER(10) PRIMARY KEY,
    CategoryName    VARCHAR2(100) UNIQUE NOT NULL,
    Description     VARCHAR2(255),
    ParentCatID     NUMBER(10),
    CONSTRAINT fk_category_parent 
        FOREIGN KEY (ParentCatID) REFERENCES Category(CategoryID)
);

CREATE TABLE Supplier (
    SupplierID        NUMBER(10) PRIMARY KEY,
    SupplierName      VARCHAR2(100) NOT NULL,
    SupplierPhone     VARCHAR2(20) NOT NULL,
    SupplierEmail     VARCHAR2(100) UNIQUE NOT NULL,
    SupplierAddress   VARCHAR2(255) NOT NULL,
    PerformanceRating NUMBER(3,1),
    CONSTRAINT chk_supplier_rating 
        CHECK (PerformanceRating BETWEEN 0 AND 5)
);

CREATE TABLE User_Account (
    UserID        NUMBER(10) PRIMARY KEY,
    FullName      VARCHAR2(150) NOT NULL,
    UserName      VARCHAR2(50) UNIQUE NOT NULL,
    Email         VARCHAR2(100) UNIQUE NOT NULL,
    PasswordHash  VARCHAR2(255) NOT NULL,
    Role          VARCHAR2(50) NOT NULL,
    DateCreated   TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    LastLogin     TIMESTAMP,
    IsActive      NUMBER(1) DEFAULT 1 NOT NULL,
    CONSTRAINT chk_user_role 
        CHECK (Role IN ('Admin', 'Manager', 'InventoryManager', 'SalesSupervisor', 'SalesClerk')),
    CONSTRAINT chk_user_active 
        CHECK (IsActive IN (0, 1))
);

CREATE TABLE Product (
    ProductID       NUMBER(10) PRIMARY KEY,
    ProductName     VARCHAR2(100) NOT NULL,
    Description     VARCHAR2(255),
    SKU             VARCHAR2(50) UNIQUE NOT NULL,
    CategoryID      NUMBER(10) NOT NULL,
    SupplierID      NUMBER(10) NOT NULL,
    UnitPrice       NUMBER(10,2) NOT NULL,
    CostPrice       NUMBER(10,2) NOT NULL,
    StockQty        NUMBER(10) DEFAULT 0 NOT NULL,
    ReorderLevel    NUMBER(10) NOT NULL,
    MaxStockLevel   NUMBER(10) NOT NULL,
    CONSTRAINT fk_product_category 
        FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID),
    CONSTRAINT fk_product_supplier 
        FOREIGN KEY (SupplierID) REFERENCES Supplier(SupplierID),
    CONSTRAINT chk_product_unitprice 
        CHECK (UnitPrice > 0),
    CONSTRAINT chk_product_costprice 
        CHECK (CostPrice > 0),
    CONSTRAINT chk_product_stockqty 
        CHECK (StockQty >= 0),
    CONSTRAINT chk_product_reorder 
        CHECK (ReorderLevel >= 0),
    CONSTRAINT chk_product_maxstock 
        CHECK (MaxStockLevel > 0)
);

CREATE TABLE Sale (
    SaleID        NUMBER(10) PRIMARY KEY,
    SaleDate      TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UserID        NUMBER(10) NOT NULL,
    TotalAmount   NUMBER(10,2) NOT NULL,
    PaymentMethod VARCHAR2(20) NOT NULL,
    CONSTRAINT fk_sale_user 
        FOREIGN KEY (UserID) REFERENCES User_Account(UserID),
    CONSTRAINT chk_sale_total 
        CHECK (TotalAmount >= 0),
    CONSTRAINT chk_sale_payment 
        CHECK (PaymentMethod IN ('Cash', 'Card', 'EFT'))
);

CREATE TABLE SaleLineItem (
    LineItemID  NUMBER(10) PRIMARY KEY,
    SaleID      NUMBER(10) NOT NULL,
    ProductID   NUMBER(10) NOT NULL,
    Quantity    NUMBER(10) NOT NULL,
    UnitPrice   NUMBER(10,2) NOT NULL,
    LineTotal   NUMBER(10,2) GENERATED ALWAYS AS (Quantity * UnitPrice) VIRTUAL,
    CONSTRAINT fk_saleline_sale 
        FOREIGN KEY (SaleID) REFERENCES Sale(SaleID) ON DELETE CASCADE,
    CONSTRAINT fk_saleline_product 
        FOREIGN KEY (ProductID) REFERENCES Product(ProductID),
    CONSTRAINT chk_saleline_quantity 
        CHECK (Quantity > 0),
    CONSTRAINT chk_saleline_unitprice 
        CHECK (UnitPrice > 0),
    CONSTRAINT uk_sale_product 
        UNIQUE (SaleID, ProductID)
);

CREATE TABLE Purchase (
    PurchaseID    NUMBER(10) PRIMARY KEY,
    PurchaseDate  TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    SupplierID    NUMBER(10) NOT NULL,
    UserID        NUMBER(10) NOT NULL,
    TotalAmount   NUMBER(10,2) NOT NULL,
    OrderStatus   VARCHAR2(20) DEFAULT 'Pending' NOT NULL,
    CONSTRAINT fk_purchase_supplier 
        FOREIGN KEY (SupplierID) REFERENCES Supplier(SupplierID),
    CONSTRAINT fk_purchase_user 
        FOREIGN KEY (UserID) REFERENCES User_Account(UserID),
    CONSTRAINT chk_purchase_total 
        CHECK (TotalAmount >= 0),
    CONSTRAINT chk_purchase_status 
        CHECK (OrderStatus IN ('Pending', 'Received', 'Cancelled'))
);

CREATE TABLE PurchaseLineItem (
    PLineItemID NUMBER(10) PRIMARY KEY,
    PurchaseID  NUMBER(10) NOT NULL,
    ProductID   NUMBER(10) NOT NULL,
    Quantity    NUMBER(10) NOT NULL,
    CostPrice   NUMBER(10,2) NOT NULL,
    LineTotal   NUMBER(10,2) GENERATED ALWAYS AS (Quantity * CostPrice) VIRTUAL,
    CONSTRAINT fk_purchaseline_purchase 
        FOREIGN KEY (PurchaseID) REFERENCES Purchase(PurchaseID) ON DELETE CASCADE,
    CONSTRAINT fk_purchaseline_product 
        FOREIGN KEY (ProductID) REFERENCES Product(ProductID),
    CONSTRAINT chk_purchaseline_quantity 
        CHECK (Quantity > 0),
    CONSTRAINT chk_purchaseline_costprice 
        CHECK (CostPrice > 0),
    CONSTRAINT uk_purchase_product 
        UNIQUE (PurchaseID, ProductID)
);

CREATE TABLE StockTransaction (
    TransactionID     NUMBER(10) PRIMARY KEY,
    ProductID         NUMBER(10) NOT NULL,
    UserID            NUMBER(10) NOT NULL,
    TransactionType   VARCHAR2(20) NOT NULL,
    Quantity          NUMBER(10) NOT NULL,
    TransactionDate   TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ReferenceID       NUMBER(10),
    Notes             VARCHAR2(255),
    CONSTRAINT fk_stock_product 
        FOREIGN KEY (ProductID) REFERENCES Product(ProductID),
    CONSTRAINT fk_stock_user 
        FOREIGN KEY (UserID) REFERENCES User_Account(UserID),
    CONSTRAINT chk_stock_type 
        CHECK (TransactionType IN ('Stock_In', 'Stock_Out', 'Adjustment')),
    CONSTRAINT chk_stock_quantity 
        CHECK (Quantity != 0)
);

CREATE TABLE AuditLog (
    LogID         NUMBER(10),
    UserID        NUMBER(10) NOT NULL,
    ActionType    VARCHAR2(20) NOT NULL,
    TableAffected VARCHAR2(100) NOT NULL,
    RecordID      NUMBER(10) NOT NULL,
    ActionDate    TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    OldValue      CLOB,
    NewValue      CLOB,
    CONSTRAINT pk_auditlog PRIMARY KEY (LogID, UserID),
    CONSTRAINT fk_auditlog_user 
        FOREIGN KEY (UserID) REFERENCES User_Account(UserID) ON DELETE CASCADE,
    CONSTRAINT chk_audit_action 
        CHECK (ActionType IN ('INSERT', 'UPDATE', 'DELETE'))
);

CREATE SEQUENCE category_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE supplier_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE product_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE user_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE sale_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE sale_lineitem_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE purchase_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE purchase_lineitem_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE stocktransaction_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE auditlog_seq START WITH 1 INCREMENT BY 1;

CREATE OR REPLACE TRIGGER category_trigger
BEFORE INSERT ON Category
FOR EACH ROW
BEGIN
    IF :NEW.CategoryID IS NULL THEN
        SELECT category_seq.NEXTVAL INTO :NEW.CategoryID FROM DUAL;
    END IF;
END;
/

CREATE OR REPLACE TRIGGER supplier_trigger
BEFORE INSERT ON Supplier
FOR EACH ROW
BEGIN
    IF :NEW.SupplierID IS NULL THEN
        SELECT supplier_seq.NEXTVAL INTO :NEW.SupplierID FROM DUAL;
    END IF;
END;
/

CREATE OR REPLACE TRIGGER product_trigger
BEFORE INSERT ON Product
FOR EACH ROW
BEGIN
    IF :NEW.ProductID IS NULL THEN
        SELECT product_seq.NEXTVAL INTO :NEW.ProductID FROM DUAL;
    END IF;
END;
/

CREATE OR REPLACE TRIGGER user_trigger
BEFORE INSERT ON User_Account
FOR EACH ROW
BEGIN
    IF :NEW.UserID IS NULL THEN
        SELECT user_seq.NEXTVAL INTO :NEW.UserID FROM DUAL;
    END IF;
END;
/

CREATE OR REPLACE TRIGGER sale_trigger
BEFORE INSERT ON Sale
FOR EACH ROW
BEGIN
    IF :NEW.SaleID IS NULL THEN
        SELECT sale_seq.NEXTVAL INTO :NEW.SaleID FROM DUAL;
    END IF;
END;
/

CREATE OR REPLACE TRIGGER salelineitem_trigger
BEFORE INSERT ON SaleLineItem
FOR EACH ROW
BEGIN
    IF :NEW.LineItemID IS NULL THEN
        SELECT sale_lineitem_seq.NEXTVAL INTO :NEW.LineItemID FROM DUAL;
    END IF;
END;
/

CREATE OR REPLACE TRIGGER purchase_trigger
BEFORE INSERT ON Purchase
FOR EACH ROW
BEGIN
    IF :NEW.PurchaseID IS NULL THEN
        SELECT purchase_seq.NEXTVAL INTO :NEW.PurchaseID FROM DUAL;
    END IF;
END;
/

CREATE OR REPLACE TRIGGER purchaselineitem_trigger
BEFORE INSERT ON PurchaseLineItem
FOR EACH ROW
BEGIN
    IF :NEW.PLineItemID IS NULL THEN
        SELECT purchase_lineitem_seq.NEXTVAL INTO :NEW.PLineItemID FROM DUAL;
    END IF;
END;
/

CREATE OR REPLACE TRIGGER stocktransaction_trigger
BEFORE INSERT ON StockTransaction
FOR EACH ROW
BEGIN
    IF :NEW.TransactionID IS NULL THEN
        SELECT stocktransaction_seq.NEXTVAL INTO :NEW.TransactionID FROM DUAL;
    END IF;
END;
/

CREATE OR REPLACE TRIGGER auditlog_trigger
BEFORE INSERT ON AuditLog
FOR EACH ROW
BEGIN
    IF :NEW.LogID IS NULL THEN
        SELECT auditlog_seq.NEXTVAL INTO :NEW.LogID FROM DUAL;
    END IF;
END;
/

CREATE OR REPLACE TRIGGER sale_stock_update
AFTER INSERT ON SaleLineItem
FOR EACH ROW
DECLARE
    v_current_stock NUMBER;
BEGIN
    UPDATE Product
    SET StockQty = StockQty - :NEW.Quantity
    WHERE ProductID = :NEW.ProductID
    RETURNING StockQty INTO v_current_stock;
    
    IF v_current_stock < 0 THEN
        RAISE_APPLICATION_ERROR(-20002, 'Insufficient stock for product ID: ' || :NEW.ProductID);
    END IF;
    
    INSERT INTO StockTransaction (
        TransactionID, ProductID, UserID, TransactionType, 
        Quantity, ReferenceID, Notes
    ) VALUES (
        stocktransaction_seq.NEXTVAL, 
        :NEW.ProductID, 
        (SELECT UserID FROM Sale WHERE SaleID = :NEW.SaleID),
        'Stock_Out',
        -:NEW.Quantity,
        :NEW.SaleID,
        'Stock reduced due to sale'
    );
EXCEPTION
    WHEN OTHERS THEN
        RAISE;
END;
/

CREATE OR REPLACE TRIGGER purchase_stock_update
AFTER UPDATE OF OrderStatus ON Purchase
FOR EACH ROW
DECLARE
    CURSOR c_items IS
        SELECT ProductID, Quantity
        FROM PurchaseLineItem
        WHERE PurchaseID = :NEW.PurchaseID;
BEGIN
    IF :OLD.OrderStatus = 'Pending' AND :NEW.OrderStatus = 'Received' THEN
        FOR item IN c_items LOOP
            UPDATE Product
            SET StockQty = StockQty + item.Quantity
            WHERE ProductID = item.ProductID;
            
            INSERT INTO StockTransaction (
                TransactionID, ProductID, UserID, TransactionType,
                Quantity, ReferenceID, Notes
            ) VALUES (
                stocktransaction_seq.NEXTVAL,
                item.ProductID,
                :NEW.UserID,
                'Stock_In',
                item.Quantity,
                :NEW.PurchaseID,
                'Stock added from purchase order'
            );
        END LOOP;
    END IF;
END;
/

CREATE OR REPLACE TRIGGER prevent_negative_stock
BEFORE UPDATE OF StockQty ON Product
FOR EACH ROW
BEGIN
    IF :NEW.StockQty < 0 THEN
        RAISE_APPLICATION_ERROR(-20001, 'Cannot update stock to negative value');
    END IF;
END;
/

CREATE OR REPLACE TRIGGER update_sale_total
AFTER INSERT OR UPDATE OR DELETE ON SaleLineItem
FOR EACH ROW
DECLARE
    v_sale_id Sale.SaleID%TYPE;
    v_new_total NUMBER(10,2);
BEGIN
    IF INSERTING THEN
        v_sale_id := :NEW.SaleID;
    ELSIF DELETING THEN
        v_sale_id := :OLD.SaleID;
    ELSE
        v_sale_id := :NEW.SaleID;
    END IF;
    
    SELECT NVL(SUM(LineTotal), 0)
    INTO v_new_total
    FROM SaleLineItem
    WHERE SaleID = v_sale_id;
    
    UPDATE Sale
    SET TotalAmount = v_new_total
    WHERE SaleID = v_sale_id;
END;
/

CREATE OR REPLACE TRIGGER update_purchase_total
AFTER INSERT OR UPDATE OR DELETE ON PurchaseLineItem
FOR EACH ROW
DECLARE
    v_purchase_id Purchase.PurchaseID%TYPE;
    v_new_total NUMBER(10,2);
BEGIN
    IF INSERTING THEN
        v_purchase_id := :NEW.PurchaseID;
    ELSIF DELETING THEN
        v_purchase_id := :OLD.PurchaseID;
    ELSE
        v_purchase_id := :NEW.PurchaseID;
    END IF;
    
    SELECT NVL(SUM(LineTotal), 0)
    INTO v_new_total
    FROM PurchaseLineItem
    WHERE PurchaseID = v_purchase_id;
    
    UPDATE Purchase
    SET TotalAmount = v_new_total
    WHERE PurchaseID = v_purchase_id;
END;
/

CREATE INDEX idx_product_category ON Product(CategoryID);
CREATE INDEX idx_product_supplier ON Product(SupplierID);
CREATE INDEX idx_sale_user ON Sale(UserID);
CREATE INDEX idx_saleline_sale ON SaleLineItem(SaleID);
CREATE INDEX idx_saleline_product ON SaleLineItem(ProductID);
CREATE INDEX idx_purchase_supplier ON Purchase(SupplierID);
CREATE INDEX idx_purchase_user ON Purchase(UserID);
CREATE INDEX idx_purchaseline_purchase ON PurchaseLineItem(PurchaseID);
CREATE INDEX idx_purchaseline_product ON PurchaseLineItem(ProductID);
CREATE INDEX idx_stock_product ON StockTransaction(ProductID);
CREATE INDEX idx_stock_user ON StockTransaction(UserID);
CREATE INDEX idx_audit_user ON AuditLog(UserID);
CREATE INDEX idx_sale_date ON Sale(SaleDate);
CREATE INDEX idx_purchase_date ON Purchase(PurchaseDate);
CREATE INDEX idx_stock_date ON StockTransaction(TransactionDate);
CREATE INDEX idx_audit_date ON AuditLog(ActionDate);
CREATE INDEX idx_product_name ON Product(ProductName);
CREATE INDEX idx_supplier_name ON Supplier(SupplierName);
CREATE INDEX idx_stock_product_date ON StockTransaction(ProductID, TransactionDate);
CREATE INDEX idx_sale_date_user ON Sale(SaleDate, UserID);

CREATE OR REPLACE VIEW LowStockAlert AS
SELECT 
    p.ProductID,
    p.ProductName,
    p.SKU,
    p.StockQty,
    p.ReorderLevel,
    p.MaxStockLevel,
    s.SupplierName,
    s.SupplierPhone,
    s.SupplierEmail,
    CASE 
        WHEN p.StockQty <= 0 THEN 'CRITICAL - Out of Stock'
        WHEN p.StockQty <= p.ReorderLevel/2 THEN 'HIGH - Very Low Stock'
        ELSE 'MEDIUM - Below Reorder Level'
    END AS AlertLevel
FROM Product p
JOIN Supplier s ON p.SupplierID = s.SupplierID
WHERE p.StockQty <= p.ReorderLevel
ORDER BY p.StockQty ASC;

CREATE OR REPLACE VIEW DailySalesSummary AS
SELECT 
    TRUNC(SaleDate) AS SaleDay,
    COUNT(DISTINCT SaleID) AS NumberOfTransactions,
    SUM(TotalAmount) AS TotalSales,
    AVG(TotalAmount) AS AverageTransactionValue,
    COUNT(DISTINCT UserID) AS ActiveCashiers
FROM Sale
GROUP BY TRUNC(SaleDate)
ORDER BY SaleDay DESC;

CREATE OR REPLACE VIEW ProductPerformance AS
SELECT 
    p.ProductID,
    p.ProductName,
    p.SKU,
    c.CategoryName,
    p.StockQty,
    p.UnitPrice,
    NVL(SUM(sl.Quantity), 0) AS TotalUnitsSold,
    NVL(SUM(sl.LineTotal), 0) AS TotalRevenue,
    p.CostPrice,
    NVL(SUM(sl.Quantity), 0) * p.CostPrice AS TotalCost,
    NVL(SUM(sl.LineTotal), 0) - (NVL(SUM(sl.Quantity), 0) * p.CostPrice) AS GrossProfit
FROM Product p
LEFT JOIN Category c ON p.CategoryID = c.CategoryID
LEFT JOIN SaleLineItem sl ON p.ProductID = sl.ProductID
LEFT JOIN Sale s ON sl.SaleID = s.SaleID
GROUP BY p.ProductID, p.ProductName, p.SKU, c.CategoryName, p.StockQty, p.UnitPrice, p.CostPrice
ORDER BY TotalRevenue DESC;

CREATE OR REPLACE VIEW SupplierPerformance AS
SELECT 
    s.SupplierID,
    s.SupplierName,
    s.SupplierPhone,
    s.SupplierEmail,
    COUNT(DISTINCT p.PurchaseID) AS TotalOrders,
    SUM(p.TotalAmount) AS TotalSpent,
    AVG(p.TotalAmount) AS AverageOrderValue,
    COUNT(DISTINCT pr.ProductID) AS NumberOfProductsSupplied,
    s.PerformanceRating
FROM Supplier s
LEFT JOIN Purchase p ON s.SupplierID = p.SupplierID AND p.OrderStatus = 'Received'
LEFT JOIN Product pr ON s.SupplierID = pr.SupplierID
GROUP BY s.SupplierID, s.SupplierName, s.SupplierPhone, s.SupplierEmail, s.PerformanceRating
ORDER BY TotalSpent DESC;