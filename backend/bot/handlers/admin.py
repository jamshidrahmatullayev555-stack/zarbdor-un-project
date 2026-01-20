from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
import csv
import io
from datetime import datetime

import database as db
from bot.states import (
    AddProductStates, EditProductStates, AddCategoryStates,
    AddNeighborhoodStates, AddAdminStates, BroadcastStates
)
from bot.keyboards import (
    get_admin_menu_keyboard, get_main_menu_keyboard, get_categories_keyboard,
    get_products_keyboard, get_admin_product_keyboard, get_admin_order_keyboard,
    get_cancel_keyboard, get_yes_no_keyboard, get_back_keyboard,
    get_neighborhoods_keyboard, get_skip_keyboard
)
from bot.utils import (
    get_text, format_price, format_order_details, format_statistics,
    save_image, validate_number, validate_integer, format_product_details,
    get_order_status_text
)
from config import SUPER_ADMIN_ID

router = Router()

# Admin command
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Handle /admin command"""
    # Check if user is admin
    if not db.is_admin(message.from_user.id):
        user = db.get_user(message.from_user.id)
        language = user.get('language', 'uz') if user else 'uz'
        await message.answer(get_text('not_admin', language))
        return
    
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz') if user else 'uz'
    
    await message.answer(
        get_text('admin_panel', language),
        reply_markup=get_admin_menu_keyboard(language)
    )

# ============ STATISTICS ============

@router.message(F.text.in_(['📊 Statistika', '📊 Статистика']))
async def show_statistics(message: Message):
    """Show statistics"""
    if not db.is_admin(message.from_user.id):
        return
    
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    stats = db.get_statistics()
    text = format_statistics(stats, language)
    
    await message.answer(text)

# ============ ORDERS MANAGEMENT ============

@router.message(F.text.in_(['🛍 Buyurtmalar', '🛍 Заказы']))
async def show_admin_orders(message: Message):
    """Show active orders for admin"""
    if not db.is_admin(message.from_user.id):
        return
    
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    # Get pending and confirmed orders
    pending_orders = db.get_all_orders('pending')
    confirmed_orders = db.get_all_orders('confirmed')
    delivering_orders = db.get_all_orders('delivering')
    
    all_orders = pending_orders + confirmed_orders + delivering_orders
    
    if not all_orders:
        await message.answer(
            "Faol buyurtmalar yo'q" if language == 'uz' else "Нет активных заказов"
        )
        return
    
    from bot.keyboards import get_orders_keyboard
    
    text = "🛍 " + ("Faol buyurtmalar:" if language == 'uz' else "Активные заказы:")
    await message.answer(
        text,
        reply_markup=get_orders_keyboard(all_orders, language)
    )

# Admin order detail callback
@router.callback_query(F.data.startswith("order_"))
async def show_admin_order_detail(callback: CallbackQuery):
    """Show order details for admin"""
    if not db.is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return
    
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    order_id = int(callback.data.split('_')[1])
    order = db.get_order(order_id)
    
    if not order:
        await callback.answer(get_text('error', language), show_alert=True)
        return
    
    order_items = db.get_order_items(order_id)
    
    text = format_order_details(order, order_items, language)
    
    await callback.message.edit_text(
        text,
        reply_markup=get_admin_order_keyboard(order_id, language)
    )
    await callback.answer()

# Order status update callbacks
@router.callback_query(F.data.startswith("ord_confirm_"))
async def confirm_order_admin(callback: CallbackQuery):
    """Confirm order"""
    if not db.is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return
    
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    order_id = int(callback.data.split('_')[2])
    db.update_order_status(order_id, 'confirmed')
    
    # Notify customer
    order = db.get_order(order_id)
    if order:
        try:
            customer = db.get_user(order['user_id'])
            customer_lang = customer.get('language', 'uz') if customer else 'uz'
            
            await callback.message.bot.send_message(
                order['user_id'],
                f"✅ {'Buyurtmangiz tasdiqlandi!' if customer_lang == 'uz' else 'Ваш заказ подтвержден!'}\n\n🆔 #{order_id}"
            )
        except:
            pass
    
    await callback.answer(get_text('order_confirmed', language))
    
    # Refresh order details
    order_items = db.get_order_items(order_id)
    order = db.get_order(order_id)
    
    text = format_order_details(order, order_items, language)
    await callback.message.edit_text(
        text,
        reply_markup=get_admin_order_keyboard(order_id, language)
    )

@router.callback_query(F.data.startswith("ord_deliver_"))
async def set_order_delivering(callback: CallbackQuery):
    """Set order to delivering status"""
    if not db.is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return
    
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    order_id = int(callback.data.split('_')[2])
    db.update_order_status(order_id, 'delivering')
    
    # Notify customer
    order = db.get_order(order_id)
    if order:
        try:
            customer = db.get_user(order['user_id'])
            customer_lang = customer.get('language', 'uz') if customer else 'uz'
            
            await callback.message.bot.send_message(
                order['user_id'],
                f"🚚 {'Buyurtmangiz yetkazilmoqda!' if customer_lang == 'uz' else 'Ваш заказ доставляется!'}\n\n🆔 #{order_id}"
            )
        except:
            pass
    
    await callback.answer("✅")
    
    # Refresh order details
    order_items = db.get_order_items(order_id)
    order = db.get_order(order_id)
    
    text = format_order_details(order, order_items, language)
    await callback.message.edit_text(
        text,
        reply_markup=get_admin_order_keyboard(order_id, language)
    )

@router.callback_query(F.data.startswith("ord_complete_"))
async def complete_order(callback: CallbackQuery):
    """Complete order"""
    if not db.is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return
    
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    order_id = int(callback.data.split('_')[2])
    db.update_order_status(order_id, 'completed')
    
    # Notify customer
    order = db.get_order(order_id)
    if order:
        try:
            customer = db.get_user(order['user_id'])
            customer_lang = customer.get('language', 'uz') if customer else 'uz'
            
            await callback.message.bot.send_message(
                order['user_id'],
                f"✔️ {'Buyurtmangiz yakunlandi! Rahmat!' if customer_lang == 'uz' else 'Ваш заказ завершен! Спасибо!'}\n\n🆔 #{order_id}"
            )
        except:
            pass
    
    await callback.answer("✅")
    
    # Refresh order details
    order_items = db.get_order_items(order_id)
    order = db.get_order(order_id)
    
    text = format_order_details(order, order_items, language)
    await callback.message.edit_text(
        text,
        reply_markup=get_admin_order_keyboard(order_id, language)
    )

@router.callback_query(F.data.startswith("ord_cancel_"))
async def cancel_order_admin(callback: CallbackQuery):
    """Cancel order"""
    if not db.is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return
    
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    order_id = int(callback.data.split('_')[2])
    
    # Return stock
    order_items = db.get_order_items(order_id)
    for item in order_items:
        product = db.get_product(item['product_id'])
        if product:
            new_stock = product.get('stock_quantity', 0) + item['quantity']
            db.update_product(item['product_id'], stock_quantity=new_stock)
    
    db.update_order_status(order_id, 'cancelled')
    
    # Notify customer
    order = db.get_order(order_id)
    if order:
        try:
            customer = db.get_user(order['user_id'])
            customer_lang = customer.get('language', 'uz') if customer else 'uz'
            
            await callback.message.bot.send_message(
                order['user_id'],
                f"❌ {'Buyurtmangiz bekor qilindi' if customer_lang == 'uz' else 'Ваш заказ отменен'}\n\n🆔 #{order_id}"
            )
        except:
            pass
    
    await callback.answer(get_text('order_cancelled', language))
    
    # Refresh order details
    order = db.get_order(order_id)
    
    text = format_order_details(order, order_items, language)
    await callback.message.edit_text(
        text,
        reply_markup=get_admin_order_keyboard(order_id, language)
    )

# Export orders to CSV
@router.message(Command("export_orders"))
async def export_orders(message: Message):
    """Export orders to CSV"""
    if not db.is_admin(message.from_user.id):
        return
    
    orders = db.get_all_orders()
    
    if not orders:
        await message.answer("No orders to export")
        return
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        'Order ID', 'User ID', 'Full Name', 'Phone', 'Address',
        'Total Amount', 'Delivery Price', 'Payment Method', 'Status',
        'Notes', 'Created At', 'Updated At'
    ])
    
    # Data
    for order in orders:
        writer.writerow([
            order['order_id'],
            order['user_id'],
            order['full_name'],
            order['phone'],
            order['address'],
            order['total_amount'],
            order.get('delivery_price', 0),
            order.get('payment_method', 'cash'),
            order['status'],
            order.get('notes', ''),
            order['created_at'],
            order.get('updated_at', '')
        ])
    
    # Send file
    output.seek(0)
    filename = f"orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    await message.answer_document(
        document=io.BytesIO(output.getvalue().encode('utf-8')),
        filename=filename,
        caption="📊 Orders export"
    )

# ============ PRODUCTS MANAGEMENT ============

@router.message(F.text.in_(['📦 Mahsulotlar', '📦 Товары']))
async def show_admin_products(message: Message):
    """Show products management"""
    if not db.is_admin(message.from_user.id):
        return
    
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    text = "📦 " + ("Mahsulotlar boshqaruvi:" if language == 'uz' else "Управление товарами:")
    text += "\n\n/add_product - " + ("Mahsulot qo'shish" if language == 'uz' else "Добавить товар")
    text += "\n/list_products - " + ("Mahsulotlar ro'yxati" if language == 'uz' else "Список товаров")
    
    await message.answer(text)

# Add product command
@router.message(Command("add_product"))
async def start_add_product(message: Message, state: FSMContext):
    """Start adding product"""
    if not db.is_admin(message.from_user.id):
        return
    
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    categories = db.get_all_categories()
    
    if not categories:
        await message.answer(
            "Avval kategoriya yarating!" if language == 'uz' else "Сначала создайте категорию!"
        )
        return
    
    await message.answer(
        "Kategoriyani tanlang:" if language == 'uz' else "Выберите категорию:",
        reply_markup=get_categories_keyboard(categories, language)
    )
    await state.set_state(AddProductStates.waiting_for_category)

@router.callback_query(F.data.startswith("cat_"), StateFilter(AddProductStates.waiting_for_category))
async def select_product_category(callback: CallbackQuery, state: FSMContext):
    """Select category for new product"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    category_id = int(callback.data.split('_')[1])
    await state.update_data(category_id=category_id)
    
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Mahsulot nomini kiriting (O'zbekcha):" if language == 'uz' else "Введите название товара (узбекский):",
        reply_markup=get_cancel_keyboard(language)
    )
    await state.set_state(AddProductStates.waiting_for_name_uz)
    await callback.answer()

