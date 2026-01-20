# ZarbdorUn E-commerce REST API

Complete REST API implementation for the ZarbdorUn e-commerce platform.

## Features

- JWT Authentication
- User Management
- Product Catalog
- Shopping Cart
- Favorites
- Order Management
- Admin Panel
- Chat System
- File Upload
- CORS Support

## Installation

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Run the API server:
```bash
python -m api.main
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## User API Endpoints

### Authentication
- `POST /api/auth/request-code` - Request verification code
- `POST /api/auth/verify-code` - Verify code and get JWT token
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

### Categories
- `GET /api/categories` - Get all categories

### Products
- `GET /api/products` - Get products (with filters: category_id, search)
- `GET /api/products/{id}` - Get single product

### Cart
- `GET /api/cart` - Get user's cart
- `POST /api/cart/add` - Add to cart
- `PUT /api/cart/update` - Update cart item
- `DELETE /api/cart/remove/{id}` - Remove from cart
- `DELETE /api/cart/clear` - Clear cart

### Favorites
- `GET /api/favorites` - Get favorites
- `POST /api/favorites/add` - Add to favorites
- `DELETE /api/favorites/remove/{id}` - Remove from favorites

### Neighborhoods
- `GET /api/neighborhoods` - Get neighborhoods

### Orders
- `POST /api/orders/create` - Create order
- `GET /api/orders` - Get user's orders
- `GET /api/orders/{id}` - Get order details

### Chat
- `GET /api/chat/messages` - Get chat messages
- `POST /api/chat/send` - Send chat message
- `POST /api/chat/upload` - Upload file to chat

## Admin API Endpoints

### Authentication
- `POST /api/admin/auth/request-code` - Admin login request
- `POST /api/admin/auth/verify-code` - Admin verify code

### Statistics
- `GET /api/admin/statistics` - Get statistics

### Orders
- `GET /api/admin/orders` - Get all orders (with filters)
- `GET /api/admin/orders/{id}` - Get order details
- `PUT /api/admin/orders/{id}/status` - Update order status

### Products
- `GET /api/admin/products` - Get all products
- `POST /api/admin/products` - Create product
- `PUT /api/admin/products/{id}` - Update product
- `DELETE /api/admin/products/{id}` - Delete product
- `POST /api/admin/products/{id}/upload-image` - Upload product image

### Categories
- `GET /api/admin/categories` - Get all categories
- `POST /api/admin/categories` - Create category
- `PUT /api/admin/categories/{id}` - Update category
- `DELETE /api/admin/categories/{id}` - Delete category

### Neighborhoods
- `GET /api/admin/neighborhoods` - Get all neighborhoods
- `POST /api/admin/neighborhoods` - Create neighborhood
- `PUT /api/admin/neighborhoods/{id}` - Update neighborhood
- `DELETE /api/admin/neighborhoods/{id}` - Delete neighborhood

### Admins (Super Admin Only)
- `GET /api/admin/admins` - Get all admins
- `POST /api/admin/admins` - Create admin
- `DELETE /api/admin/admins/{id}` - Remove admin

### Userbot
- `GET /api/admin/userbot` - Get userbot settings
- `PUT /api/admin/userbot` - Update userbot settings

### Chat
- `GET /api/admin/chats` - Get unread chats
- `GET /api/admin/chats/{user_id}` - Get chat messages
- `POST /api/admin/chats/{user_id}/reply` - Reply to chat

### Users
- `GET /api/admin/users` - Get all users
- `GET /api/admin/users/{id}` - Get user details

## Authentication

### User Authentication

1. Request verification code:
```bash
curl -X POST http://localhost:8000/api/auth/request-code \
  -H "Content-Type: application/json" \
  -d '{"phone": "+998901234567"}'
```

2. Verify code and get token:
```bash
curl -X POST http://localhost:8000/api/auth/verify-code \
  -H "Content-Type: application/json" \
  -d '{"phone": "+998901234567", "code": "1234"}'
```

3. Use token in subsequent requests:
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Admin Authentication

Same flow but using `/api/admin/auth/` endpoints with admin_id instead of phone.

## Request Examples

### Add to Cart
```bash
curl -X POST http://localhost:8000/api/cart/add \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'
```

### Create Order
```bash
curl -X POST http://localhost:8000/api/orders/create \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "phone": "+998901234567",
    "address": "123 Main St",
    "neighborhood_id": 1,
    "payment_method": "cash"
  }'
```

### Upload Product Image (Admin)
```bash
curl -X POST http://localhost:8000/api/admin/products/1/upload-image \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -F "file=@product.jpg"
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message here"
}
```

HTTP Status Codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 422: Validation Error
- 500: Internal Server Error

## Security

- JWT tokens expire after 720 hours (30 days)
- Verification codes expire after 5 minutes
- Passwords are hashed using bcrypt
- CORS is configured (update origins in production)
- File uploads are validated (type and size)

## File Uploads

Supported image formats: .jpg, .jpeg, .png, .webp
Maximum file size: 10 MB

Uploaded files are stored in the `uploads/` directory and accessible via:
`http://localhost:8000/uploads/filename.jpg`

## Environment Variables

Configure in `config.py`:
- `API_HOST`: API host (default: 0.0.0.0)
- `API_PORT`: API port (default: 8000)
- `DB_NAME`: Database name
- `UPLOAD_DIR`: Upload directory
- `MAX_FILE_SIZE`: Maximum file size in bytes

## Development

### Run with auto-reload:
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Access Interactive Docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Production Deployment

1. Update CORS origins to specific domains
2. Remove development code (e.g., returning verification codes in response)
3. Set up proper SMS/Telegram integration for verification codes
4. Use environment variables for sensitive data
5. Set up HTTPS
6. Configure proper logging
7. Set up database backups

## License

Proprietary - ZarbdorUn E-commerce Platform
