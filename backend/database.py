import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from config import DB_NAME, TIMEZONE_OFFSET

def get_connection():
    """Create and return database connection"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with all required tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            phone TEXT UNIQUE,
            language TEXT DEFAULT 'uz',
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # Categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_uz TEXT NOT NULL,
            name_ru TEXT NOT NULL,
            description_uz TEXT,
            description_ru TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            name_uz TEXT NOT NULL,
            name_ru TEXT NOT NULL,
            description_uz TEXT,
            description_ru TEXT,
            price REAL NOT NULL,
            discount_price REAL,
            stock_quantity INTEGER DEFAULT 0,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (category_id) REFERENCES categories(category_id)
        )
    ''')
    
    # Cart items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart_items (
            cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    ''')
    
    # Neighborhoods table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS neighborhoods (
            neighborhood_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_uz TEXT NOT NULL,
            name_ru TEXT NOT NULL,
            delivery_price REAL DEFAULT 0,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            neighborhood_id INTEGER,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            total_amount REAL NOT NULL,
            delivery_price REAL DEFAULT 0,
            payment_method TEXT DEFAULT 'cash',
            status TEXT DEFAULT 'pending',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (neighborhood_id) REFERENCES neighborhoods(neighborhood_id)
        )
    ''')
    
    # Order items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    ''')
    
    # Admins table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            admin_id INTEGER PRIMARY KEY,
            username TEXT,
            role TEXT DEFAULT 'admin',
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # Verification codes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verification_codes (
            code_id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            code TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            is_used INTEGER DEFAULT 0
        )
    ''')
    
    # Chat messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            admin_id INTEGER,
            message_text TEXT NOT NULL,
            sender_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Userbot settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS userbot_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_id INTEGER,
            api_hash TEXT,
            phone TEXT,
            session_string TEXT,
            is_active INTEGER DEFAULT 0
        )
    ''')
    
    # Favorites table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            favorite_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            UNIQUE(user_id, product_id)
        )
    ''')
    
    # Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Insert super admin
    cursor.execute('''
        INSERT OR IGNORE INTO admins (admin_id, role, is_active) 
        VALUES (?, 'super_admin', 1)
    ''', (5895427105,))
    
    conn.commit()
    conn.close()

# User functions
def create_user(user_id: int, username: str = None, first_name: str = None, 
                last_name: str = None, phone: str = None, language: str = 'uz') -> bool:
    """Create new user"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (user_id, username, first_name, last_name, phone, language)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, phone, language))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_user(user_id: int, **kwargs) -> bool:
    """Update user information"""
    conn = get_connection()
    cursor = conn.cursor()
    fields = ', '.join([f'{k} = ?' for k in kwargs.keys()])
    values = list(kwargs.values()) + [user_id]
    cursor.execute(f'UPDATE users SET {fields} WHERE user_id = ?', values)
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def get_user_by_phone(phone: str) -> Optional[Dict]:
    """Get user by phone number"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE phone = ?', (phone,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_users() -> List[Dict]:
    """Get all users"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY registered_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Category functions
def create_category(name_uz: str, name_ru: str, description_uz: str = None, 
                   description_ru: str = None) -> int:
    """Create new category"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO categories (name_uz, name_ru, description_uz, description_ru)
        VALUES (?, ?, ?, ?)
    ''', (name_uz, name_ru, description_uz, description_ru))
    conn.commit()
    category_id = cursor.lastrowid
    conn.close()
    return category_id

def get_category(category_id: int) -> Optional[Dict]:
    """Get category by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM categories WHERE category_id = ? AND is_active = 1', (category_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_categories(active_only: bool = True) -> List[Dict]:
    """Get all categories"""
    conn = get_connection()
    cursor = conn.cursor()
    if active_only:
        cursor.execute('SELECT * FROM categories WHERE is_active = 1 ORDER BY name_uz')
    else:
        cursor.execute('SELECT * FROM categories ORDER BY name_uz')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_category(category_id: int, **kwargs) -> bool:
    """Update category"""
    conn = get_connection()
    cursor = conn.cursor()
    fields = ', '.join([f'{k} = ?' for k in kwargs.keys()])
    values = list(kwargs.values()) + [category_id]
    cursor.execute(f'UPDATE categories SET {fields} WHERE category_id = ?', values)
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def delete_category(category_id: int) -> bool:
    """Soft delete category"""
    return update_category(category_id, is_active=0)