@router.message(AddProductStates.waiting_for_name_uz)
async def enter_product_name_uz(message: Message, state: FSMContext):
    """Enter product name in Uzbek"""
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    if message.text in ['❌ Bekor qilish', '❌ Отмена']:
        await state.clear()
        await message.answer(get_text('cancelled', language))
        return
    
    await state.update_data(name_uz=message.text)
    await message.answer(
        "Mahsulot nomini kiriting (Ruscha):" if language == 'uz' else "Введите название товара (русский):"
    )
    await state.set_state(AddProductStates.waiting_for_name_ru)

@router.message(AddProductStates.waiting_for_name_ru)
async def enter_product_name_ru(message: Message, state: FSMContext):
    """Enter product name in Russian"""
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    await state.update_data(name_ru=message.text)
    await message.answer(
        "Tavsif kiriting (O'zbekcha):" if language == 'uz' else "Введите описание (узбекский):"
    )
    await state.set_state(AddProductStates.waiting_for_description_uz)

@router.message(AddProductStates.waiting_for_description_uz)
async def enter_product_desc_uz(message: Message, state: FSMContext):
    """Enter product description in Uzbek"""
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    await state.update_data(description_uz=message.text)
    await message.answer(
        "Tavsif kiriting (Ruscha):" if language == 'uz' else "Введите описание (русский):"
    )
    await state.set_state(AddProductStates.waiting_for_description_ru)

