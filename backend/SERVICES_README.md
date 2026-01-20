# Userbot and Notification Services

This directory contains the userbot client and notification services for the ZarbdorUn e-commerce platform.

## Files

### 1. `userbot/client.py` - Telethon Userbot Client

A Telegram userbot client built with Telethon for sending verification codes and messages.

**Features:**
- Initialize userbot from database settings
- Send verification codes via Telegram
- Auto-reconnect on connection errors
- Session management with StringSession
- Save session to database
- Monitor connection health

**Usage:**

```python
from userbot import get_userbot

# Get userbot instance (auto-initializes if needed)
userbot = await get_userbot()

# Send verification code
success = await userbot.send_verification_code("+998901234567", "1234")

# Login userbot (first time setup)
result = await userbot.login(
    api_id=12345,
    api_hash="abc123",
    phone="+998901234567",
    code="12345"  # Telegram code
)

# Check if userbot is active
if userbot.is_active():
    print("Userbot is connected!")
```

**Database Settings:**
The userbot settings are stored in the `userbot_settings` table:
- `api_id`: Telegram API ID
- `api_hash`: Telegram API Hash
- `phone`: Userbot phone number
- `session_string`: Saved session (auto-generated)
- `is_active`: Active status

### 2. `services/notifications.py` - Notification Service

A comprehensive notification service for sending messages via bot and userbot.

**Features:**
- Send verification codes (via userbot)
- Send order status updates to users
- Send new order notifications to admins
- Send admin messages
- Broadcast messages to all users
- Product notifications (back in stock, price drops, etc.)
- Welcome messages
- Cart reminders

**Usage:**

```python
from services import get_notification_service

# Get notification service
notif = get_notification_service()

# Send verification code
result = await notif.send_verification_code("+998901234567", "1234")

# Send order notification to user
await notif.send_order_notification(
    user_id=123456,
    order_id=1,
    status='confirmed',
    language='uz'
)

# Notify admins about new order
await notif.send_new_order_to_admins(order_id=1)

# Broadcast message to all users
result = await notif.broadcast_message(
    message="🎉 Special offer! 50% discount on all products!",
    exclude_blocked=True
)

# Send welcome message
await notif.send_welcome_message(user_id=123456, language='uz')

# Send product notification
await notif.send_product_notification(
    user_id=123456,
    product_id=1,
    notification_type='back_in_stock',
    language='uz'
)
```

## Order Status Notifications

Supported order statuses with automatic notifications:
- `pending`: Order received and being reviewed
- `confirmed`: Order confirmed and being prepared
- `preparing`: Order is being prepared
- `delivering`: Order is being delivered
- `completed`: Order delivered successfully
- `cancelled`: Order cancelled

## Notification Types

### Verification Code
Sends verification code via Telegram userbot. Falls back to logging if userbot unavailable.

### Order Updates
Automatically sends status updates to users in their preferred language (uz/ru).

### Admin Notifications
Sends new order notifications to all active admins with inline action buttons:
- ✅ Confirm order
- ❌ Cancel order
- 📋 View details

### Broadcast Messages
Send messages to all users or specific user list. Returns statistics:
- Total users
- Successfully sent
- Failed
- Blocked users

### Product Notifications
- `back_in_stock`: Notify when product is available again
- `price_drop`: Notify about discounts
- `new_product`: Notify about new products

## Error Handling

Both services include comprehensive error handling:
- Automatic reconnection for userbot
- Graceful handling of blocked users
- Logging of all errors
- Fallback mechanisms for critical operations

## Dependencies

- `telethon`: Telegram userbot client
- `aiogram`: Telegram bot framework
- `asyncio`: Async operations

## Configuration

Required settings in `config.py`:
- `BOT_TOKEN`: Telegram bot token
- `SUPER_ADMIN_ID`: Super admin Telegram ID

Required database tables:
- `userbot_settings`: Userbot configuration
- `users`: User data
- `admins`: Admin list
- `orders`: Orders data
- `order_items`: Order items
- `products`: Products catalog

## Example Integration

```python
# In your bot handlers
from services import get_notification_service

async def order_created_handler(order_id: int, user_id: int):
    notif = get_notification_service()
    
    # Notify user
    await notif.send_order_notification(
        user_id=user_id,
        order_id=order_id,
        status='pending',
        language='uz'
    )
    
    # Notify admins
    await notif.send_new_order_to_admins(order_id)

# In your API routes
from services import get_notification_service

async def send_code(phone: str, code: str):
    notif = get_notification_service()
    result = await notif.send_verification_code(phone, code)
    return result
```

## Testing

To test the services:

```python
import asyncio
from userbot import get_userbot
from services import get_notification_service

async def test():
    # Test userbot
    userbot = await get_userbot()
    print(f"Userbot active: {userbot.is_active()}")
    
    # Test notification service
    notif = get_notification_service()
    result = await notif.send_verification_code("+998901234567", "1234")
    print(f"Verification result: {result}")

asyncio.run(test())
```

## Logging

Both services use Python's logging module. Configure logging level:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Security Notes

- Never commit API credentials to version control
- Store userbot session securely in database
- Use environment variables for sensitive data
- Implement rate limiting for broadcast messages
- Validate user permissions before sending admin notifications
