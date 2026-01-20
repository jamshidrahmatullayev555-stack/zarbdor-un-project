# ZarbdorUn E-Commerce Backend

Complete backend implementation for the ZarbdorUn Telegram e-commerce bot.

## 📁 Project Structure

```
backend/
├── config.py              # Configuration settings
├── database.py            # SQLite database functions
├── requirements.txt       # Python dependencies
├── bot/                   # Telegram bot module
│   ├── __init__.py
│   ├── states.py         # FSM states
│   ├── keyboards.py      # Keyboards (inline & reply)
│   └── utils.py          # Utility functions
├── api/                   # REST API module
│   └── __init__.py
├── userbot/              # Userbot module
│   └── __init__.py
└── services/             # Business logic services
    └── __init__.py
```

## 🗄️ Database Schema

The system uses SQLite with the following tables:

- **users** - User information and profiles
- **categories** - Product categories (bilingual)
- **products** - Product catalog with prices and stock
- **cart_items** - Shopping cart items
- **neighborhoods** - Delivery areas with pricing
- **orders** - Customer orders
- **order_items** - Order line items
- **admins** - Admin users with roles
- **verification_codes** - Phone verification codes
- **chat_messages** - Support chat messages
- **userbot_settings** - Userbot configuration
- **favorites** - User favorite products
- **sessions** - User sessions for API

## 🔧 Configuration

### config.py

Contains all configuration settings:

- `BOT_TOKEN` - Telegram Bot API token
- `SUPER_ADMIN_ID` - Super admin user ID
- `DB_NAME` - Database filename
- `API_HOST` / `API_PORT` - API server settings
- `API_SECRET_KEY` - JWT secret key (auto-generated)
- `JWT_EXPIRE_HOURS` - JWT token expiry (720 hours)
- `CODE_EXPIRE_MINUTES` - Verification code expiry (5 minutes)
- `CODE_LENGTH` - Verification code length (4 digits)
- `UPLOAD_DIR` - Image upload directory
- `MAX_FILE_SIZE` - Maximum upload size (10MB)
- `TIMEZONE_OFFSET` - Timezone offset (UTC+5)

## 📦 Database Functions

### User Management
- `create_user()` - Create new user
- `get_user()` - Get user by ID
- `update_user()` - Update user info
- `get_user_by_phone()` - Find user by phone
- `get_all_users()` - List all users

### Category Management
- `create_category()` - Add category
- `get_category()` - Get category
- `get_all_categories()` - List categories
- `update_category()` - Update category
- `delete_category()` - Soft delete category

### Product Management
- `create_product()` - Add product
- `get_product()` - Get product
- `get_products_by_category()` - Products in category
- `get_all_products()` - List all products
- `update_product()` - Update product
- `delete_product()` - Soft delete product
- `search_products()` - Search by name

### Cart Management
- `add_to_cart()` - Add item to cart
- `get_cart_items()` - Get user's cart
- `update_cart_quantity()` - Update quantity
- `remove_from_cart()` - Remove item
- `clear_cart()` - Clear all items

### Order Management
- `create_order()` - Create new order
- `add_order_item()` - Add item to order
- `get_order()` - Get order details
- `get_order_items()` - Get order items
- `get_user_orders()` - User's orders
- `get_all_orders()` - All orders
- `update_order_status()` - Update status

### Admin Management
- `create_admin()` - Add admin
- `get_admin()` - Get admin
- `get_all_admins()` - List admins
- `is_admin()` - Check admin status
- `is_super_admin()` - Check super admin
- `remove_admin()` - Remove admin

### Verification
- `create_verification_code()` - Create code
- `verify_code()` - Verify phone code

### Chat/Support
- `create_message()` - Create message
- `get_user_messages()` - Get chat history
- `mark_messages_read()` - Mark as read

### Favorites
- `add_to_favorites()` - Add to favorites
- `remove_from_favorites()` - Remove favorite
- `get_user_favorites()` - Get favorites
- `is_favorite()` - Check if favorite

### Statistics
- `get_statistics()` - Get system stats

## 🤖 Bot Module

### States (bot/states.py)

FSM states for user flows:

- `RegistrationStates` - User registration
- `AddProductStates` - Add product (admin)
- `EditProductStates` - Edit product (admin)
- `AddCategoryStates` - Add category (admin)
- `AddNeighborhoodStates` - Add neighborhood (admin)
- `OrderStates` - Order placement
- `AddAdminStates` - Add admin (super admin)
- `BroadcastStates` - Broadcast messages
- `SupportStates` - Customer support
- `SearchStates` - Product search
- `UserbotStates` - Userbot setup

### Keyboards (bot/keyboards.py)

Keyboard generators (bilingual - Uzbek/Russian):

- `get_main_menu_keyboard()` - Main user menu
- `get_admin_menu_keyboard()` - Admin menu
- `get_language_keyboard()` - Language selection
- `get_phone_keyboard()` - Phone number request
- `get_categories_keyboard()` - Category list
- `get_products_keyboard()` - Product list with pagination
- `get_product_detail_keyboard()` - Product details
- `get_cart_keyboard()` - Shopping cart
- `get_cart_item_keyboard()` - Cart item controls
- `get_neighborhoods_keyboard()` - Neighborhood selection
- `get_payment_keyboard()` - Payment method
- `get_confirmation_keyboard()` - Order confirmation
- `get_orders_keyboard()` - Order list
- `get_admin_product_keyboard()` - Product management
- `get_admin_order_keyboard()` - Order management
- And more utility keyboards...

### Utilities (bot/utils.py)

Helper functions:

- `get_text()` - Get translated text
- `generate_code()` - Generate verification code
- `format_phone()` - Format phone number
- `validate_phone()` - Validate phone format
- `format_price()` - Format price with separators
- `format_datetime()` - Format datetime with timezone
- `calculate_cart_total()` - Calculate cart total
- `format_order_details()` - Format order for display
- `format_product_details()` - Format product for display
- `save_image()` - Save and resize uploaded images
- `validate_number()` - Validate numeric input
- `validate_integer()` - Validate integer input
- `format_statistics()` - Format stats for display
- `is_valid_image()` - Validate image file

## 🚀 Installation

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Initialize database:
```python
import database
database.init_db()
```

3. Configure settings in `config.py`

4. The super admin (ID: 5895427105) is automatically created

## 📝 Features

- ✅ Bilingual support (Uzbek/Russian)
- ✅ User registration with phone verification
- ✅ Product catalog with categories
- ✅ Shopping cart functionality
- ✅ Order management system
- ✅ Admin panel with role-based access
- ✅ Customer support chat
- ✅ Favorites system
- ✅ Image upload and processing
- ✅ Statistics and reporting
- ✅ Broadcast messaging
- ✅ Neighborhood-based delivery pricing

## 🔒 Security

- Phone number verification
- Admin role-based access control
- Super admin privileges
- Session management
- Image validation and size limits
- SQL injection protection (parameterized queries)

## 📊 Database Initialization

The database is automatically initialized with:
- All required tables
- Super admin user (ID: 5895427105)
- Proper indexes and foreign keys
- Timestamp tracking

## 🌍 Localization

Full bilingual support:
- Uzbek (uz) - Default
- Russian (ru)

All user-facing text, keyboards, and messages are translated.

## 📄 License

Proprietary - ZarbdorUn Project