@router.message(AddProductStates.waiting_for_description_ru)
async def enter_product_desc_ru(message: Message, state: FSMContext):
    """Enter product description in Russian"""
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    await state.update_data(description_ru=message.text)
    await message.answer(
        "Narxini kiriting (so'mda):" if language == 'uz' else "Введите цену (в сумах):"
    )
    await state.set_state(AddProductStates.waiting_for_price)

@router.message(AddProductStates.waiting_for_price)
async def enter_product_price(message: Message, state: FSMContext):
    """Enter product price"""
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    price = validate_number(message.text, min_val=0)
    
    if price is None:
        await message.answer(get_text('invalid_input', language))
        return
    
    await state.update_data(price=price)
    await message.answer(
        "Chegirma narxini kiriting (ixtiyoriy, 0 - chegirma yo'q):" if language == 'uz' 
        else "Введите цену со скидкой (необязательно, 0 - без скидки):",
        reply_markup=get_skip_keyboard(language)
    )
    await state.set_state(AddProductStates.waiting_for_discount_price)

@router.message(AddProductStates.waiting_for_discount_price)
async def enter_discount_price(message: Message, state: FSMContext):
    """Enter discount price"""
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    discount_price = validate_number(message.text, min_val=0)
    
    if discount_price == 0:
        discount_price = None
    
    await state.update_data(discount_price=discount_price)
    await message.answer(
        "Ombordagi miqdorini kiriting:" if language == 'uz' else "Введите количество на складе:"
    )
    await state.set_state(AddProductStates.waiting_for_stock)

