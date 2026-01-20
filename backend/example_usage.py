"""
Example usage of userbot client and notification services
"""
import asyncio
from userbot import get_userbot
from services import get_notification_service


async def example_verification_code():
    """Example: Send verification code"""
    print("\n=== Example: Verification Code ===")
    
    # Get notification service
    notif = get_notification_service()
    
    # Send verification code
    result = await notif.send_verification_code(
        phone="+998901234567",
        code="1234"
    )
    
    print(f"Result: {result}")


async def example_order_notification():
    """Example: Send order notification to user"""
    print("\n=== Example: Order Notification ===")
    
    notif = get_notification_service()
    
    # Send order status update
    success = await notif.send_order_notification(
        user_id=123456789,
        order_id=1,
        status='confirmed',
        language='uz'
    )
    
    print(f"Notification sent: {success}")


async def example_admin_notification():
    """Example: Notify admins about new order"""
    print("\n=== Example: Admin Notification ===")
    
    notif = get_notification_service()
    
    # Notify all admins
    count = await notif.send_new_order_to_admins(order_id=1)
    
    print(f"Notified {count} admins")


async def example_broadcast():
    """Example: Broadcast message to all users"""
    print("\n=== Example: Broadcast Message ===")
    
    notif = get_notification_service()
    
    # Broadcast to all users
    result = await notif.broadcast_message(
        message="🎉 <b>Special Offer!</b>\n\n50% discount on all products!",
        exclude_blocked=True
    )
    
    print(f"Broadcast stats: {result}")


async def example_welcome_message():
    """Example: Send welcome message"""
    print("\n=== Example: Welcome Message ===")
    
    notif = get_notification_service()
    
    success = await notif.send_welcome_message(
        user_id=123456789,
        language='uz'
    )
    
    print(f"Welcome message sent: {success}")


async def example_product_notification():
    """Example: Send product notification"""
    print("\n=== Example: Product Notification ===")
    
    notif = get_notification_service()
    
    # Notify about product back in stock
    success = await notif.send_product_notification(
        user_id=123456789,
        product_id=1,
        notification_type='back_in_stock',
        language='uz'
    )
    
    print(f"Product notification sent: {success}")


async def example_userbot_login():
    """Example: Login userbot (first time setup)"""
    print("\n=== Example: Userbot Login ===")
    
    userbot = await get_userbot()
    
    # Step 1: Send code
    result = await userbot.login(
        api_id=12345,
        api_hash="your_api_hash",
        phone="+998901234567"
    )
    print(f"Step 1: {result}")
    
    # Step 2: Enter code (uncomment when you have the code)
    # result = await userbot.login(
    #     api_id=12345,
    #     api_hash="your_api_hash",
    #     phone="+998901234567",
    #     code="12345"  # Code from Telegram
    # )
    # print(f"Step 2: {result}")


async def example_userbot_status():
    """Example: Check userbot status"""
    print("\n=== Example: Userbot Status ===")
    
    userbot = await get_userbot()
    
    print(f"Userbot active: {userbot.is_active()}")
    print(f"Userbot running: {userbot.is_running}")
    print(f"Phone: {userbot.phone}")


async def main():
    """Run all examples"""
    print("=== ZarbdorUn Notification Services Examples ===\n")
    
    # Check userbot status
    await example_userbot_status()
    
    # Uncomment to run specific examples:
    
    # await example_verification_code()
    # await example_order_notification()
    # await example_admin_notification()
    # await example_broadcast()
    # await example_welcome_message()
    # await example_product_notification()
    
    # First time setup only:
    # await example_userbot_login()
    
    print("\n=== Examples Complete ===")


if __name__ == "__main__":
    # Run examples
    asyncio.run(main())
