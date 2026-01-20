from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from bot.states import RegistrationStates, SearchStates, SupportStates
from bot.keyboards import (
    get_main_menu_keyboard, get_language_keyboard, get_phone_keyboard,
    get_categories_keyboard, get_products_keyboard, get_product_detail_keyboard,
    get_cart_keyboard, get_cart_item_keyboard, get_back_keyboard,
    get_cancel_keyboard
)
from bot.utils import (
    get_text, format_phone, validate_phone, format_product_details,
    calculate_cart_total, format_price
)

router = Router()

# /start command
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    await state.clear()
    
    user = db.get_user(message.from_user.id)
    
    if not user:
        # New user - show language selection
        await message.answer(
            get_text('choose_language', 'uz'),
            reply_markup=get_language_keyboard()
        )
        await state.set_state(RegistrationStates.waiting_for_language)
    else:
        # Existing user - show main menu
        language = user.get('language', 'uz')
        await message.answer(
            get_text('welcome', language),
            reply_markup=get_main_menu_keyboard(language)
        )

# Language selection callback
@router.callback_query(F.data.startswith("lang_"), StateFilter(RegistrationStates.waiting_for_language))
async def select_language(callback: CallbackQuery, state: FSMContext):
    """Handle language selection"""
    language = callback.data.split('_')[1]
    await state.update_data(language=language)
    
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        get_text('send_phone', language),
        reply_markup=get_phone_keyboard(language)
    )
    await state.set_state(RegistrationStates.waiting_for_phone)
    await callback.answer()

# Phone number registration
@router.message(RegistrationStates.waiting_for_phone, F.contact)
async def register_phone(message: Message, state: FSMContext):
    """Handle phone number registration"""
    data = await state.get_data()
    language = data.get('language', 'uz')
    
    # Only accept user's own phone number
    if message.contact.user_id != message.from_user.id:
        await message.answer(
            "Iltimos, o'zingizning telefon raqamingizni yuboring!" if language == 'uz' 
            else "Пожалуйста, отправьте свой номер телефона!",
            reply_markup=get_phone_keyboard(language)
        )
        return
    
    phone = format_phone(message.contact.phone_number)
    
    if not validate_phone(phone):
        await message.answer(
            get_text('invalid_input', language),
            reply_markup=get_phone_keyboard(language)
        )
        return
    
    # Create user
    db.create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        phone=phone,
        language=language
    )
    
    await message.answer(
        get_text('registered', language),
        reply_markup=get_main_menu_keyboard(language)
    )
    await state.clear()

# Catalog handler
@router.message(F.text.in_(['🛍 Katalog', '🛍 Каталог']))
async def show_catalog(message: Message):
    """Show product categories"""
    user = db.get_user(message.from_user.id)
    if not user:
        await cmd_start(message, None)
        return
    
    language = user.get('language', 'uz')
    categories = db.get_all_categories()
    
    if not categories:
        await message.answer(get_text('no_products', language))
        return
    
    await message.answer(
        get_text('select_category', language),
        reply_markup=get_categories_keyboard(categories, language)
    )

# Category selection callback
@router.callback_query(F.data.startswith("cat_"))
async def show_category_products(callback: CallbackQuery):
    """Show products in selected category"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    category_id = int(callback.data.split('_')[1])
    products = db.get_products_by_category(category_id)
    
    if not products:
        await callback.answer(get_text('no_products', language), show_alert=True)
        return
    
    await callback.message.edit_text(
        get_text('catalog', language),
        reply_markup=get_products_keyboard(products, language)
    )
    await callback.answer()

# Product detail callback
@router.callback_query(F.data.startswith("prod_"))
async def show_product_detail(callback: CallbackQuery):
    """Show product details"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    product_id = int(callback.data.split('_')[1])
    product = db.get_product(product_id)
    
    if not product:
        await callback.answer(get_text('error', language), show_alert=True)
        return
    
    is_fav = db.is_favorite(callback.from_user.id, product_id)
    text = format_product_details(product, language)
    
    # Send product image if available
    if product.get('image_path'):
        try:
            await callback.message.delete()
            await callback.message.answer_photo(
                photo=open(product['image_path'], 'rb'),
                caption=text,
                reply_markup=get_product_detail_keyboard(product_id, language, is_fav)
            )
        except:
            await callback.message.edit_text(
                text,
                reply_markup=get_product_detail_keyboard(product_id, language, is_fav)
            )
    else:
        await callback.message.edit_text(
            text,
            reply_markup=get_product_detail_keyboard(product_id, language, is_fav)
        )
    
    await callback.answer()