@router.callback_query(F.data == "skip", StateFilter(AddProductStates.waiting_for_discount_price))
async def skip_discount_price(callback: CallbackQuery, state: FSMContext):
    """Skip discount price"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    await state.update_data(discount_price=None)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Ombordagi miqdorini kiriting:" if language == 'uz' else "Введите количество на складе:"
    )
    await state.set_state(AddProductStates.waiting_for_stock)
    await callback.answer()

@router.message(AddProductStates.waiting_for_stock)
async def enter_product_stock(message: Message, state: FSMContext):
    """Enter product stock"""
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    stock = validate_integer(message.text, min_val=0)
    
    if stock is None:
        await message.answer(get_text('invalid_input', language))
        return
    
    await state.update_data(stock_quantity=stock)
    await message.answer(
        "Mahsulot rasmini yuboring:" if language == 'uz' else "Отправьте фото товара:",
        reply_markup=get_skip_keyboard(language)
    )
    await state.set_state(AddProductStates.waiting_for_image)

@router.message(AddProductStates.waiting_for_image, F.photo)
async def save_product_image(message: Message, state: FSMContext):
    """Save product image and create product"""
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    # Get largest photo
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    file_bytes = await message.bot.download_file(file.file_path)
    
    # Save image
    image_path = await save_image(file_bytes.read(), f"{photo.file_id}.jpg")
    
    # Get data and create product
    data = await state.get_data()
    
    product_id = db.create_product(
        category_id=data['category_id'],
        name_uz=data['name_uz'],
        name_ru=data['name_ru'],
        price=data['price'],
        description_uz=data.get('description_uz'),
        description_ru=data.get('description_ru'),
        discount_price=data.get('discount_price'),
        stock_quantity=data['stock_quantity'],
        image_path=image_path
    )
    
    await message.answer(
        f"✅ {'Mahsulot qo\'shildi!' if language == 'uz' else 'Товар добавлен!'}\n\n🆔 #{product_id}",
        reply_markup=get_admin_menu_keyboard(language)
    )
    await state.clear()

@router.callback_query(F.data == "skip", StateFilter(AddProductStates.waiting_for_image))
async def skip_product_image(callback: CallbackQuery, state: FSMContext):
    """Skip product image"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    # Get data and create product
    data = await state.get_data()
    
    product_id = db.create_product(
        category_id=data['category_id'],
        name_uz=data['name_uz'],
        name_ru=data['name_ru'],
        price=data['price'],
        description_uz=data.get('description_uz'),
        description_ru=data.get('description_ru'),
        discount_price=data.get('discount_price'),
        stock_quantity=data['stock_quantity']
    )
    
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        f"✅ {'Mahsulot qo\'shildi!' if language == 'uz' else 'Товар добавлен!'}\n\n🆔 #{product_id}",
        reply_markup=get_admin_menu_keyboard(language)
    )
    await state.clear()
    await callback.answer()

