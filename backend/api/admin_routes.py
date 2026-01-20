from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List
import jwt
import random
import os
import shutil
from datetime import datetime, timedelta
from config import API_SECRET_KEY, JWT_EXPIRE_HOURS, CODE_EXPIRE_MINUTES, CODE_LENGTH, UPLOAD_DIR, MAX_FILE_SIZE
import database as db

router = APIRouter(prefix="/api/admin")
security = HTTPBearer()

# Pydantic Models for Admin
class AdminRequestCodeModel(BaseModel):
    admin_id: int

class AdminVerifyCodeModel(BaseModel):
    admin_id: int
    code: str = Field(..., min_length=CODE_LENGTH, max_length=CODE_LENGTH)

class OrderStatusUpdateModel(BaseModel):
    status: str = Field(..., regex='^(pending|confirmed|processing|shipped|delivered|cancelled)$')

class ProductCreateModel(BaseModel):
    category_id: int
    name_uz: str = Field(..., min_length=1, max_length=200)
    name_ru: str = Field(..., min_length=1, max_length=200)
    description_uz: Optional[str] = None
    description_ru: Optional[str] = None
    price: float = Field(..., gt=0)
    discount_price: Optional[float] = None
    stock_quantity: int = Field(default=0, ge=0)

class ProductUpdateModel(BaseModel):
    category_id: Optional[int] = None
    name_uz: Optional[str] = Field(None, min_length=1, max_length=200)
    name_ru: Optional[str] = Field(None, min_length=1, max_length=200)
    description_uz: Optional[str] = None
    description_ru: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    discount_price: Optional[float] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[int] = None

class CategoryCreateModel(BaseModel):
    name_uz: str = Field(..., min_length=1, max_length=100)
    name_ru: str = Field(..., min_length=1, max_length=100)
    description_uz: Optional[str] = None
    description_ru: Optional[str] = None

class CategoryUpdateModel(BaseModel):
    name_uz: Optional[str] = Field(None, min_length=1, max_length=100)
    name_ru: Optional[str] = Field(None, min_length=1, max_length=100)
    description_uz: Optional[str] = None
    description_ru: Optional[str] = None
    is_active: Optional[int] = None

class NeighborhoodCreateModel(BaseModel):
    name_uz: str = Field(..., min_length=1, max_length=100)
    name_ru: str = Field(..., min_length=1, max_length=100)
    delivery_price: float = Field(default=0, ge=0)

class NeighborhoodUpdateModel(BaseModel):
    name_uz: Optional[str] = Field(None, min_length=1, max_length=100)
    name_ru: Optional[str] = Field(None, min_length=1, max_length=100)
    delivery_price: Optional[float] = Field(None, ge=0)
    is_active: Optional[int] = None

class AdminCreateModel(BaseModel):
    admin_id: int
    username: Optional[str] = None
    role: str = Field(default='admin', regex='^(admin|super_admin)$')

class UserbotSettingsModel(BaseModel):
    api_id: int
    api_hash: str
    phone: str
    session_string: Optional[str] = None

class AdminChatReplyModel(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)

class MessageResponse(BaseModel):
    message: str
    success: bool = True

# Helper Functions
def create_admin_access_token(admin_id: int) -> str:
    """Create JWT access token for admin"""
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {
        'admin_id': admin_id,
        'exp': expire,
        'type': 'admin'
    }
    token = jwt.encode(payload, API_SECRET_KEY, algorithm='HS256')
    return token

def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Verify JWT token and return admin_id"""
    try:
        payload = jwt.decode(credentials.credentials, API_SECRET_KEY, algorithms=['HS256'])
        admin_id = payload.get('admin_id')
        token_type = payload.get('type')
        
        if admin_id is None or token_type != 'admin':
            raise HTTPException(status_code=401, detail="Invalid admin token")
        
        # Verify admin exists and is active
        admin = db.get_admin(admin_id)
        if not admin or not admin.get('is_active'):
            raise HTTPException(status_code=401, detail="Admin not found or inactive")
        
        return admin_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def verify_super_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Verify super admin token"""
    admin_id = verify_admin_token(credentials)
    if not db.is_super_admin(admin_id):
        raise HTTPException(status_code=403, detail="Super admin access required")
    return admin_id

