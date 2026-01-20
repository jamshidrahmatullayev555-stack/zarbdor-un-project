import logging
import asyncio
from typing import Optional, List
from datetime import datetime
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from config import BOT_TOKEN, SUPER_ADMIN_ID, BROADCAST_DELAY
from database import (
    get_user, get_all_admins, get_all_users, get_order, get_order_items,
    get_product, get_userbot_settings
)
from userbot.client import get_userbot

logger = logging.getLogger(__name__)


def _get_localized_text(language: str) -> str:
    """Helper to get valid language code with fallback"""
    return language if language in ['uz', 'ru'] else 'uz'


class NotificationService:
    """Service for sending notifications via bot and userbot"""
    
    def __init__(self, bot: Optional[Bot] = None):
        """Initialize notification service with bot instance"""
        self._bot = bot
        self._userbot = None
        
    @property
    def bot(self) -> Bot:
        """Get or create bot instance"""
        if self._bot is None:
            self._bot = Bot(token=BOT_TOKEN)
        return self._bot
    
    async def get_userbot_client(self):
        """Get userbot client instance"""
        if self._userbot is None:
            self._userbot = await get_userbot()
        return self._userbot
    
    async def send_verification_code(self, phone: str, code: str) -> dict:
        """
        Send verification code via userbot or bot
        Returns dict with status and method used
        """
        try:
            # Try userbot first if available
            userbot = await self.get_userbot_client()
            
            if userbot and userbot.is_active():
                success = await userbot.send_verification_code(phone, code)
                
                if success:
                    logger.info(f"Verification code sent via userbot to {phone}")
                    return {
                        'success': True,
                        'method': 'userbot',
                        'message': 'Code sent via Telegram'
                    }
            
            # Fallback: Log code if userbot failed
            logger.warning(f"Userbot unavailable. Verification code for {phone}: {code}")
            
            # In production, you could integrate SMS gateway here
            return {
                'success': False,
                'method': 'none',
                'message': 'Userbot not available. Check server logs for code.',
                'code': code  # Only for development
            }
            
        except Exception as e:
            logger.error(f"Failed to send verification code: {e}")
            return {
                'success': False,
                'method': 'error',
                'message': str(e),
                'code': code  # Only for development
            }
    
    async def send_order_notification(self, user_id: int, order_id: int, 
                                     status: str, language: str = 'uz') -> bool:
        """Send order status update notification to user"""
        try:
            order = get_order(order_id)
            if not order:
                logger.error(f"Order {order_id} not found")
                return False
            
            # Status messages
            status_messages = {
                'uz': {
                    'pending': '⏳ Buyurtmangiz qabul qilindi va ko\'rib chiqilmoqda.',
                    'confirmed': '✅ Buyurtmangiz tasdiqlandi va tayyorlanmoqda.',
                    'preparing': '📦 Buyurtmangiz tayyorlanmoqda.',
                    'delivering': '🚚 Buyurtmangiz yetkazib berilmoqda.',
                    'completed': '✅ Buyurtmangiz yetkazib berildi. Xarid uchun rahmat!',
                    'cancelled': '❌ Buyurtmangiz bekor qilindi.'
                },
                'ru': {
                    'pending': '⏳ Ваш заказ принят и рассматривается.',
                    'confirmed': '✅ Ваш заказ подтвержден и готовится.',
                    'preparing': '📦 Ваш заказ готовится.',
                    'delivering': '🚚 Ваш заказ доставляется.',
                    'completed': '✅ Ваш заказ доставлен. Спасибо за покупку!',
                    'cancelled': '❌ Ваш заказ отменен.'
                }
            }
            
            lang = _get_localized_text(language)
            status_text = status_messages[lang].get(
                status, 
                f"{'Buyurtma holati' if lang == 'uz' else 'Статус заказа'}: {status}"
            )
            
            # Build message
            order_label = 'Buyurtma' if lang == 'uz' else 'Заказ'
            message = f"🛍 <b>{order_label} #{order_id}</b>\n\n{status_text}"
            
            # Send notification
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='HTML'
            )
            
            logger.info(f"Order notification sent to user {user_id} for order {order_id}")
            return True
            
        except TelegramForbiddenError:
            logger.warning(f"User {user_id} blocked the bot")
            return False
        except Exception as e:
            logger.error(f"Failed to send order notification: {e}")
            return False
    
    async def send_new_order_to_admins(self, order_id: int) -> int:
        """
        Send new order notification to all admins
        Returns number of admins notified
        """
        try:
            order = get_order(order_id)
            if not order:
                logger.error(f"Order {order_id} not found")
                return 0
            
            # Get order items
            items = get_order_items(order_id)
            
            # Build order details
            items_text = ""
            for idx, item in enumerate(items, 1):
                items_text += f"{idx}. {item['name_uz']} x {item['quantity']} = {item['price'] * item['quantity']:,.0f} сум\n"
            
            # Build message
            message = f"""
🆕 <b>Новый заказ #{order_id}</b>

👤 <b>Клиент:</b> {order['full_name']}
📞 <b>Телефон:</b> {order['phone']}
📍 <b>Адрес:</b> {order['address']}

📦 <b>Товары:</b>
{items_text}

💰 <b>Сумма товаров:</b> {order['total_amount'] - order['delivery_price']:,.0f} сум
🚚 <b>Доставка:</b> {order['delivery_price']:,.0f} сум
💳 <b>Итого:</b> {order['total_amount']:,.0f} сум
💵 <b>Оплата:</b> {"Наличные" if order['payment_method'] == 'cash' else "Карта"}

📝 <b>Примечание:</b> {order['notes'] or 'Нет'}
🕐 <b>Время:</b> {order['created_at']}
"""
            
            # Create inline keyboard for quick actions
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Подтвердить",
                        callback_data=f"admin_order_confirm_{order_id}"
                    ),
                    InlineKeyboardButton(
                        text="❌ Отменить",
                        callback_data=f"admin_order_cancel_{order_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📋 Детали заказа",
                        callback_data=f"admin_order_details_{order_id}"
                    )
                ]
            ])
            
            # Get all admins
            admins = get_all_admins()
            notified_count = 0
            
            # Send to all admins
            for admin in admins:
                try:
                    await self.bot.send_message(
                        chat_id=admin['admin_id'],
                        text=message,
                        parse_mode='HTML',
                        reply_markup=keyboard
                    )
                    notified_count += 1
                except TelegramForbiddenError:
                    logger.warning(f"Admin {admin['admin_id']} blocked the bot")
                except Exception as e:
                    logger.error(f"Failed to notify admin {admin['admin_id']}: {e}")
            
            logger.info(f"New order #{order_id} notification sent to {notified_count} admins")
            return notified_count
            
        except Exception as e:
            logger.error(f"Failed to send new order notification to admins: {e}")
            return 0
    
    async def send_admin_message(self, message: str, 
                                admin_id: Optional[int] = None) -> bool:
        """
        Send message to specific admin or super admin
        """
        try:
            target_id = admin_id or SUPER_ADMIN_ID
            
            await self.bot.send_message(
                chat_id=target_id,
                text=message,
                parse_mode='HTML'
            )
            
            logger.info(f"Admin message sent to {target_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send admin message: {e}")
            return False
    
    async def broadcast_message(self, message: str, user_ids: List[int] = None,
                              exclude_blocked: bool = True) -> dict:
        """
        Broadcast message to users
        Returns dict with statistics
        """
        try:
            # Get target users
            if user_ids:
                users = [{'user_id': uid} for uid in user_ids]
            else:
                users = get_all_users()
            
            sent_count = 0
            failed_count = 0
            blocked_count = 0
            
            for user in users:
                try:
                    await self.bot.send_message(
                        chat_id=user['user_id'],
                        text=message,
                        parse_mode='HTML'
                    )
                    sent_count += 1
                    
                    # Small delay to avoid rate limits
                    await asyncio.sleep(BROADCAST_DELAY)
                    
                except TelegramForbiddenError:
                    blocked_count += 1
                    if not exclude_blocked:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"Failed to send to user {user['user_id']}: {e}")
                    failed_count += 1
            
            result = {
                'total': len(users),
                'sent': sent_count,
                'failed': failed_count,
                'blocked': blocked_count
            }
            
            logger.info(f"Broadcast completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Broadcast failed: {e}")
            return {
                'total': 0,
                'sent': 0,
                'failed': 0,
                'blocked': 0,
                'error': str(e)
            }
    
    async def send_welcome_message(self, user_id: int, language: str = 'uz') -> bool:
        """Send welcome message to new user"""
        try:
            messages = {
                'uz': """
👋 <b>Xush kelibsiz!</b>

ZarbdorUn internet do'koniga xush kelibsiz! 

Bizning botda siz:
🛍 Mahsulotlarni ko'rishingiz
🛒 Savat orqali buyurtma berishingiz
💬 Qo'llab-quvvatlash xizmati bilan bog'lanishingiz
⭐️ Sevimli mahsulotlarni saqlashingiz mumkin

Boshlash uchun quyidagi menyudan tanlang! 👇
""",
                'ru': """
👋 <b>Добро пожаловать!</b>

Добро пожаловать в интернет-магазин ZarbdorUn! 

В нашем боте вы можете:
🛍 Просматривать товары
🛒 Оформлять заказы через корзину
💬 Связаться со службой поддержки
⭐️ Сохранять избранные товары

Выберите из меню ниже, чтобы начать! 👇
"""
            }
            
            lang = _get_localized_text(language)
            
            await self.bot.send_message(
                chat_id=user_id,
                text=messages[lang],
                parse_mode='HTML'
            )
            
            logger.info(f"Welcome message sent to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send welcome message: {e}")
            return False
    
    async def send_cart_reminder(self, user_id: int, 
                                language: str = 'uz') -> bool:
        """Send cart reminder to user"""
        try:
            messages = {
                'uz': """
🛒 <b>Sizning savatingizda mahsulotlar bor!</b>

Buyurtmani yakunlash uchun "🛒 Savat" bo'limiga o'ting.

Hurmat bilan,
ZarbdorUn jamoasi
""",
                'ru': """
🛒 <b>В вашей корзине есть товары!</b>

Чтобы завершить заказ, перейдите в раздел "🛒 Корзина".

С уважением,
Команда ZarbdorUn
"""
            }
            
            lang = _get_localized_text(language)
            
            await self.bot.send_message(
                chat_id=user_id,
                text=messages[lang],
                parse_mode='HTML'
            )
            
            logger.info(f"Cart reminder sent to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send cart reminder: {e}")
            return False
    
    async def send_product_notification(self, user_id: int, product_id: int,
                                       notification_type: str,
                                       language: str = 'uz') -> bool:
        """
        Send product-related notification
        Types: back_in_stock, price_drop, new_product
        """
        try:
            product = get_product(product_id)
            if not product:
                logger.error(f"Product {product_id} not found")
                return False
            
            lang = _get_localized_text(language)
            product_name = product[f'name_{lang}']
            
            messages = {
                'back_in_stock': {
                    'uz': f"✅ <b>{product_name}</b> yana sotuvda!\n\nNarxi: {product['price']:,.0f} сум",
                    'ru': f"✅ <b>{product_name}</b> снова в продаже!\n\nЦена: {product['price']:,.0f} сум"
                },
                'price_drop': {
                    'uz': f"🔥 <b>Chegirma!</b>\n\n{product_name}\nYangi narx: {product.get('discount_price', product['price']):,.0f} сум",
                    'ru': f"🔥 <b>Скидка!</b>\n\n{product_name}\nНовая цена: {product.get('discount_price', product['price']):,.0f} сум"
                },
                'new_product': {
                    'uz': f"🆕 <b>Yangi mahsulot!</b>\n\n{product_name}\nNarxi: {product['price']:,.0f} сум",
                    'ru': f"🆕 <b>Новый товар!</b>\n\n{product_name}\nЦена: {product['price']:,.0f} сум"
                }
            }
            
            if notification_type not in messages:
                logger.error(f"Unknown notification type: {notification_type}")
                return False
            
            message = messages[notification_type][lang]
            
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='HTML'
            )
            
            logger.info(f"Product notification sent to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send product notification: {e}")
            return False
    
    async def close(self):
        """Close bot session"""
        try:
            if self._bot:
                await self._bot.session.close()
            if self._userbot:
                await self._userbot.disconnect()
            logger.info("Notification service closed")
        except Exception as e:
            logger.error(f"Error closing notification service: {e}")


# Global notification service instance
notification_service = NotificationService()


def get_notification_service(bot: Optional[Bot] = None) -> NotificationService:
    """Get or create notification service instance"""
    global notification_service
    if bot and notification_service._bot is None:
        notification_service._bot = bot
    return notification_service