# List products command
@router.message(Command("list_products"))
async def list_products(message: Message):
    """List all products"""
    if not db.is_admin(message.from_user.id):
        return
    
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    products = db.get_all_products(active_only=False)
    
    if not products:
        await message.answer("No products found")
        return
    
    await message.answer(
        "Mahsulotlar ro'yxati:" if language == 'uz' else "Список товаров:",
        reply_markup=get_products_keyboard(products, language)
    )

# ============ CATEGORIES MANAGEMENT ============

@router.message(F.text.in_(['📑 Kategoriyalar', '📑 Категории']))
async def show_admin_categories(message: Message):
    """Show categories management"""
    if not db.is_admin(message.from_user.id):
        return
    
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    text = "📑 " + ("Kategoriyalar boshqaruvi:" if language == 'uz' else "Управление категориями:")
    text += "\n\n/add_category - " + ("Kategoriya qo'shish" if language == 'uz' else "Добавить категорию")
    text += "\n/list_categories - " + ("Kategoriyalar ro'yxati" if language == 'uz' else "Список категорий")
    
    await message.answer(text)

# Add category command
@router.message(Command("add_category"))
async def start_add_category(message: Message, state: FSMContext):
    """Start adding category"""
    if not db.is_admin(message.from_user.id):
        return
    
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    await message.answer(
        "Kategoriya nomini kiriting (O'zbekcha):" if language == 'uz' else "Введите название категории (узбекский):",
        reply_markup=get_cancel_keyboard(language)
    )
    await state.set_state(AddCategoryStates.waiting_for_name_uz)

@router.message(AddCategoryStates.waiting_for_name_uz)
async def enter_category_name_uz(message: Message, state: FSMContext):
    """Enter category name in Uzbek"""
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    if message.text in ['❌ Bekor qilish', '❌ Отмена']:
        await state.clear()
        await message.answer(get_text('cancelled', language))
        return
    
    await state.update_data(name_uz=message.text)
    await message.answer(
        "Kategoriya nomini kiriting (Ruscha):" if language == 'uz' else "Введите название категории (русский):"
    )
    await state.set_state(AddCategoryStates.waiting_for_name_ru)

@router.message(AddCategoryStates.waiting_for_name_ru)
async def enter_category_name_ru(message: Message, state: FSMContext):
    """Enter category name in Russian and create"""
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    name_ru = message.text
    data = await state.get_data()
    
    category_id = db.create_category(
        name_uz=data['name_uz'],
        name_ru=name_ru
    )
    
    await message.answer(
        f"✅ {'Kategoriya qo\'shildi!' if language == 'uz' else 'Категория добавлена!'}\n\n🆔 #{category_id}",
        reply_markup=get_admin_menu_keyboard(language)
    )
    await state.clear()