# Add to cart callback
@router.callback_query(F.data.startswith("add_cart_"))
async def add_to_cart(callback: CallbackQuery):
    """Add product to cart"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    product_id = int(callback.data.split('_')[2])
    product = db.get_product(product_id)
    
    if not product:
        await callback.answer(get_text('error', language), show_alert=True)
        return
    
    # Check stock
    if product.get('stock_quantity', 0) <= 0:
        await callback.answer(
            "Omborda yo'q!" if language == 'uz' else "Нет в наличии!",
            show_alert=True
        )
        return
    
    db.add_to_cart(callback.from_user.id, product_id, 1)
    await callback.answer(get_text('product_added', language))

# Favorites handlers
@router.callback_query(F.data.startswith("fav_"))
async def add_to_favorites(callback: CallbackQuery):
    """Add product to favorites"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    product_id = int(callback.data.split('_')[1])
    db.add_to_favorites(callback.from_user.id, product_id)
    
    # Update keyboard
    product = db.get_product(product_id)
    if product:
        text = format_product_details(product, language)
        await callback.message.edit_text(
            text,
            reply_markup=get_product_detail_keyboard(product_id, language, True)
        )
    
    await callback.answer(get_text('added_to_favorites', language))

@router.callback_query(F.data.startswith("unfav_"))
async def remove_from_favorites(callback: CallbackQuery):
    """Remove product from favorites"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    product_id = int(callback.data.split('_')[1])
    db.remove_from_favorites(callback.from_user.id, product_id)
    
    # Update keyboard
    product = db.get_product(product_id)
    if product:
        text = format_product_details(product, language)
        await callback.message.edit_text(
            text,
            reply_markup=get_product_detail_keyboard(product_id, language, False)
        )
    
    await callback.answer(get_text('removed_from_favorites', language))

# Cart handler
@router.message(F.text.in_(['🛒 Savatcha', '🛒 Корзина']))
async def show_cart(message: Message):
    """Show user's cart"""
    user = db.get_user(message.from_user.id)
    if not user:
        await cmd_start(message, None)
        return
    
    language = user.get('language', 'uz')
    cart_items = db.get_cart_items(message.from_user.id)
    
    if not cart_items:
        await message.answer(get_text('cart_empty', language))
        return
    
    # Format cart message
    lines = [get_text('cart', language), ""]
    total = 0
    
    for item in cart_items:
        name = item.get(f'name_{language}', item.get('name_uz', ''))
        price = item.get('discount_price') or item.get('price', 0)
        quantity = item['quantity']
        subtotal = price * quantity
        total += subtotal
        
        lines.append(f"• {name}")
        lines.append(f"  {quantity} x {format_price(price)} = {format_price(subtotal)}")
    
    lines.append("")
    lines.append(f"💰 {get_text('total', language)}: {format_price(total)}")
    
    await message.answer(
        '\n'.join(lines),
        reply_markup=get_cart_keyboard(cart_items, language)
    )

# Cart item callback
@router.callback_query(F.data.startswith("cart_item_"))
async def show_cart_item(callback: CallbackQuery):
    """Show cart item controls"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    cart_id = int(callback.data.split('_')[2])
    
    await callback.message.edit_reply_markup(
        reply_markup=get_cart_item_keyboard(cart_id, language)
    )
    await callback.answer()

# Cart item increase
@router.callback_query(F.data.startswith("cart_inc_"))
async def increase_cart_item(callback: CallbackQuery):
    """Increase cart item quantity"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    cart_id = int(callback.data.split('_')[2])
    cart_items = db.get_cart_items(callback.from_user.id)
    
    # Find current item
    current_item = next((item for item in cart_items if item['cart_id'] == cart_id), None)
    
    if current_item:
        new_quantity = current_item['quantity'] + 1
        
        # Check stock
        product = db.get_product(current_item['product_id'])
        if product and new_quantity <= product.get('stock_quantity', 0):
            db.update_cart_quantity(cart_id, new_quantity)
            await callback.answer("✅")
        else:
            await callback.answer(
                "Omborda yetarli emas!" if language == 'uz' else "Недостаточно на складе!",
                show_alert=True
            )
    else:
        await callback.answer(get_text('error', language))

# Cart item decrease
@router.callback_query(F.data.startswith("cart_dec_"))
async def decrease_cart_item(callback: CallbackQuery):
    """Decrease cart item quantity"""
    cart_id = int(callback.data.split('_')[2])
    cart_items = db.get_cart_items(callback.from_user.id)
    
    # Find current item
    current_item = next((item for item in cart_items if item['cart_id'] == cart_id), None)
    
    if current_item:
        new_quantity = current_item['quantity'] - 1
        db.update_cart_quantity(cart_id, new_quantity)
        await callback.answer("✅")

# Cart item delete
@router.callback_query(F.data.startswith("cart_del_"))
async def delete_cart_item(callback: CallbackQuery):
    """Delete cart item"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    cart_id = int(callback.data.split('_')[2])
    db.remove_from_cart(cart_id)
    
    await callback.answer(get_text('product_removed', language))
    
    # Refresh cart
    cart_items = db.get_cart_items(callback.from_user.id)
    
    if not cart_items:
        await callback.message.edit_text(get_text('cart_empty', language))
        await callback.message.edit_reply_markup(reply_markup=None)
    else:
        await callback.message.edit_reply_markup(
            reply_markup=get_cart_keyboard(cart_items, language)
        )

# Clear cart callback
@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery):
    """Clear all cart items"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    db.clear_cart(callback.from_user.id)
    
    await callback.message.edit_text(get_text('cart_empty', language))
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()