def generate_verification_code() -> str:
    """Generate random verification code"""
    return ''.join([str(random.randint(0, 9)) for _ in range(CODE_LENGTH)])

# Admin Authentication
@router.post("/auth/request-code", response_model=MessageResponse)
async def admin_request_code(data: AdminRequestCodeModel):
    """Request verification code for admin login"""
    # Verify admin exists
    admin = db.get_admin(data.admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    code = generate_verification_code()
    # Store code temporarily (using phone as admin_id string)
    db.create_verification_code(str(data.admin_id), code, CODE_EXPIRE_MINUTES)
    
    # TODO: Send code via Telegram bot
    # For now, return code in response (ONLY FOR DEVELOPMENT)
    return {
        "message": "Verification code sent to admin",
        "success": True,
        "code": code  # Remove this in production
    }

@router.post("/auth/verify-code")
async def admin_verify_code(data: AdminVerifyCodeModel):
    """Verify admin code and return JWT token"""
    if not db.verify_code(str(data.admin_id), data.code):
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    
    admin = db.get_admin(data.admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    # Create JWT token
    token = create_admin_access_token(data.admin_id)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "admin": admin,
        "success": True
    }

# Statistics
@router.get("/statistics")
async def get_statistics(admin_id: int = Depends(verify_admin_token)):
    """Get general statistics"""
    stats = db.get_statistics()
    return {"statistics": stats, "success": True}

# Orders Management
@router.get("/orders")
async def get_all_orders(
    status: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    admin_id: int = Depends(verify_admin_token)
):
    """Get all orders with optional filters"""
    orders = db.get_all_orders(status=status)
    
    # Add items to each order
    for order in orders:
        order['items'] = db.get_order_items(order['order_id'])
        # Get user info
        user = db.get_user(order['user_id'])
        order['user'] = user
    
    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_orders = orders[start:end]
    
    return {
        "orders": paginated_orders,
        "total": len(orders),
        "page": page,
        "per_page": per_page,
        "success": True
    }

@router.get("/orders/{order_id}")
async def get_order_details(order_id: int, admin_id: int = Depends(verify_admin_token)):
    """Get order details"""
    order = db.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    items = db.get_order_items(order_id)
    user = db.get_user(order['user_id'])
    
    order['items'] = items
    order['user'] = user
    
    return {"order": order, "success": True}

@router.put("/orders/{order_id}/status", response_model=MessageResponse)
async def update_order_status(
    order_id: int,
    data: OrderStatusUpdateModel,
    admin_id: int = Depends(verify_admin_token)
):
    """Update order status"""
    if not db.update_order_status(order_id, data.status):
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"message": "Order status updated", "success": True}

# Products Management
@router.get("/products")
async def get_all_products_admin(
    active_only: bool = False,
    category_id: Optional[int] = None,
    admin_id: int = Depends(verify_admin_token)
):
    """Get all products (including inactive)"""
    if category_id:
        products = db.get_products_by_category(category_id)
    else:
        products = db.get_all_products(active_only=active_only)
    
    return {"products": products, "success": True}