# List categories
@router.message(Command("list_categories"))
async def list_categories(message: Message):
    """List all categories"""
    if not db.is_admin(message.from_user.id):
        return
    
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    categories = db.get_all_categories(active_only=False)
    
    if not categories:
        await message.answer("No categories found")
        return
    
    text = "📑 " + ("Kategoriyalar:" if language == 'uz' else "Категории:") + "\n\n"
    
    for cat in categories:
        status = "✅" if cat['is_active'] else "❌"
        text += f"{status} #{cat['category_id']}: {cat[f'name_{language}']}\n"
    
    await message.answer(text)

# ============ NEIGHBORHOODS MANAGEMENT ============

@router.message(F.text.in_(['🏘 Mahallalar', '🏘 Районы']))
async def show_admin_neighborhoods(message: Message):
    """Show neighborhoods management"""
    if not db.is_admin(message.from_user.id):
        return
    
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    text = "🏘 " + ("Mahallalar boshqaruvi:" if language == 'uz' else "Управление районами:")
    text += "\n\n/add_neighborhood - " + ("Mahalla qo'shish" if language == 'uz' else "Добавить район")
    text += "\n/list_neighborhoods - " + ("Mahallalar ro'yxati" if language == 'uz' else "Список районов")
    
    await message.answer(text)

# Add neighborhood
@router.message(Command("add_neighborhood"))
async def start_add_neighborhood(message: Message, state: FSMContext):
    """Start adding neighborhood"""
    if not db.is_admin(message.from_user.id):
        return
    
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    await message.answer(
        "Mahalla nomini kiriting (O'zbekcha):" if language == 'uz' else "Введите название района (узбекский):",
        reply_markup=get_cancel_keyboard(language)
    )
    await state.set_state(AddNeighborhoodStates.waiting_for_name_uz)

@router.message(AddNeighborhoodStates.waiting_for_name_uz)
async def enter_neighborhood_name_uz(message: Message, state: FSMContext):
    """Enter neighborhood name in Uzbek"""
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    if message.text in ['❌ Bekor qilish', '❌ Отмена']:
        await state.clear()
        await message.answer(get_text('cancelled', language))
        return
    
    await state.update_data(name_uz=message.text)
    await message.answer(
        "Mahalla nomini kiriting (Ruscha):" if language == 'uz' else "Введите название района (русский):"
    )
    await state.set_state(AddNeighborhoodStates.waiting_for_name_ru)

@router.message(AddNeighborhoodStates.waiting_for_name_ru)
async def enter_neighborhood_name_ru(message: Message, state: FSMContext):
    """Enter neighborhood name in Russian"""
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    await state.update_data(name_ru=message.text)
    await message.answer(
        "Yetkazib berish narxini kiriting:" if language == 'uz' else "Введите стоимость доставки:"
    )
    await state.set_state(AddNeighborhoodStates.waiting_for_delivery_price)

@router.message(AddNeighborhoodStates.waiting_for_delivery_price)
async def enter_delivery_price(message: Message, state: FSMContext):
    """Enter delivery price and create neighborhood"""
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    price = validate_number(message.text, min_val=0)
    
    if price is None:
        await message.answer(get_text('invalid_input', language))
        return
    
    data = await state.get_data()
    
    neighborhood_id = db.create_neighborhood(
        name_uz=data['name_uz'],
        name_ru=data['name_ru'],
        delivery_price=price
    )
    
    await message.answer(
        f"✅ {'Mahalla qo\'shildi!' if language == 'uz' else 'Район добавлен!'}\n\n🆔 #{neighborhood_id}",
        reply_markup=get_admin_menu_keyboard(language)
    )
    await state.clear()