# Back to cart callback
@router.callback_query(F.data == "back_to_cart")
async def back_to_cart(callback: CallbackQuery):
    """Go back to cart view"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    cart_items = db.get_cart_items(callback.from_user.id)
    
    await callback.message.edit_reply_markup(
        reply_markup=get_cart_keyboard(cart_items, language)
    )
    await callback.answer()

# Back to catalog callback
@router.callback_query(F.data == "back_to_catalog")
async def back_to_catalog(callback: CallbackQuery):
    """Go back to catalog"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    categories = db.get_all_categories()
    
    await callback.message.edit_text(
        get_text('select_category', language),
        reply_markup=get_categories_keyboard(categories, language)
    )
    await callback.answer()

# Back to menu callback
@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Go back to main menu"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    await callback.message.delete()
    await callback.message.answer(
        get_text('main_menu', language),
        reply_markup=get_main_menu_keyboard(language)
    )
    await callback.answer()

# My orders handler
@router.message(F.text.in_(['📦 Mening buyurtmalarim', '📦 Мои заказы']))
async def show_my_orders(message: Message):
    """Show user's orders"""
    user = db.get_user(message.from_user.id)
    if not user:
        await cmd_start(message, None)
        return
    
    language = user.get('language', 'uz')
    orders = db.get_user_orders(message.from_user.id)
    
    if not orders:
        await message.answer(get_text('no_orders', language))
        return
    
    from bot.keyboards import get_orders_keyboard
    
    await message.answer(
        get_text('my_orders', language),
        reply_markup=get_orders_keyboard(orders, language)
    )

# Favorites handler
@router.message(F.text.in_(['❤️ Sevimlilar', '❤️ Избранное']))
async def show_favorites(message: Message):
    """Show user's favorite products"""
    user = db.get_user(message.from_user.id)
    if not user:
        await cmd_start(message, None)
        return
    
    language = user.get('language', 'uz')
    favorites = db.get_user_favorites(message.from_user.id)
    
    if not favorites:
        await message.answer(get_text('favorites_empty', language))
        return
    
    await message.answer(
        get_text('favorites', language),
        reply_markup=get_products_keyboard(favorites, language)
    )

# Settings handler
@router.message(F.text.in_(['⚙️ Sozlamalar', '⚙️ Настройки']))
async def show_settings(message: Message):
    """Show settings menu"""
    user = db.get_user(message.from_user.id)
    if not user:
        await cmd_start(message, None)
        return
    
    language = user.get('language', 'uz')
    
    text = "⚙️ Sozlamalar:" if language == 'uz' else "⚙️ Настройки:"
    text += f"\n\n👤 {user['first_name'] or ''} {user['last_name'] or ''}"
    text += f"\n📱 {user['phone']}"
    text += f"\n🌐 {language.upper()}"
    
    await message.answer(text, reply_markup=get_language_keyboard())

# Change language callback
@router.callback_query(F.data.startswith("lang_"), StateFilter(None))
async def change_language(callback: CallbackQuery):
    """Change user language"""
    language = callback.data.split('_')[1]
    
    db.update_user(callback.from_user.id, language=language)
    
    await callback.message.edit_text(
        get_text('main_menu', language)
    )
    await callback.message.answer(
        "Til o'zgartirildi!" if language == 'uz' else "Язык изменен!",
        reply_markup=get_main_menu_keyboard(language)
    )
    await callback.answer()

# Support handler
@router.message(F.text.in_(['💬 Yordam', '💬 Поддержка']))
async def start_support(message: Message, state: FSMContext):
    """Start support chat"""
    user = db.get_user(message.from_user.id)
    if not user:
        await cmd_start(message, None)
        return
    
    language = user.get('language', 'uz')
    
    await message.answer(
        get_text('support', language),
        reply_markup=get_cancel_keyboard(language)
    )
    await state.set_state(SupportStates.waiting_for_message)

# Support message handler
@router.message(SupportStates.waiting_for_message)
async def handle_support_message(message: Message, state: FSMContext):
    """Handle support message"""
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    # Check for cancel
    if message.text in ['❌ Bekor qilish', '❌ Отмена']:
        await state.clear()
        await message.answer(
            get_text('cancelled', language),
            reply_markup=get_main_menu_keyboard(language)
        )
        return
    
    # Save message
    db.create_message(message.from_user.id, message.text, 'user')
    
    await message.answer(
        get_text('message_sent', language),
        reply_markup=get_main_menu_keyboard(language)
    )
    
    # Notify admins
    admins = db.get_all_admins()
    for admin in admins:
        try:
            await message.bot.send_message(
                admin['admin_id'],
                f"💬 Yangi xabar:\n\n"
                f"👤 {user['first_name']} {user.get('last_name', '')}\n"
                f"📱 {user['phone']}\n"
                f"🆔 {message.from_user.id}\n\n"
                f"💭 {message.text}"
            )
        except:
            pass
    
    await state.clear()
