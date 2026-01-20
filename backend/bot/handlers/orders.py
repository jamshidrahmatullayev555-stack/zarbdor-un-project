from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
from bot.states import OrderStates
from bot.keyboards import (
    get_main_menu_keyboard, get_neighborhoods_keyboard, get_payment_keyboard,
    get_confirmation_keyboard, get_cancel_keyboard, get_orders_keyboard,
    get_back_keyboard
)
from bot.utils import (
    get_text, format_phone, validate_phone, calculate_cart_total,
    format_order_details, format_price, get_order_status_text
)

router = Router()

# Checkout callback
@router.callback_query(F.data == "checkout")
async def start_checkout(callback: CallbackQuery, state: FSMContext):
    """Start checkout process"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    cart_items = db.get_cart_items(callback.from_user.id)
    
    if not cart_items:
        await callback.answer(get_text('cart_empty', language), show_alert=True)
        return
    
    # Check stock for all items
    for item in cart_items:
        product = db.get_product(item['product_id'])
        if not product or product.get('stock_quantity', 0) < item['quantity']:
            await callback.answer(
                "Ba'zi mahsulotlar omborda yetarli emas!" if language == 'uz' 
                else "Некоторых товаров недостаточно на складе!",
                show_alert=True
            )
            return
    
    # Calculate total
    total = calculate_cart_total(cart_items)
    await state.update_data(cart_items=cart_items, subtotal=total)
    
    await callback.message.delete()
    await callback.message.answer(
        get_text('enter_name', language),
        reply_markup=get_cancel_keyboard(language)
    )
    await state.set_state(OrderStates.waiting_for_full_name)
    await callback.answer()

# Full name input
@router.message(OrderStates.waiting_for_full_name)
async def enter_full_name(message: Message, state: FSMContext):
    """Handle full name input"""
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
    
    full_name = message.text.strip()
    
    if len(full_name) < 3:
        await message.answer(get_text('invalid_input', language))
        return
    
    await state.update_data(full_name=full_name)
    
    # Pre-fill phone if available
    if user.get('phone'):
        await message.answer(
            f"{get_text('enter_phone', language)}\n\n📱 {user['phone']}\n\n"
            f"{'Ushbu raqamdan foydalanish uchun tasdiqlang yoki boshqa raqam kiriting' if language == 'uz' else 'Подтвердите этот номер или введите другой'}",
            reply_markup=get_cancel_keyboard(language)
        )
    else:
        await message.answer(
            get_text('enter_phone', language),
            reply_markup=get_cancel_keyboard(language)
        )
    
    await state.set_state(OrderStates.waiting_for_phone)

# Phone input
@router.message(OrderStates.waiting_for_phone)
async def enter_phone(message: Message, state: FSMContext):
    """Handle phone input"""
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
    
    phone = format_phone(message.text)
    
    if not validate_phone(phone):
        await message.answer(get_text('invalid_input', language))
        return
    
    await state.update_data(phone=phone)
    
    # Show neighborhoods
    neighborhoods = db.get_all_neighborhoods()
    
    if not neighborhoods:
        # Skip neighborhood selection
        await message.answer(
            get_text('enter_address', language),
            reply_markup=get_cancel_keyboard(language)
        )
        await state.set_state(OrderStates.waiting_for_address)
    else:
        await message.answer(
            get_text('select_neighborhood', language),
            reply_markup=get_neighborhoods_keyboard(neighborhoods, language)
        )
        await state.set_state(OrderStates.waiting_for_neighborhood)

# Neighborhood selection callback
@router.callback_query(F.data.startswith("neigh_"), StateFilter(OrderStates.waiting_for_neighborhood))
async def select_neighborhood(callback: CallbackQuery, state: FSMContext):
    """Handle neighborhood selection"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    neighborhood_id = int(callback.data.split('_')[1])
    neighborhood = db.get_neighborhood(neighborhood_id)
    
    if not neighborhood:
        await callback.answer(get_text('error', language), show_alert=True)
        return
    
    await state.update_data(
        neighborhood_id=neighborhood_id,
        delivery_price=neighborhood.get('delivery_price', 0)
    )
    
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        get_text('enter_address', language),
        reply_markup=get_cancel_keyboard(language)
    )
    await state.set_state(OrderStates.waiting_for_address)
    await callback.answer()

# Address input
@router.message(OrderStates.waiting_for_address)
async def enter_address(message: Message, state: FSMContext):
    """Handle address input"""
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
    
    # Accept text or location
    if message.location:
        address = f"📍 Lokatsiya: {message.location.latitude}, {message.location.longitude}"
    elif message.text:
        address = message.text.strip()
        
        if len(address) < 5:
            await message.answer(get_text('invalid_input', language))
            return
    else:
        await message.answer(get_text('invalid_input', language))
        return
    
    await state.update_data(address=address)
    
    # Ask for payment method
    await message.answer(
        get_text('select_payment', language),
        reply_markup=get_payment_keyboard(language)
    )
    await state.set_state(OrderStates.waiting_for_payment_method)