# Product functions
def create_product(category_id: int, name_uz: str, name_ru: str, price: float,
                  description_uz: str = None, description_ru: str = None,
                  discount_price: float = None, stock_quantity: int = 0,
                  image_path: str = None) -> int:
    """Create new product"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (category_id, name_uz, name_ru, description_uz, description_ru,
                            price, discount_price, stock_quantity, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (category_id, name_uz, name_ru, description_uz, description_ru, 
          price, discount_price, stock_quantity, image_path))
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    return product_id

def get_product(product_id: int) -> Optional[Dict]:
    """Get product by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE product_id = ? AND is_active = 1', (product_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_products_by_category(category_id: int) -> List[Dict]:
    """Get all products in a category"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM products 
        WHERE category_id = ? AND is_active = 1 
        ORDER BY created_at DESC
    ''', (category_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_all_products(active_only: bool = True) -> List[Dict]:
    """Get all products"""
    conn = get_connection()
    cursor = conn.cursor()
    if active_only:
        cursor.execute('SELECT * FROM products WHERE is_active = 1 ORDER BY created_at DESC')
    else:
        cursor.execute('SELECT * FROM products ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_product(product_id: int, **kwargs) -> bool:
    """Update product"""
    conn = get_connection()
    cursor = conn.cursor()
    fields = ', '.join([f'{k} = ?' for k in kwargs.keys()])
    values = list(kwargs.values()) + [product_id]
    cursor.execute(f'UPDATE products SET {fields} WHERE product_id = ?', values)
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def delete_product(product_id: int) -> bool:
    """Soft delete product"""
    return update_product(product_id, is_active=0)

def search_products(query: str, language: str = 'uz') -> List[Dict]:
    """Search products by name"""
    conn = get_connection()
    cursor = conn.cursor()
    name_field = f'name_{language}'
    cursor.execute(f'''
        SELECT * FROM products 
        WHERE {name_field} LIKE ? AND is_active = 1
        ORDER BY created_at DESC
    ''', (f'%{query}%',))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Cart functions
def add_to_cart(user_id: int, product_id: int, quantity: int = 1) -> bool:
    """Add item to cart or update quantity"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT cart_id, quantity FROM cart_items 
        WHERE user_id = ? AND product_id = ?
    ''', (user_id, product_id))
    existing = cursor.fetchone()
    
    if existing:
        new_quantity = existing['quantity'] + quantity
        cursor.execute('''
            UPDATE cart_items SET quantity = ? 
            WHERE cart_id = ?
        ''', (new_quantity, existing['cart_id']))
    else:
        cursor.execute('''
            INSERT INTO cart_items (user_id, product_id, quantity)
            VALUES (?, ?, ?)
        ''', (user_id, product_id, quantity))
    
    conn.commit()
    conn.close()
    return True

def get_cart_items(user_id: int) -> List[Dict]:
    """Get all cart items for user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, p.* FROM cart_items c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = ? AND p.is_active = 1
        ORDER BY c.added_at DESC
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_cart_quantity(cart_id: int, quantity: int) -> bool:
    """Update cart item quantity"""
    conn = get_connection()
    cursor = conn.cursor()
    if quantity <= 0:
        cursor.execute('DELETE FROM cart_items WHERE cart_id = ?', (cart_id,))
    else:
        cursor.execute('UPDATE cart_items SET quantity = ? WHERE cart_id = ?', (quantity, cart_id))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def remove_from_cart(cart_id: int) -> bool:
    """Remove item from cart"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cart_items WHERE cart_id = ?', (cart_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def clear_cart(user_id: int) -> bool:
    """Clear all items from user's cart"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cart_items WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
    return True

# Neighborhood functions
def create_neighborhood(name_uz: str, name_ru: str, delivery_price: float = 0) -> int:
    """Create new neighborhood"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO neighborhoods (name_uz, name_ru, delivery_price)
        VALUES (?, ?, ?)
    ''', (name_uz, name_ru, delivery_price))
    conn.commit()
    neighborhood_id = cursor.lastrowid
    conn.close()
    return neighborhood_id

