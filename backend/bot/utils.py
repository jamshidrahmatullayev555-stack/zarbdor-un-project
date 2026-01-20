import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import os
from PIL import Image
import io
from config import CODE_LENGTH, TIMEZONE_OFFSET, UPLOAD_DIR, MAX_FILE_SIZE

# Text translations
TEXTS = {
    'uz': {
        'welcome': "Xush kelibsiz! ZarbdorUn onlayn do'koniga!",
        'choose_language': "Tilni tanlang / Выберите язык:",
        'send_phone': "Telefon raqamingizni yuboring:",
        'send_code': "Tasdiqlash kodini kiriting:",
        'invalid_code': "Noto'g'ri kod. Qaytadan kiriting:",
        'registered': "Muvaffaqiyatli ro'yxatdan o'tdingiz!",
        'main_menu': "Asosiy menyu:",
        'catalog': "Katalog:",
        'cart_empty': "Savatingiz bo'sh",
        'cart': "Savatingiz:",
        'total': "Jami:",
        'delivery': "Yetkazib berish:",
        'order_placed': "Buyurtmangiz qabul qilindi! Tez orada siz bilan bog'lanamiz.",
        'product_added': "Mahsulot savatga qo'shildi",
        'product_removed': "Mahsulot o'chirildi",
        'no_products': "Mahsulotlar topilmadi",
        'select_category': "Kategoriyani tanlang:",
        'product_details': "Mahsulot ma'lumotlari:",
        'price': "Narxi:",
        'discount': "Chegirma:",
        'stock': "Omborda:",
        'description': "Tavsif:",
        'enter_quantity': "Miqdorini kiriting:",
        'enter_name': "Ismingizni kiriting:",
        'enter_phone': "Telefon raqamingizni kiriting:",
        'enter_address': "Manzilingizni kiriting:",
        'select_neighborhood': "Mahallangizni tanlang:",
        'select_payment': "To'lov turini tanlang:",
        'confirm_order': "Buyurtmani tasdiqlaysizmi?",
        'order_details': "Buyurtma tafsilotlari:",
        'order_confirmed': "Buyurtma tasdiqlandi",
        'order_cancelled': "Buyurtma bekor qilindi",
        'favorites': "Sevimli mahsulotlar:",
        'favorites_empty': "Sevimlilar bo'sh",
        'added_to_favorites': "Sevimlilarga qo'shildi",
        'removed_from_favorites': "Sevimlilardan o'chirildi",
        'my_orders': "Mening buyurtmalarim:",
        'no_orders': "Buyurtmalar topilmadi",
        'support': "Yordam xizmati. Savolingizni yozing:",
        'message_sent': "Xabar yuborildi",
        'admin_panel': "Admin panel:",
        'not_admin': "Sizda admin huquqi yo'q",
        'stats': "Statistika:",
        'total_users': "Jami foydalanuvchilar:",
        'total_products': "Jami mahsulotlar:",
        'total_orders': "Jami buyurtmalar:",
        'pending_orders': "Kutilayotgan buyurtmalar:",
        'total_revenue': "Umumiy daromad:",
        'error': "Xatolik yuz berdi. Qaytadan urinib ko'ring.",
        'cancelled': "Bekor qilindi",
        'invalid_input': "Noto'g'ri ma'lumot. Qaytadan kiriting:",
    },
    'ru': {
        'welcome': "Добро пожаловать в интернет-магазин ZarbdorUn!",
        'choose_language': "Tilni tanlang / Выберите язык:",
        'send_phone': "Отправьте номер телефона:",
        'send_code': "Введите код подтверждения:",
        'invalid_code': "Неверный код. Попробуйте еще раз:",
        'registered': "Вы успешно зарегистрированы!",
        'main_menu': "Главное меню:",
        'catalog': "Каталог:",
        'cart_empty': "Ваша корзина пуста",
        'cart': "Ваша корзина:",
        'total': "Итого:",
        'delivery': "Доставка:",
        'order_placed': "Ваш заказ принят! Мы свяжемся с вами в ближайшее время.",
        'product_added': "Товар добавлен в корзину",
        'product_removed': "Товар удален",
        'no_products': "Товары не найдены",
        'select_category': "Выберите категорию:",
        'product_details': "Информация о товаре:",
        'price': "Цена:",
        'discount': "Скидка:",
        'stock': "В наличии:",
        'description': "Описание:",
        'enter_quantity': "Введите количество:",
        'enter_name': "Введите ваше имя:",
        'enter_phone': "Введите номер телефона:",
        'enter_address': "Введите адрес:",
        'select_neighborhood': "Выберите район:",
        'select_payment': "Выберите способ оплаты:",
        'confirm_order': "Подтвердить заказ?",
        'order_details': "Детали заказа:",
        'order_confirmed': "Заказ подтвержден",
        'order_cancelled': "Заказ отменен",
        'favorites': "Избранные товары:",
        'favorites_empty': "Избранное пусто",
        'added_to_favorites': "Добавлено в избранное",
        'removed_from_favorites': "Удалено из избранного",
        'my_orders': "Мои заказы:",
        'no_orders': "Заказы не найдены",
        'support': "Служба поддержки. Напишите ваш вопрос:",
        'message_sent': "Сообщение отправлено",
        'admin_panel': "Панель администратора:",
        'not_admin': "У вас нет прав администратора",
        'stats': "Статистика:",
        'total_users': "Всего пользователей:",
        'total_products': "Всего товаров:",
        'total_orders': "Всего заказов:",
        'pending_orders': "Ожидающих заказов:",
        'total_revenue': "Общий доход:",
        'error': "Произошла ошибка. Попробуйте еще раз.",
        'cancelled': "Отменено",
        'invalid_input': "Неверный ввод. Попробуйте еще раз:",
    }
}

