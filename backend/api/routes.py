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

router = APIRouter()
security = HTTPBearer()

# Pydantic Models
class RequestCodeModel(BaseModel):
    phone: str = Field(..., min_length=9, max_length=15)

class VerifyCodeModel(BaseModel):
    phone: str = Field(..., min_length=9, max_length=15)
    code: str = Field(..., min_length=CODE_LENGTH, max_length=CODE_LENGTH)

class CartAddModel(BaseModel):
    product_id: int
    quantity: int = Field(default=1, gt=0)

class CartUpdateModel(BaseModel):
    cart_id: int
    quantity: int = Field(..., gt=0)

class FavoriteModel(BaseModel):
    product_id: int

class OrderCreateModel(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=9, max_length=15)
    address: str = Field(..., min_length=5, max_length=500)
    neighborhood_id: Optional[int] = None
    payment_method: str = Field(default='cash')
    notes: Optional[str] = None

class ChatMessageModel(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)

# Response Models
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class MessageResponse(BaseModel):
    message: str
    success: bool = True

class ProductResponse(BaseModel):
    product_id: int
    category_id: int
    name_uz: str
    name_ru: str
    description_uz: Optional[str]
    description_ru: Optional[str]
    price: float
    discount_price: Optional[float]
    stock_quantity: int
    image_path: Optional[str]
    is_favorite: bool = False

class OrderResponse(BaseModel):
    order_id: int
    full_name: str
    phone: str
    address: str
    total_amount: float
    delivery_price: float
    payment_method: str
    status: str
    created_at: str
    items: List[dict]

# Helper Functions
def create_access_token(user_id: int) -> str:
    """Create JWT access token"""
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {
        'user_id': user_id,
        'exp': expire
    }
    token = jwt.encode(payload, API_SECRET_KEY, algorithm='HS256')
    return token

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Verify JWT token and return user_id"""
    try:
        payload = jwt.decode(credentials.credentials, API_SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Verify user exists and is active
        user = db.get_user(user_id)
        if not user or not user.get('is_active'):
            raise HTTPException(status_code=401, detail="User not found or inactive")
        
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def generate_verification_code() -> str:
    """Generate random verification code"""
    return ''.join([str(random.randint(0, 9)) for _ in range(CODE_LENGTH)])

# Authentication Endpoints
@router.post("/api/auth/request-code", response_model=MessageResponse)
async def request_verification_code(data: RequestCodeModel):
    """Request verification code for phone number"""
    code = generate_verification_code()
    db.create_verification_code(data.phone, code, CODE_EXPIRE_MINUTES)
    
    # TODO: Send code via SMS or Telegram userbot
    # For now, return code in response (ONLY FOR DEVELOPMENT)
    return {
        "message": f"Verification code sent to {data.phone}",
        "success": True,
        "code": code  # Remove this in production
    }

@router.post("/api/auth/verify-code", response_model=TokenResponse)
async def verify_verification_code(data: VerifyCodeModel):
    """Verify code and return JWT token"""
    if not db.verify_code(data.phone, data.code):
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    
    # Get or create user
    user = db.get_user_by_phone(data.phone)
    if not user:
        # Create new user with phone
        user_id = int(data.phone.replace('+', ''))
        db.create_user(user_id, phone=data.phone)
        user = db.get_user(user_id)
    
    # Create JWT token
    token = create_access_token(user['user_id'])
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/api/auth/logout", response_model=MessageResponse)
async def logout(user_id: int = Depends(verify_token)):
    """Logout user (client should delete token)"""
    return {"message": "Logged out successfully", "success": True}

@router.get("/api/auth/me")
async def get_current_user(user_id: int = Depends(verify_token)):
    """Get current authenticated user"""
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Category Endpoints
@router.get("/api/categories")
async def get_categories(language: str = Query(default='uz', regex='^(uz|ru)$')):
    """Get all active categories"""
    categories = db.get_all_categories(active_only=True)
    return {"categories": categories, "success": True}

# Product Endpoints
@router.get("/api/products")
async def get_products(
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    language: str = Query(default='uz', regex='^(uz|ru)$'),
    user_id: Optional[int] = Depends(verify_token)
):
    """Get products with optional filters"""
    if search:
        products = db.search_products(search, language)
    elif category_id:
        products = db.get_products_by_category(category_id)
    else:
        products = db.get_all_products(active_only=True)
    
    # Add favorite status if user is authenticated
    if user_id:
        for product in products:
            product['is_favorite'] = db.is_favorite(user_id, product['product_id'])
    
    return {"products": products, "success": True}

@router.get("/api/products/{product_id}")
async def get_product(
    product_id: int,
    user_id: Optional[int] = Depends(verify_token)
):
    """Get single product by ID"""
    product = db.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Add favorite status
    if user_id:
        product['is_favorite'] = db.is_favorite(user_id, product['product_id'])
    
    return {"product": product, "success": True}

# Cart Endpoints
@router.get("/api/cart")
async def get_cart(user_id: int = Depends(verify_token)):
    """Get user's cart items"""
    cart_items = db.get_cart_items(user_id)
    
    # Calculate totals
    total = sum(item['quantity'] * (item['discount_price'] or item['price']) for item in cart_items)
    
    return {
        "cart_items": cart_items,
        "total": total,
        "count": len(cart_items),
        "success": True
    }