def get_neighborhood(neighborhood_id: int) -> Optional[Dict]:
    """Get neighborhood by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM neighborhoods WHERE neighborhood_id = ?', (neighborhood_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_neighborhoods(active_only: bool = True) -> List[Dict]:
    """Get all neighborhoods"""
    conn = get_connection()
    cursor = conn.cursor()
    if active_only:
        cursor.execute('SELECT * FROM neighborhoods WHERE is_active = 1 ORDER BY name_uz')
    else:
        cursor.execute('SELECT * FROM neighborhoods ORDER BY name_uz')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_neighborhood(neighborhood_id: int, **kwargs) -> bool:
    """Update neighborhood"""
    conn = get_connection()
    cursor = conn.cursor()
    fields = ', '.join([f'{k} = ?' for k in kwargs.keys()])
    values = list(kwargs.values()) + [neighborhood_id]
    cursor.execute(f'UPDATE neighborhoods SET {fields} WHERE neighborhood_id = ?', values)
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

# Order functions
def create_order(user_id: int, full_name: str, phone: str, address: str,
                total_amount: float, neighborhood_id: int = None, 
                delivery_price: float = 0, payment_method: str = 'cash',
                notes: str = None) -> int:
    """Create new order"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (user_id, neighborhood_id, full_name, phone, address,
                          total_amount, delivery_price, payment_method, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, neighborhood_id, full_name, phone, address, 
          total_amount, delivery_price, payment_method, notes))
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    return order_id

def add_order_item(order_id: int, product_id: int, quantity: int, price: float) -> bool:
    """Add item to order"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO order_items (order_id, product_id, quantity, price)
        VALUES (?, ?, ?, ?)
    ''', (order_id, product_id, quantity, price))
    conn.commit()
    conn.close()
    return True

def get_order(order_id: int) -> Optional[Dict]:
    """Get order by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_order_items(order_id: int) -> List[Dict]:
    """Get all items in an order"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT oi.*, p.name_uz, p.name_ru, p.image_path 
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        WHERE oi.order_id = ?
    ''', (order_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_user_orders(user_id: int) -> List[Dict]:
    """Get all orders for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM orders 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_all_orders(status: str = None) -> List[Dict]:
    """Get all orders, optionally filtered by status"""
    conn = get_connection()
    cursor = conn.cursor()
    if status:
        cursor.execute('SELECT * FROM orders WHERE status = ? ORDER BY created_at DESC', (status,))
    else:
        cursor.execute('SELECT * FROM orders ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_order_status(order_id: int, status: str) -> bool:
    """Update order status"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE orders 
        SET status = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE order_id = ?
    ''', (status, order_id))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

# Admin functions
def create_admin(admin_id: int, username: str = None, role: str = 'admin') -> bool:
    """Create new admin"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO admins (admin_id, username, role)
            VALUES (?, ?, ?)
        ''', (admin_id, username, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_admin(admin_id: int) -> Optional[Dict]:
    """Get admin by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM admins WHERE admin_id = ? AND is_active = 1', (admin_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_admins() -> List[Dict]:
    """Get all admins"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM admins WHERE is_active = 1 ORDER BY added_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    admin = get_admin(user_id)
    return admin is not None

def is_super_admin(user_id: int) -> bool:
    """Check if user is super admin"""
    admin = get_admin(user_id)
    return admin and admin['role'] == 'super_admin'

def remove_admin(admin_id: int) -> bool:
    """Remove admin (soft delete)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE admins SET is_active = 0 WHERE admin_id = ?', (admin_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

# Verification code functions
def create_verification_code(phone: str, code: str, expire_minutes: int = 5) -> int:
    """Create verification code"""
    conn = get_connection()
    cursor = conn.cursor()
    expires_at = datetime.now() + timedelta(minutes=expire_minutes)
    cursor.execute('''
        INSERT INTO verification_codes (phone, code, expires_at)
        VALUES (?, ?, ?)
    ''', (phone, code, expires_at))
    conn.commit()
    code_id = cursor.lastrowid
    conn.close()
    return code_id

def verify_code(phone: str, code: str) -> bool:
    """Verify code for phone number"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT code_id FROM verification_codes
        WHERE phone = ? AND code = ? AND is_used = 0 
        AND expires_at > CURRENT_TIMESTAMP
        ORDER BY created_at DESC LIMIT 1
    ''', (phone, code))
    row = cursor.fetchone()
    
    if row:
        cursor.execute('UPDATE verification_codes SET is_used = 1 WHERE code_id = ?', 
                      (row['code_id'],))
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