# Payment method selection callback
@router.callback_query(F.data.startswith("payment_"), StateFilter(OrderStates.waiting_for_payment_method))
async def select_payment_method(callback: CallbackQuery, state: FSMContext):
    """Handle payment method selection"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    payment_method = callback.data.split('_')[1]
    await state.update_data(payment_method=payment_method)
    
    await callback.message.edit_reply_markup(reply_markup=None)
    
    # Ask for notes (optional)
    notes_text = "Izoh qoldiring (ixtiyoriy):" if language == 'uz' else "Оставьте комментарий (необязательно):"
    await callback.message.answer(
        notes_text,
        reply_markup=get_cancel_keyboard(language)
    )
    await state.set_state(OrderStates.waiting_for_notes)
    await callback.answer()

# Notes input
@router.message(OrderStates.waiting_for_notes)
async def enter_notes(message: Message, state: FSMContext):
    """Handle notes input"""
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
    
    notes = message.text.strip() if message.text else None
    await state.update_data(notes=notes)
    
    # Show order confirmation
    data = await state.get_data()
    
    # Build confirmation message
    lines = [get_text('confirm_order', language), ""]
    
    # Items
    for item in data['cart_items']:
        name = item.get(f'name_{language}', item.get('name_uz', ''))
        price = item.get('discount_price') or item.get('price', 0)
        quantity = item['quantity']
        subtotal = price * quantity
        
        lines.append(f"• {name}")
        lines.append(f"  {quantity} x {format_price(price)} = {format_price(subtotal)}")
    
    lines.append("")
    lines.append(f"💰 {get_text('total', language)}: {format_price(data['subtotal'])}")
    
    if data.get('delivery_price', 0) > 0:
        lines.append(f"🚚 {get_text('delivery', language)}: {format_price(data['delivery_price'])}")
        total_with_delivery = data['subtotal'] + data['delivery_price']
        lines.append(f"💳 Итого к оплате: {format_price(total_with_delivery)}")
    
    lines.append("")
    lines.append(f"👤 {data['full_name']}")
    lines.append(f"📱 {data['phone']}")
    lines.append(f"📍 {data['address']}")
    
    payment_text = "💵 Naqd" if data['payment_method'] == 'cash' else "💳 Karta"
    if language == 'ru':
        payment_text = "💵 Наличные" if data['payment_method'] == 'cash' else "💳 Карта"
    lines.append(f"💳 {payment_text}")
    
    if notes:
        lines.append(f"📝 {notes}")
    
    await message.answer(
        '\n'.join(lines),
        reply_markup=get_confirmation_keyboard(language)
    )
    await state.set_state(OrderStates.waiting_for_confirmation)

# Order confirmation callback
@router.callback_query(F.data == "confirm_order", StateFilter(OrderStates.waiting_for_confirmation))
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    """Confirm and create order"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    data = await state.get_data()
    
    # Calculate total
    total = data['subtotal'] + data.get('delivery_price', 0)
    
    # Create order
    order_id = db.create_order(
        user_id=callback.from_user.id,
        full_name=data['full_name'],
        phone=data['phone'],
        address=data['address'],
        total_amount=total,
        neighborhood_id=data.get('neighborhood_id'),
        delivery_price=data.get('delivery_price', 0),
        payment_method=data['payment_method'],
        notes=data.get('notes')
    )
    
    # Add order items
    for item in data['cart_items']:
        price = item.get('discount_price') or item.get('price', 0)
        db.add_order_item(
            order_id=order_id,
            product_id=item['product_id'],
            quantity=item['quantity'],
            price=price
        )
        
        # Update stock
        product = db.get_product(item['product_id'])
        if product:
            new_stock = product.get('stock_quantity', 0) - item['quantity']
            db.update_product(item['product_id'], stock_quantity=new_stock)
    
    # Clear cart
    db.clear_cart(callback.from_user.id)
    
    await callback.message.edit_text(
        f"{get_text('order_placed', language)}\n\n🆔 #{order_id}"
    )
    await callback.message.answer(
        get_text('main_menu', language),
        reply_markup=get_main_menu_keyboard(language)
    )
    
    # Notify admins
    admins = db.get_all_admins()
    order = db.get_order(order_id)
    order_items = db.get_order_items(order_id)
    
    for admin in admins:
        try:
            admin_user = db.get_user(admin['admin_id'])
            admin_lang = admin_user.get('language', 'uz') if admin_user else 'uz'
            
            notification = f"🔔 {'Yangi buyurtma!' if admin_lang == 'uz' else 'Новый заказ!'}\n\n"
            notification += format_order_details(order, order_items, admin_lang)
            
            from bot.keyboards import get_admin_order_keyboard
            
            await callback.message.bot.send_message(
                admin['admin_id'],
                notification,
                reply_markup=get_admin_order_keyboard(order_id, admin_lang)
            )
        except:
            pass
    
    await state.clear()
    await callback.answer()

# Cancel order callback
@router.callback_query(F.data == "cancel_order", StateFilter(OrderStates.waiting_for_confirmation))
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    """Cancel order"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    await state.clear()
    await callback.message.edit_text(get_text('cancelled', language))
    await callback.message.answer(
        get_text('main_menu', language),
        reply_markup=get_main_menu_keyboard(language)
    )
    await callback.answer()

# Order detail callback
@router.callback_query(F.data.startswith("order_"))
async def show_order_detail(callback: CallbackQuery):
    """Show order details"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    order_id = int(callback.data.split('_')[1])
    order = db.get_order(order_id)
    
    # Check if user owns this order
    if not order or order['user_id'] != callback.from_user.id:
        await callback.answer(get_text('error', language), show_alert=True)
        return
    
    order_items = db.get_order_items(order_id)
    
    text = format_order_details(order, order_items, language)
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard(language)
    )
    await callback.answer()