# List neighborhoods
@router.message(Command("list_neighborhoods"))
async def list_neighborhoods(message: Message):
    """List all neighborhoods"""
    if not db.is_admin(message.from_user.id):
        return
    
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    neighborhoods = db.get_all_neighborhoods(active_only=False)
    
    if not neighborhoods:
        await message.answer("No neighborhoods found")
        return
    
    text = "🏘 " + ("Mahallalar:" if language == 'uz' else "Районы:") + "\n\n"
    
    for n in neighborhoods:
        status = "✅" if n['is_active'] else "❌"
        text += f"{status} #{n['neighborhood_id']}: {n[f'name_{language}']} - {format_price(n['delivery_price'])}\n"
    
    await message.answer(text)

# ============ ADMINS MANAGEMENT ============

@router.message(F.text.in_(['👨‍💼 Adminlar', '👨‍💼 Админы']))
async def show_admin_management(message: Message):
    """Show admin management (super admin only)"""
    if message.from_user.id != SUPER_ADMIN_ID:
        return
    
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    text = "👨‍💼 " + ("Adminlar boshqaruvi:" if language == 'uz' else "Управление админами:")
    text += "\n\n/add_admin - " + ("Admin qo'shish" if language == 'uz' else "Добавить админа")
    text += "\n/list_admins - " + ("Adminlar ro'yxati" if language == 'uz' else "Список админов")
    text += "\n/remove_admin - " + ("Admin o'chirish" if language == 'uz' else "Удалить админа")
    
    await message.answer(text)

# Add admin
@router.message(Command("add_admin"))
async def start_add_admin(message: Message, state: FSMContext):
    """Start adding admin (super admin only)"""
    if message.from_user.id != SUPER_ADMIN_ID:
        return
    
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    await message.answer(
        "Admin ID kiriting:" if language == 'uz' else "Введите ID администратора:",
        reply_markup=get_cancel_keyboard(language)
    )
    await state.set_state(AddAdminStates.waiting_for_admin_id)

@router.message(AddAdminStates.waiting_for_admin_id)
async def enter_admin_id(message: Message, state: FSMContext):
    """Enter admin ID"""
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    if message.text in ['❌ Bekor qilish', '❌ Отмена']:
        await state.clear()
        await message.answer(get_text('cancelled', language))
        return
    
    admin_id = validate_integer(message.text)
    
    if not admin_id:
        await message.answer(get_text('invalid_input', language))
        return
    
    # Create admin
    success = db.create_admin(admin_id)
    
    if success:
        await message.answer(
            f"✅ {'Admin qo\'shildi!' if language == 'uz' else 'Админ добавлен!'}\n\n🆔 {admin_id}",
            reply_markup=get_admin_menu_keyboard(language)
        )
    else:
        await message.answer("Error: Admin already exists")
    
    await state.clear()

# List admins
@router.message(Command("list_admins"))
async def list_admins(message: Message):
    """List all admins"""
    if message.from_user.id != SUPER_ADMIN_ID:
        return
    
    admins = db.get_all_admins()
    
    text = "👨‍💼 Admins:\n\n"
    
    for admin in admins:
        role = admin.get('role', 'admin')
        text += f"{'🔴' if role == 'super_admin' else '🔵'} {admin['admin_id']} - {admin.get('username', 'N/A')} ({role})\n"
    
    await message.answer(text)

# ============ BROADCAST ============

@router.message(F.text.in_(['📢 Xabar yuborish', '📢 Рассылка']))
async def start_broadcast(message: Message, state: FSMContext):
    """Start broadcast message"""
    if not db.is_admin(message.from_user.id):
        return
    
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    await message.answer(
        "Xabarni kiriting:" if language == 'uz' else "Введите сообщение:",
        reply_markup=get_cancel_keyboard(language)
    )
    await state.set_state(BroadcastStates.waiting_for_message)