# Chat functions
def create_message(user_id: int, message_text: str, sender_type: str, 
                  admin_id: int = None) -> int:
    """Create chat message"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_messages (user_id, admin_id, message_text, sender_type)
        VALUES (?, ?, ?, ?)
    ''', (user_id, admin_id, message_text, sender_type))
    conn.commit()
    message_id = cursor.lastrowid
    conn.close()
    return message_id

def get_user_messages(user_id: int) -> List[Dict]:
    """Get all messages for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM chat_messages 
        WHERE user_id = ? 
        ORDER BY created_at ASC
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def mark_messages_read(user_id: int, admin_id: int = None) -> bool:
    """Mark messages as read"""
    conn = get_connection()
    cursor = conn.cursor()
    if admin_id:
        cursor.execute('''
            UPDATE chat_messages 
            SET is_read = 1 
            WHERE user_id = ? AND admin_id = ?
        ''', (user_id, admin_id))
    else:
        cursor.execute('''
            UPDATE chat_messages 
            SET is_read = 1 
            WHERE user_id = ?
        ''', (user_id,))
    conn.commit()
    conn.close()
    return True

# Favorites functions
def add_to_favorites(user_id: int, product_id: int) -> bool:
    """Add product to favorites"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO favorites (user_id, product_id)
            VALUES (?, ?)
        ''', (user_id, product_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def remove_from_favorites(user_id: int, product_id: int) -> bool:
    """Remove product from favorites"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM favorites 
        WHERE user_id = ? AND product_id = ?
    ''', (user_id, product_id))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def get_user_favorites(user_id: int) -> List[Dict]:
    """Get user's favorite products"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.* FROM favorites f
        JOIN products p ON f.product_id = p.product_id
        WHERE f.user_id = ? AND p.is_active = 1
        ORDER BY f.added_at DESC
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def is_favorite(user_id: int, product_id: int) -> bool:
    """Check if product is in favorites"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 1 FROM favorites 
        WHERE user_id = ? AND product_id = ?
    ''', (user_id, product_id))
    result = cursor.fetchone() is not None
    conn.close()
    return result

# Session functions
def create_session(session_id: str, user_id: int, expire_hours: int = 720) -> bool:
    """Create session"""
    conn = get_connection()
    cursor = conn.cursor()
    expires_at = datetime.now() + timedelta(hours=expire_hours)
    cursor.execute('''
        INSERT INTO sessions (session_id, user_id, expires_at)
        VALUES (?, ?, ?)
    ''', (session_id, user_id, expires_at))
    conn.commit()
    conn.close()
    return True

def get_session(session_id: str) -> Optional[Dict]:
    """Get session by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM sessions 
        WHERE session_id = ? AND expires_at > CURRENT_TIMESTAMP
    ''', (session_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_session(session_id: str) -> bool:
    """Delete session"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

# Userbot settings functions
def save_userbot_settings(api_id: int, api_hash: str, phone: str, 
                         session_string: str = None) -> bool:
    """Save or update userbot settings"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM userbot_settings')
    cursor.execute('''
        INSERT INTO userbot_settings (api_id, api_hash, phone, session_string, is_active)
        VALUES (?, ?, ?, ?, 1)
    ''', (api_id, api_hash, phone, session_string))
    conn.commit()
    conn.close()
    return True

def get_userbot_settings() -> Optional[Dict]:
    """Get userbot settings"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM userbot_settings WHERE is_active = 1 LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# Statistics functions
def get_statistics() -> Dict:
    """Get general statistics"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as total FROM users')
    total_users = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM products WHERE is_active = 1')
    total_products = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM orders')
    total_orders = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM orders WHERE status = "pending"')
    pending_orders = cursor.fetchone()['total']
    
    cursor.execute('SELECT COALESCE(SUM(total_amount), 0) as total FROM orders WHERE status = "completed"')
    total_revenue = cursor.fetchone()['total']
    
    conn.close()
    
    return {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue
    }
