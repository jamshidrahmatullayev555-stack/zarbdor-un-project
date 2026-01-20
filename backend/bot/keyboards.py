from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from typing import List, Dict

# Main menu keyboards
def get_main_menu_keyboard(language: str = 'uz') -> ReplyKeyboardMarkup:
    """Get main menu keyboard"""
    texts = {
        'uz': {
            'catalog': '🛍 Katalog',
            'cart': '🛒 Savatcha',
            'orders': '📦 Mening buyurtmalarim',
            'favorites': '❤️ Sevimlilar',
            'settings': '⚙️ Sozlamalar',
            'support': '💬 Yordam'
        },
        'ru': {
            'catalog': '🛍 Каталог',
            'cart': '🛒 Корзина',
            'orders': '📦 Мои заказы',
            'favorites': '❤️ Избранное',
            'settings': '⚙️ Настройки',
            'support': '💬 Поддержка'
        }
    }
    
    t = texts.get(language, texts['uz'])
    builder = ReplyKeyboardBuilder()
    builder.button(text=t['catalog'])
    builder.button(text=t['cart'])
    builder.button(text=t['orders'])
    builder.button(text=t['favorites'])
    builder.button(text=t['settings'])
    builder.button(text=t['support'])
    builder.adjust(2, 2, 2)
    
    return builder.as_markup(resize_keyboard=True)

def get_admin_menu_keyboard(language: str = 'uz') -> ReplyKeyboardMarkup:
    """Get admin menu keyboard"""
    texts = {
        'uz': {
            'products': '📦 Mahsulotlar',
            'categories': '📑 Kategoriyalar',
            'orders': '🛍 Buyurtmalar',
            'users': '👥 Foydalanuvchilar',
            'neighborhoods': '🏘 Mahallalar',
            'admins': '👨‍💼 Adminlar',
            'stats': '📊 Statistika',
            'broadcast': '📢 Xabar yuborish',
            'back': '◀️ Orqaga'
        },
        'ru': {
            'products': '📦 Товары',
            'categories': '📑 Категории',
            'orders': '🛍 Заказы',
            'users': '👥 Пользователи',
            'neighborhoods': '🏘 Районы',
            'admins': '👨‍💼 Админы',
            'stats': '📊 Статистика',
            'broadcast': '📢 Рассылка',
            'back': '◀️ Назад'
        }
    }
    
    t = texts.get(language, texts['uz'])
    builder = ReplyKeyboardBuilder()
    builder.button(text=t['products'])
    builder.button(text=t['categories'])
    builder.button(text=t['orders'])
    builder.button(text=t['users'])
    builder.button(text=t['neighborhoods'])
    builder.button(text=t['admins'])
    builder.button(text=t['stats'])
    builder.button(text=t['broadcast'])
    builder.button(text=t['back'])
    builder.adjust(2, 2, 2, 2, 1)
    
    return builder.as_markup(resize_keyboard=True)

