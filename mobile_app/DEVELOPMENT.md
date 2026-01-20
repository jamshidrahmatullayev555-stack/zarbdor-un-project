# ZarbdorUn Mobile App - Development Notes

## Architecture Overview

### State Management Pattern

The app uses Provider pattern with the following structure:

1. **Services Layer**: API calls and WebSocket connections
2. **Providers Layer**: Business logic and state management
3. **UI Layer**: Screens and widgets that consume providers

### Key Design Decisions

1. **Guest Mode**: 
   - Users can browse products without authentication
   - Login required only for cart checkout and orders
   - Favorites and cart stored locally for guests

2. **Offline Support**:
   - Cart and favorites persist in SharedPreferences
   - Network detection with automatic retry
   - Graceful degradation of features

3. **Bilingual Support**:
   - All text translated to Uzbek Latin and Russian
   - Language stored in SharedPreferences
   - Dynamic language switching without app restart

4. **Real-time Features**:
   - WebSocket connection for order chat
   - Automatic reconnection on network loss
   - Message buffering during disconnection

## API Integration

### Endpoints Used

- `POST /auth/send-otp` - Send OTP code
- `POST /auth/verify-otp` - Verify OTP and login
- `GET /users/me` - Get current user
- `GET /categories` - List categories
- `GET /products` - List products (paginated, filtered)
- `GET /products/:id` - Get product details
- `POST /orders` - Create order
- `GET /orders/my` - List user's orders
- `GET /orders/:id` - Get order details
- `POST /orders/:id/cancel` - Cancel order
- `GET /chat/:orderId/messages` - Get chat messages
- `POST /chat/:orderId/messages` - Send message
- `POST /upload/image` - Upload image
- `GET /neighborhoods` - List neighborhoods

### WebSocket

- Connection: `ws://HOST/ws/chat/:orderId?token=TOKEN`
- Message format: JSON with `content`, `image_url`, `timestamp`

## Local Storage

### SharedPreferences Keys

- `auth_token` - JWT access token
- `user_id` - Current user ID
- `language` - Selected language (uz/ru)
- `cart` - Serialized cart items
- `favorites` - Serialized favorite product IDs

## UI/UX Guidelines

### Colors

- Primary: #F97316 (Orange)
- Secondary: #1E293B (Slate)
- Background: #F8FAFC
- Error: #EF4444
- Success: #10B981

### Typography

- Font: Inter (Google Fonts)
- Display: Bold, 24-32px
- Heading: Semi-bold, 18-20px
- Body: Regular, 14-16px

### Spacing

- Padding: 16px standard
- Card margin: 12px
- Section spacing: 24px
- Icon size: 20-24px

## Testing

### Test Accounts

Use any phone number with OTP `123456` for testing.

### Test Data

- Products should have valid image URLs
- Categories should be active
- Neighborhoods should be linked to districts

## Known Issues

1. Image upload size limit: 5MB
2. WebSocket reconnection delay: 3 seconds
3. Map requires Google API key configuration

## Future Enhancements

1. Push notifications for order updates
2. Product reviews and ratings
3. Multiple delivery addresses
4. Payment gateway integration
5. Coupon/promo code support
6. Order history filtering
7. Product comparison
8. Wishlist sharing