def get_text(key: str, language: str = 'uz') -> str:
    """Get translated text"""
    return TEXTS.get(language, TEXTS['uz']).get(key, key)

def generate_code(length: int = CODE_LENGTH) -> str:
    """Generate random verification code"""
    return ''.join(random.choices(string.digits, k=length))

def format_phone(phone: str) -> str:
    """Format phone number to standard format"""
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    # Add +998 if not present
    if not digits.startswith('998'):
        digits = '998' + digits
    
    return '+' + digits

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    formatted = format_phone(phone)
    return len(formatted) == 13 and formatted.startswith('+998')

def format_price(price: float) -> str:
    """Format price with thousand separators"""
    return f"{price:,.0f} so'm"

def format_datetime(dt: str, offset_hours: int = TIMEZONE_OFFSET) -> str:
    """Format datetime string with timezone offset"""
    try:
        if isinstance(dt, str):
            dt_obj = datetime.fromisoformat(dt)
        else:
            dt_obj = dt
        
        # Apply timezone offset
        local_dt = dt_obj + timedelta(hours=offset_hours)
        
        return local_dt.strftime("%d.%m.%Y %H:%M")
    except:
        return str(dt)

def calculate_cart_total(cart_items: List[Dict]) -> float:
    """Calculate total price of cart items"""
    total = 0.0
    for item in cart_items:
        price = item.get('discount_price') or item.get('price', 0)
        quantity = item.get('quantity', 1)
        total += price * quantity
    
    return total

def format_order_details(order: Dict, items: List[Dict], language: str = 'uz') -> str:
    """Format order details for display"""
    lines = []
    lines.append(f"🆔 {get_text('order_details', language)} #{order['order_id']}")
    lines.append("")
    
    # Order items
    for item in items:
        name = item.get(f'name_{language}', item.get('name_uz', ''))
        quantity = item['quantity']
        price = item['price']
        total = price * quantity
        lines.append(f"• {name}")
        lines.append(f"  {quantity} x {format_price(price)} = {format_price(total)}")
    
    lines.append("")
    lines.append(f"💰 {get_text('total', language)}: {format_price(order['total_amount'])}")
    
    if order.get('delivery_price', 0) > 0:
        lines.append(f"🚚 {get_text('delivery', language)}: {format_price(order['delivery_price'])}")
    
    lines.append("")
    lines.append(f"👤 {order['full_name']}")
    lines.append(f"📱 {order['phone']}")
    lines.append(f"📍 {order['address']}")
    
    if order.get('notes'):
        lines.append(f"📝 {order['notes']}")
    
    lines.append("")
    lines.append(f"📅 {format_datetime(order['created_at'])}")
    
    status_emoji = {
        'pending': '⏳',
        'confirmed': '✅',
        'delivering': '🚚',
        'completed': '✔️',
        'cancelled': '❌'
    }
    status = order['status']
    emoji = status_emoji.get(status, '📦')
    lines.append(f"{emoji} Status: {status}")
    
    return '\n'.join(lines)