@router.message(BroadcastStates.waiting_for_message)
async def enter_broadcast_message(message: Message, state: FSMContext):
    """Enter broadcast message"""
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    if message.text in ['❌ Bekor qilish', '❌ Отмена']:
        await state.clear()
        await message.answer(get_text('cancelled', language))
        return
    
    await state.update_data(broadcast_message=message.text)
    
    await message.answer(
        "Xabarni yuborishni tasdiqlaysizmi?" if language == 'uz' else "Подтвердить отправку сообщения?",
        reply_markup=get_yes_no_keyboard(language)
    )
    await state.set_state(BroadcastStates.waiting_for_confirmation)

@router.callback_query(F.data == "yes", StateFilter(BroadcastStates.waiting_for_confirmation))
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext):
    """Confirm and send broadcast"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    data = await state.get_data()
    broadcast_text = data['broadcast_message']
    
    users = db.get_all_users()
    
    sent = 0
    failed = 0
    
    await callback.message.edit_text("Yuborilmoqda..." if language == 'uz' else "Отправка...")
    
    for u in users:
        try:
            await callback.message.bot.send_message(u['user_id'], broadcast_text)
            sent += 1
        except:
            failed += 1
    
    await callback.message.answer(
        f"✅ Yuborildi: {sent}\n❌ Xatolik: {failed}" if language == 'uz' 
        else f"✅ Отправлено: {sent}\n❌ Ошибки: {failed}",
        reply_markup=get_admin_menu_keyboard(language)
    )
    
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "no", StateFilter(BroadcastStates.waiting_for_confirmation))
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    """Cancel broadcast"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    await state.clear()
    await callback.message.edit_text(get_text('cancelled', language))
    await callback.answer()

# ============ USERS MANAGEMENT ============

@router.message(F.text.in_(['👥 Foydalanuvchilar', '👥 Пользователи']))
async def show_users(message: Message):
    """Show users statistics"""
    if not db.is_admin(message.from_user.id):
        return
    
    user = db.get_user(message.from_user.id)
    language = user.get('language', 'uz')
    
    users = db.get_all_users()
    
    text = "👥 " + ("Foydalanuvchilar:" if language == 'uz' else "Пользователи:") + f" {len(users)}\n\n"
    text += "/export_users - " + ("Eksport qilish" if language == 'uz' else "Экспорт")
    
    await message.answer(text)

# Export users
@router.message(Command("export_users"))
async def export_users(message: Message):
    """Export users to CSV"""
    if not db.is_admin(message.from_user.id):
        return
    
    users = db.get_all_users()
    
    if not users:
        await message.answer("No users to export")
        return
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        'User ID', 'Username', 'First Name', 'Last Name', 'Phone',
        'Language', 'Registered At', 'Is Active'
    ])
    
    # Data
    for u in users:
        writer.writerow([
            u['user_id'],
            u.get('username', ''),
            u.get('first_name', ''),
            u.get('last_name', ''),
            u.get('phone', ''),
            u.get('language', 'uz'),
            u['registered_at'],
            u.get('is_active', 1)
        ])
    
    # Send file
    output.seek(0)
    filename = f"users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    await message.answer_document(
        document=io.BytesIO(output.getvalue().encode('utf-8')),
        filename=filename,
        caption="👥 Users export"
    )

# Back to admin callback
@router.callback_query(F.data == "back_admin")
async def back_to_admin(callback: CallbackQuery):
    """Go back to admin menu"""
    if not db.is_admin(callback.from_user.id):
        await callback.answer("Access denied")
        return
    
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    await callback.message.delete()
    await callback.message.answer(
        get_text('admin_panel', language),
        reply_markup=get_admin_menu_keyboard(language)
    )
    await callback.answer()

# Back to main menu from admin
@router.message(F.text.in_(['◀️ Orqaga', '◀️ Назад']))
async def back_to_main_from_admin(message: Message):
    """Go back to main menu from admin"""
    user = db.get_user(message.from_user.id)
    if not user:
        return
    
    language = user.get('language', 'uz')
    
    await message.answer(
        get_text('main_menu', language),
        reply_markup=get_main_menu_keyboard(language)
    )