@router.post("/products")
async def create_product(
    data: ProductCreateModel,
    admin_id: int = Depends(verify_admin_token)
):
    """Create new product"""
    # Verify category exists
    category = db.get_category(data.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    product_id = db.create_product(
        category_id=data.category_id,
        name_uz=data.name_uz,
        name_ru=data.name_ru,
        description_uz=data.description_uz,
        description_ru=data.description_ru,
        price=data.price,
        discount_price=data.discount_price,
        stock_quantity=data.stock_quantity
    )
    
    product = db.get_product(product_id)
    return {"product": product, "message": "Product created", "success": True}

@router.put("/products/{product_id}")
async def update_product(
    product_id: int,
    data: ProductUpdateModel,
    admin_id: int = Depends(verify_admin_token)
):
    """Update product"""
    # Prepare update data
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    if not db.update_product(product_id, **update_data):
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = db.get_product(product_id)
    return {"product": product, "message": "Product updated", "success": True}

@router.delete("/products/{product_id}", response_model=MessageResponse)
async def delete_product(product_id: int, admin_id: int = Depends(verify_admin_token)):
    """Delete product (soft delete)"""
    if not db.delete_product(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted", "success": True}

@router.post("/products/{product_id}/upload-image")
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    admin_id: int = Depends(verify_admin_token)
):
    """Upload product image"""
    # Verify product exists
    product = db.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check file type
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Save file
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_name = f"product_{product_id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update product
    db.update_product(product_id, image_path=file_path)
    
    return {
        "message": "Image uploaded",
        "file_path": file_path,
        "success": True
    }

# Categories Management
@router.get("/categories")
async def get_all_categories_admin(
    active_only: bool = False,
    admin_id: int = Depends(verify_admin_token)
):
    """Get all categories (including inactive)"""
    categories = db.get_all_categories(active_only=active_only)
    return {"categories": categories, "success": True}

@router.post("/categories")
async def create_category(
    data: CategoryCreateModel,
    admin_id: int = Depends(verify_admin_token)
):
    """Create new category"""
    category_id = db.create_category(
        name_uz=data.name_uz,
        name_ru=data.name_ru,
        description_uz=data.description_uz,
        description_ru=data.description_ru
    )
    
    category = db.get_category(category_id)
    return {"category": category, "message": "Category created", "success": True}

@router.put("/categories/{category_id}")
async def update_category(
    category_id: int,
    data: CategoryUpdateModel,
    admin_id: int = Depends(verify_admin_token)
):
    """Update category"""
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    if not db.update_category(category_id, **update_data):
        raise HTTPException(status_code=404, detail="Category not found")
    
    category = db.get_category(category_id)
    return {"category": category, "message": "Category updated", "success": True}

@router.delete("/categories/{category_id}", response_model=MessageResponse)
async def delete_category(category_id: int, admin_id: int = Depends(verify_admin_token)):
    """Delete category (soft delete)"""
    if not db.delete_category(category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted", "success": True}

# Neighborhoods Management
@router.get("/neighborhoods")
async def get_all_neighborhoods_admin(
    active_only: bool = False,
    admin_id: int = Depends(verify_admin_token)
):
    """Get all neighborhoods (including inactive)"""
    neighborhoods = db.get_all_neighborhoods(active_only=active_only)
    return {"neighborhoods": neighborhoods, "success": True}

@router.post("/neighborhoods")
async def create_neighborhood(
    data: NeighborhoodCreateModel,
    admin_id: int = Depends(verify_admin_token)
):
    """Create new neighborhood"""
    neighborhood_id = db.create_neighborhood(
        name_uz=data.name_uz,
        name_ru=data.name_ru,
        delivery_price=data.delivery_price
    )
    
    neighborhood = db.get_neighborhood(neighborhood_id)
    return {"neighborhood": neighborhood, "message": "Neighborhood created", "success": True}

@router.put("/neighborhoods/{neighborhood_id}")
async def update_neighborhood(
    neighborhood_id: int,
    data: NeighborhoodUpdateModel,
    admin_id: int = Depends(verify_admin_token)
):
    """Update neighborhood"""
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    if not db.update_neighborhood(neighborhood_id, **update_data):
        raise HTTPException(status_code=404, detail="Neighborhood not found")
    
    neighborhood = db.get_neighborhood(neighborhood_id)
    return {"neighborhood": neighborhood, "message": "Neighborhood updated", "success": True}

@router.delete("/neighborhoods/{neighborhood_id}", response_model=MessageResponse)
async def delete_neighborhood(
    neighborhood_id: int,
    admin_id: int = Depends(verify_admin_token)
):
    """Delete neighborhood (soft delete)"""
    if not db.update_neighborhood(neighborhood_id, is_active=0):
        raise HTTPException(status_code=404, detail="Neighborhood not found")
    return {"message": "Neighborhood deleted", "success": True}

# Admins Management (Super Admin Only)
@router.get("/admins")
async def get_all_admins(admin_id: int = Depends(verify_super_admin)):
    """Get all admins (super admin only)"""
    admins = db.get_all_admins()
    return {"admins": admins, "success": True}

@router.post("/admins")
async def create_admin(
    data: AdminCreateModel,
    admin_id: int = Depends(verify_super_admin)
):
    """Create new admin (super admin only)"""
    if not db.create_admin(data.admin_id, data.username, data.role):
        raise HTTPException(status_code=400, detail="Admin already exists")
    
    admin = db.get_admin(data.admin_id)
    return {"admin": admin, "message": "Admin created", "success": True}

@router.delete("/admins/{target_admin_id}", response_model=MessageResponse)
async def remove_admin(
    target_admin_id: int,
    admin_id: int = Depends(verify_super_admin)
):
    """Remove admin (super admin only)"""
    if target_admin_id == admin_id:
        raise HTTPException(status_code=400, detail="Cannot remove yourself")
    
    if not db.remove_admin(target_admin_id):
        raise HTTPException(status_code=404, detail="Admin not found")
    
    return {"message": "Admin removed", "success": True}

# Userbot Settings
@router.get("/userbot")
async def get_userbot_settings(admin_id: int = Depends(verify_admin_token)):
    """Get userbot settings"""
    settings = db.get_userbot_settings()
    if settings:
        # Hide sensitive data
        settings['api_hash'] = '***'
        settings['session_string'] = '***' if settings.get('session_string') else None
    
    return {"settings": settings, "success": True}

@router.put("/userbot")
async def update_userbot_settings(
    data: UserbotSettingsModel,
    admin_id: int = Depends(verify_admin_token)
):
    """Update userbot settings"""
    db.save_userbot_settings(
        api_id=data.api_id,
        api_hash=data.api_hash,
        phone=data.phone,
        session_string=data.session_string
    )
    
    return {"message": "Userbot settings updated", "success": True}

# Chat Management
@router.get("/chats")
async def get_unread_chats(admin_id: int = Depends(verify_admin_token)):
    """Get users with unread messages"""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT u.*, COUNT(cm.message_id) as unread_count
        FROM chat_messages cm
        JOIN users u ON cm.user_id = u.user_id
        WHERE cm.is_read = 0 AND cm.sender_type = 'user'
        GROUP BY u.user_id
        ORDER BY MAX(cm.created_at) DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    chats = [dict(row) for row in rows]
    return {"chats": chats, "success": True}

@router.get("/chats/{user_id}")
async def get_chat_messages(user_id: int, admin_id: int = Depends(verify_admin_token)):
    """Get chat messages with specific user"""
    messages = db.get_user_messages(user_id)
    
    # Mark admin messages as read
    db.mark_messages_read(user_id, admin_id)
    
    return {"messages": messages, "success": True}

@router.post("/chats/{user_id}/reply", response_model=MessageResponse)
async def reply_to_chat(
    user_id: int,
    data: AdminChatReplyModel,
    admin_id: int = Depends(verify_admin_token)
):
    """Reply to user chat"""
    # Verify user exists
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    message_id = db.create_message(user_id, data.message, 'admin', admin_id)
    
    return {
        "message": "Reply sent",
        "message_id": message_id,
        "success": True
    }

# Users Management
@router.get("/users")
async def get_all_users(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=100),
    admin_id: int = Depends(verify_admin_token)
):
    """Get all users"""
    users = db.get_all_users()
    
    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_users = users[start:end]
    
    return {
        "users": paginated_users,
        "total": len(users),
        "page": page,
        "per_page": per_page,
        "success": True
    }

@router.get("/users/{user_id}")
async def get_user_details(user_id: int, admin_id: int = Depends(verify_admin_token)):
    """Get user details"""
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's orders
    orders = db.get_user_orders(user_id)
    
    return {
        "user": user,
        "orders": orders,
        "success": True
    }