@router.post("/api/cart/add", response_model=MessageResponse)
async def add_to_cart(data: CartAddModel, user_id: int = Depends(verify_token)):
    """Add item to cart"""
    # Verify product exists
    product = db.get_product(data.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check stock
    if product['stock_quantity'] < data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    db.add_to_cart(user_id, data.product_id, data.quantity)
    return {"message": "Product added to cart", "success": True}

@router.put("/api/cart/update", response_model=MessageResponse)
async def update_cart(data: CartUpdateModel, user_id: int = Depends(verify_token)):
    """Update cart item quantity"""
    if not db.update_cart_quantity(data.cart_id, data.quantity):
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {"message": "Cart updated", "success": True}

@router.delete("/api/cart/remove/{cart_id}", response_model=MessageResponse)
async def remove_from_cart(cart_id: int, user_id: int = Depends(verify_token)):
    """Remove item from cart"""
    if not db.remove_from_cart(cart_id):
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {"message": "Item removed from cart", "success": True}

@router.delete("/api/cart/clear", response_model=MessageResponse)
async def clear_cart(user_id: int = Depends(verify_token)):
    """Clear all items from cart"""
    db.clear_cart(user_id)
    return {"message": "Cart cleared", "success": True}

# Favorites Endpoints
@router.get("/api/favorites")
async def get_favorites(user_id: int = Depends(verify_token)):
    """Get user's favorite products"""
    favorites = db.get_user_favorites(user_id)
    return {"favorites": favorites, "count": len(favorites), "success": True}

@router.post("/api/favorites/add", response_model=MessageResponse)
async def add_to_favorites(data: FavoriteModel, user_id: int = Depends(verify_token)):
    """Add product to favorites"""
    # Verify product exists
    product = db.get_product(data.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if not db.add_to_favorites(user_id, data.product_id):
        raise HTTPException(status_code=400, detail="Product already in favorites")
    
    return {"message": "Product added to favorites", "success": True}

@router.delete("/api/favorites/remove/{product_id}", response_model=MessageResponse)
async def remove_from_favorites(product_id: int, user_id: int = Depends(verify_token)):
    """Remove product from favorites"""
    if not db.remove_from_favorites(user_id, product_id):
        raise HTTPException(status_code=404, detail="Product not in favorites")
    return {"message": "Product removed from favorites", "success": True}

# Neighborhoods Endpoints
@router.get("/api/neighborhoods")
async def get_neighborhoods():
    """Get all active neighborhoods"""
    neighborhoods = db.get_all_neighborhoods(active_only=True)
    return {"neighborhoods": neighborhoods, "success": True}

# Order Endpoints
@router.post("/api/orders/create")
async def create_order(data: OrderCreateModel, user_id: int = Depends(verify_token)):
    """Create new order from cart"""
    # Get cart items
    cart_items = db.get_cart_items(user_id)
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Calculate total
    total_amount = sum(item['quantity'] * (item['discount_price'] or item['price']) for item in cart_items)
    
    # Get delivery price
    delivery_price = 0
    if data.neighborhood_id:
        neighborhood = db.get_neighborhood(data.neighborhood_id)
        if neighborhood:
            delivery_price = neighborhood['delivery_price']
    
    # Create order
    order_id = db.create_order(
        user_id=user_id,
        full_name=data.full_name,
        phone=data.phone,
        address=data.address,
        total_amount=total_amount,
        neighborhood_id=data.neighborhood_id,
        delivery_price=delivery_price,
        payment_method=data.payment_method,
        notes=data.notes
    )
    
    # Add order items
    for item in cart_items:
        db.add_order_item(
            order_id=order_id,
            product_id=item['product_id'],
            quantity=item['quantity'],
            price=item['discount_price'] or item['price']
        )
    
    # Clear cart
    db.clear_cart(user_id)
    
    # Get order details
    order = db.get_order(order_id)
    items = db.get_order_items(order_id)
    
    return {
        "order": {**order, "items": items},
        "message": "Order created successfully",
        "success": True
    }

@router.get("/api/orders")
async def get_user_orders(user_id: int = Depends(verify_token)):
    """Get user's orders"""
    orders = db.get_user_orders(user_id)
    
    # Add items to each order
    for order in orders:
        order['items'] = db.get_order_items(order['order_id'])
    
    return {"orders": orders, "success": True}

@router.get("/api/orders/{order_id}")
async def get_order_details(order_id: int, user_id: int = Depends(verify_token)):
    """Get order details"""
    order = db.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Verify order belongs to user
    if order['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    items = db.get_order_items(order_id)
    order['items'] = items
    
    return {"order": order, "success": True}

# Chat Endpoints
@router.get("/api/chat/messages")
async def get_chat_messages(user_id: int = Depends(verify_token)):
    """Get chat messages for user"""
    messages = db.get_user_messages(user_id)
    db.mark_messages_read(user_id)
    return {"messages": messages, "success": True}

@router.post("/api/chat/send", response_model=MessageResponse)
async def send_chat_message(data: ChatMessageModel, user_id: int = Depends(verify_token)):
    """Send chat message to admin"""
    message_id = db.create_message(user_id, data.message, 'user')
    return {"message": "Message sent", "message_id": message_id, "success": True}

@router.post("/api/chat/upload")
async def upload_chat_file(
    file: UploadFile = File(...),
    user_id: int = Depends(verify_token)
):
    """Upload file to chat"""
    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Save file
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_extension = os.path.splitext(file.filename)[1]
    file_name = f"chat_{user_id}_{datetime.now().timestamp()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create message with file reference
    db.create_message(user_id, f"[File: {file.filename}]", 'user')
    
    return {
        "message": "File uploaded",
        "file_path": file_path,
        "success": True
    }