# Language selection keyboard
def get_language_keyboard() -> InlineKeyboardMarkup:
    """Get language selection keyboard"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇿 O'zbek", callback_data="lang_uz")
    builder.button(text="🇷🇺 Русский", callback_data="lang_ru")
    builder.adjust(2)
    return builder.as_markup()

# Phone number request keyboard
def get_phone_keyboard(language: str = 'uz') -> ReplyKeyboardMarkup:
    """Get phone number request keyboard"""
    texts = {
        'uz': "📱 Telefon raqamni yuborish",
        'ru': "📱 Отправить номер телефона"
    }
    text = texts.get(language, texts['uz'])
    
    builder = ReplyKeyboardBuilder()
    builder.button(text=text, request_contact=True)
    builder.adjust(1)
    
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

# Categories keyboard
def get_categories_keyboard(categories: List[Dict], language: str = 'uz') -> InlineKeyboardMarkup:
    """Get categories inline keyboard"""
    builder = InlineKeyboardBuilder()
    
    for category in categories:
        name = category[f'name_{language}']
        builder.button(text=name, callback_data=f"cat_{category['category_id']}")
    
    builder.adjust(2)
    return builder.as_markup()

# Products keyboard
def get_products_keyboard(products: List[Dict], language: str = 'uz', page: int = 0) -> InlineKeyboardMarkup:
    """Get products inline keyboard"""
    builder = InlineKeyboardBuilder()
    
    # Products per page
    per_page = 10
    start = page * per_page
    end = start + per_page
    page_products = products[start:end]
    
    for product in page_products:
        name = product[f'name_{language}']
        price = product['discount_price'] if product['discount_price'] else product['price']
        builder.button(text=f"{name} - {price:,.0f} so'm", callback_data=f"prod_{product['product_id']}")
    
    # Pagination buttons
    nav_buttons = []
    if page > 0:
        texts = {'uz': '⬅️ Orqaga', 'ru': '⬅️ Назад'}
        nav_buttons.append(InlineKeyboardButton(text=texts.get(language, texts['uz']), 
                                               callback_data=f"page_{page-1}"))
    
    if end < len(products):
        texts = {'uz': 'Keyingi ➡️', 'ru': 'Далее ➡️'}
        nav_buttons.append(InlineKeyboardButton(text=texts.get(language, texts['uz']), 
                                               callback_data=f"page_{page+1}"))
    
    builder.adjust(1)
    
    if nav_buttons:
        markup = builder.as_markup()
        markup.inline_keyboard.append(nav_buttons)
        return markup
    
    return builder.as_markup()

# Product detail keyboard
def get_product_detail_keyboard(product_id: int, language: str = 'uz', is_favorite: bool = False) -> InlineKeyboardMarkup:
    """Get product detail keyboard"""
    texts = {
        'uz': {
            'add_cart': '🛒 Savatga qo\'shish',
            'favorite': '❤️ Sevimlilarga qo\'shish',
            'unfavorite': '💔 Sevimlilardan o\'chirish',
            'back': '◀️ Orqaga'
        },
        'ru': {
            'add_cart': '🛒 Добавить в корзину',
            'favorite': '❤️ В избранное',
            'unfavorable': '💔 Убрать из избранного',
            'back': '◀️ Назад'
        }
    }
    
    t = texts.get(language, texts['uz'])
    builder = InlineKeyboardBuilder()
    
    builder.button(text=t['add_cart'], callback_data=f"add_cart_{product_id}")
    
    if is_favorite:
        builder.button(text=t['unfavorite'], callback_data=f"unfav_{product_id}")
    else:
        builder.button(text=t['favorite'], callback_data=f"fav_{product_id}")
    
    builder.button(text=t['back'], callback_data="back_to_catalog")
    
    builder.adjust(1)
    return builder.as_markup()

# Cart keyboard
def get_cart_keyboard(cart_items: List[Dict], language: str = 'uz') -> InlineKeyboardMarkup:
    """Get cart inline keyboard"""
    texts = {
        'uz': {
            'checkout': '✅ Buyurtma berish',
            'clear': '🗑 Savatni tozalash',
            'back': '◀️ Orqaga'
        },
        'ru': {
            'checkout': '✅ Оформить заказ',
            'clear': '🗑 Очистить корзину',
            'back': '◀️ Назад'
        }
    }
    
    t = texts.get(language, texts['uz'])
    builder = InlineKeyboardBuilder()
    
    for item in cart_items:
        name = item[f'name_{language}']
        qty = item['quantity']
        builder.button(text=f"{name} ({qty})", callback_data=f"cart_item_{item['cart_id']}")
    
    builder.adjust(1)
    
    if cart_items:
        builder.row(
            InlineKeyboardButton(text=t['checkout'], callback_data="checkout"),
            InlineKeyboardButton(text=t['clear'], callback_data="clear_cart")
        )
    
    builder.button(text=t['back'], callback_data="back_to_menu")
    
    return builder.as_markup()

# Cart item control keyboard
def get_cart_item_keyboard(cart_id: int, language: str = 'uz') -> InlineKeyboardMarkup:
    """Get cart item control keyboard"""
    texts = {
        'uz': {
            'increase': '➕ Ko\'paytirish',
            'decrease': '➖ Kamaytirish',
            'remove': '🗑 O\'chirish',
            'back': '◀️ Orqaga'
        },
        'ru': {
            'increase': '➕ Увеличить',
            'decrease': '➖ Уменьшить',
            'remove': '🗑 Удалить',
            'back': '◀️ Назад'
        }
    }
    
    t = texts.get(language, texts['uz'])
    builder = InlineKeyboardBuilder()
    
    builder.button(text=t['decrease'], callback_data=f"cart_dec_{cart_id}")
    builder.button(text=t['increase'], callback_data=f"cart_inc_{cart_id}")
    builder.button(text=t['remove'], callback_data=f"cart_del_{cart_id}")
    builder.button(text=t['back'], callback_data="back_to_cart")
    
    builder.adjust(2, 1, 1)
    return builder.as_markup()

# Neighborhoods keyboard
def get_neighborhoods_keyboard(neighborhoods: List[Dict], language: str = 'uz') -> InlineKeyboardMarkup:
    """Get neighborhoods keyboard"""
    builder = InlineKeyboardBuilder()
    
    for neighborhood in neighborhoods:
        name = neighborhood[f'name_{language}']
        price = neighborhood['delivery_price']
        text = f"{name} - {price:,.0f} so'm" if price > 0 else name
        builder.button(text=text, callback_data=f"neigh_{neighborhood['neighborhood_id']}")
    
    builder.adjust(1)
    return builder.as_markup()

# Payment method keyboard
def get_payment_keyboard(language: str = 'uz') -> InlineKeyboardMarkup:
    """Get payment method keyboard"""
    texts = {
        'uz': {
            'cash': '💵 Naqd pul',
            'card': '💳 Karta orqali'
        },
        'ru': {
            'cash': '💵 Наличные',
            'card': '💳 Карта'
        }
    }
    
    t = texts.get(language, texts['uz'])
    builder = InlineKeyboardBuilder()
    
    builder.button(text=t['cash'], callback_data="payment_cash")
    builder.button(text=t['card'], callback_data="payment_card")
    
    builder.adjust(2)
    return builder.as_markup()

# Order confirmation keyboard
def get_confirmation_keyboard(language: str = 'uz') -> InlineKeyboardMarkup:
    """Get order confirmation keyboard"""
    texts = {
        'uz': {
            'confirm': '✅ Tasdiqlash',
            'cancel': '❌ Bekor qilish'
        },
        'ru': {
            'confirm': '✅ Подтвердить',
            'cancel': '❌ Отменить'
        }
    }
    
    t = texts.get(language, texts['uz'])
    builder = InlineKeyboardBuilder()
    
    builder.button(text=t['confirm'], callback_data="confirm_order")
    builder.button(text=t['cancel'], callback_data="cancel_order")
    
    builder.adjust(2)
    return builder.as_markup()

# Orders list keyboard
def get_orders_keyboard(orders: List[Dict], language: str = 'uz') -> InlineKeyboardMarkup:
    """Get user orders keyboard"""
    builder = InlineKeyboardBuilder()
    
    status_emoji = {
        'pending': '⏳',
        'confirmed': '✅',
        'delivering': '🚚',
        'completed': '✔️',
        'cancelled': '❌'
    }
    
    for order in orders[:20]:  # Limit to 20 recent orders
        status = status_emoji.get(order['status'], '📦')
        text = f"{status} #{order['order_id']} - {order['total_amount']:,.0f} so'm"
        builder.button(text=text, callback_data=f"order_{order['order_id']}")
    
    builder.adjust(1)
    return builder.as_markup()

# Admin product management keyboard
def get_admin_product_keyboard(product_id: int, language: str = 'uz') -> InlineKeyboardMarkup:
    """Get admin product management keyboard"""
    texts = {
        'uz': {
            'edit': '✏️ Tahrirlash',
            'delete': '🗑 O\'chirish',
            'toggle': '🔄 Faolligini o\'zgartirish',
            'back': '◀️ Orqaga'
        },
        'ru': {
            'edit': '✏️ Редактировать',
            'delete': '🗑 Удалить',
            'toggle': '🔄 Изменить статус',
            'back': '◀️ Назад'
        }
    }
    
    t = texts.get(language, texts['uz'])
    builder = InlineKeyboardBuilder()
    
    builder.button(text=t['edit'], callback_data=f"edit_prod_{product_id}")
    builder.button(text=t['delete'], callback_data=f"del_prod_{product_id}")
    builder.button(text=t['toggle'], callback_data=f"toggle_prod_{product_id}")
    builder.button(text=t['back'], callback_data="back_admin")
    
    builder.adjust(1)
    return builder.as_markup()

# Admin order management keyboard
def get_admin_order_keyboard(order_id: int, language: str = 'uz') -> InlineKeyboardMarkup:
    """Get admin order management keyboard"""
    texts = {
        'uz': {
            'confirm': '✅ Tasdiqlash',
            'deliver': '🚚 Yetkazilmoqda',
            'complete': '✔️ Yakunlash',
            'cancel': '❌ Bekor qilish',
            'back': '◀️ Orqaga'
        },
        'ru': {
            'confirm': '✅ Подтвердить',
            'deliver': '🚚 В доставке',
            'complete': '✔️ Завершить',
            'cancel': '❌ Отменить',
            'back': '◀️ Назад'
        }
    }
    
    t = texts.get(language, texts['uz'])
    builder = InlineKeyboardBuilder()
    
    builder.button(text=t['confirm'], callback_data=f"ord_confirm_{order_id}")
    builder.button(text=t['deliver'], callback_data=f"ord_deliver_{order_id}")
    builder.button(text=t['complete'], callback_data=f"ord_complete_{order_id}")
    builder.button(text=t['cancel'], callback_data=f"ord_cancel_{order_id}")
    builder.button(text=t['back'], callback_data="back_admin")
    
    builder.adjust(2, 2, 1)
    return builder.as_markup()

# Cancel keyboard
def get_cancel_keyboard(language: str = 'uz') -> ReplyKeyboardMarkup:
    """Get cancel keyboard"""
    texts = {
        'uz': '❌ Bekor qilish',
        'ru': '❌ Отмена'
    }
    
    text = texts.get(language, texts['uz'])
    builder = ReplyKeyboardBuilder()
    builder.button(text=text)
    
    return builder.as_markup(resize_keyboard=True)

# Skip keyboard
def get_skip_keyboard(language: str = 'uz') -> InlineKeyboardMarkup:
    """Get skip button keyboard"""
    texts = {
        'uz': '⏭ O\'tkazib yuborish',
        'ru': '⏭ Пропустить'
    }
    
    text = texts.get(language, texts['uz'])
    builder = InlineKeyboardBuilder()
    builder.button(text=text, callback_data="skip")
    
    return builder.as_markup()

# Yes/No keyboard
def get_yes_no_keyboard(language: str = 'uz') -> InlineKeyboardMarkup:
    """Get yes/no keyboard"""
    texts = {
        'uz': {
            'yes': '✅ Ha',
            'no': '❌ Yo\'q'
        },
        'ru': {
            'yes': '✅ Да',
            'no': '❌ Нет'
        }
    }
    
    t = texts.get(language, texts['uz'])
    builder = InlineKeyboardBuilder()
    
    builder.button(text=t['yes'], callback_data="yes")
    builder.button(text=t['no'], callback_data="no")
    
    builder.adjust(2)
    return builder.as_markup()

# Back to menu keyboard
def get_back_keyboard(language: str = 'uz') -> InlineKeyboardMarkup:
    """Get back to menu keyboard"""
    texts = {
        'uz': '◀️ Asosiy menyuga',
        'ru': '◀️ Главное меню'
    }
    
    text = texts.get(language, texts['uz'])
    builder = InlineKeyboardBuilder()
    builder.button(text=text, callback_data="back_to_menu")
    
    return builder.as_markup()