def format_product_details(product: Dict, language: str = 'uz') -> str:
    """Format product details for display"""
    lines = []
    
    name = product.get(f'name_{language}', product.get('name_uz', ''))
    description = product.get(f'description_{language}', product.get('description_uz', ''))
    
    lines.append(f"📦 {name}")
    lines.append("")
    
    if description:
        lines.append(f"📝 {get_text('description', language)}:")
        lines.append(description)
        lines.append("")
    
    price = product['price']
    discount_price = product.get('discount_price')
    
    if discount_price and discount_price < price:
        lines.append(f"💰 {get_text('price', language)}: ~~{format_price(price)}~~")
        lines.append(f"🏷 {get_text('discount', language)}: {format_price(discount_price)}")
        lines.append(f"💵 {format_price(price - discount_price)} tejash!")
    else:
        lines.append(f"💰 {get_text('price', language)}: {format_price(price)}")
    
    lines.append("")
    
    stock = product.get('stock_quantity', 0)
    if stock > 0:
        lines.append(f"✅ {get_text('stock', language)}: {stock}")
    else:
        lines.append(f"❌ Omborda yo'q" if language == 'uz' else "❌ Нет в наличии")
    
    return '\n'.join(lines)

async def save_image(file_content: bytes, filename: str) -> Optional[str]:
    """Save uploaded image and return path"""
    try:
        # Create uploads directory if not exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Check file size
        if len(file_content) > MAX_FILE_SIZE:
            return None
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = os.path.splitext(filename)[1] or '.jpg'
        new_filename = f"{timestamp}_{random.randint(1000, 9999)}{ext}"
        filepath = os.path.join(UPLOAD_DIR, new_filename)
        
        # Open and resize image
        image = Image.open(io.BytesIO(file_content))
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        # Resize if too large
        max_size = (1200, 1200)
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save image
        image.save(filepath, quality=85, optimize=True)
        
        return filepath
    
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

def validate_number(text: str, min_val: float = 0, max_val: float = None) -> Optional[float]:
    """Validate and parse number input"""
    try:
        value = float(text.replace(',', '').replace(' ', ''))
        
        if value < min_val:
            return None
        
        if max_val is not None and value > max_val:
            return None
        
        return value
    except:
        return None

def validate_integer(text: str, min_val: int = 0, max_val: int = None) -> Optional[int]:
    """Validate and parse integer input"""
    try:
        value = int(text.replace(',', '').replace(' ', ''))
        
        if value < min_val:
            return None
        
        if max_val is not None and value > max_val:
            return None
        
        return value
    except:
        return None

def escape_markdown(text: str) -> str:
    """Escape markdown special characters"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split list into chunks"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def get_order_status_text(status: str, language: str = 'uz') -> str:
    """Get order status text"""
    statuses = {
        'uz': {
            'pending': '⏳ Kutilmoqda',
            'confirmed': '✅ Tasdiqlandi',
            'delivering': '🚚 Yetkazilmoqda',
            'completed': '✔️ Yakunlandi',
            'cancelled': '❌ Bekor qilindi'
        },
        'ru': {
            'pending': '⏳ Ожидание',
            'confirmed': '✅ Подтвержден',
            'delivering': '🚚 Доставляется',
            'completed': '✔️ Завершен',
            'cancelled': '❌ Отменен'
        }
    }
    
    return statuses.get(language, statuses['uz']).get(status, status)

def format_statistics(stats: Dict, language: str = 'uz') -> str:
    """Format statistics for display"""
    lines = []
    lines.append(f"📊 {get_text('stats', language)}")
    lines.append("")
    lines.append(f"👥 {get_text('total_users', language)} {stats['total_users']}")
    lines.append(f"📦 {get_text('total_products', language)} {stats['total_products']}")
    lines.append(f"🛍 {get_text('total_orders', language)} {stats['total_orders']}")
    lines.append(f"⏳ {get_text('pending_orders', language)} {stats['pending_orders']}")
    lines.append(f"💰 {get_text('total_revenue', language)} {format_price(stats['total_revenue'])}")
    
    return '\n'.join(lines)

def is_valid_image(file_content: bytes) -> bool:
    """Check if file is a valid image"""
    try:
        image = Image.open(io.BytesIO(file_content))
        image.verify()
        return True
    except:
        return False
