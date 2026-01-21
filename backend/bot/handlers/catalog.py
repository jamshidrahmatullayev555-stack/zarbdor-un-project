"""
Product Catalog Handlers
Handles product browsing, category navigation, and product details
"""

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
from bot.states import CatalogStates
from bot.keyboards import (
    get_categories_keyboard, 
    get_products_keyboard, 
    get_product_detail_keyboard,
    get_back_keyboard
)
from bot.utils import get_text, format_product_details, format_price

router = Router()


# View categories
@router.message(F.text.in_(['📦 Mahsulotlar', '📦 Товары']))
async def show_categories(message: Message, state: FSMContext):
    """Show product categories"""
    user = db.get_user(message.from_user.id)
    if not user:
        await message.answer(get_text('not_registered', 'uz'))
        return
    
    language = user.get('language', 'uz')
    categories = db.get_active_categories()
    
    if not categories:
        await message.answer(
            get_text('no_categories', language),
            reply_markup=get_back_keyboard(language)
        )
        return
    
    await message.answer(
        get_text('select_category', language),
        reply_markup=get_categories_keyboard(categories, language)
    )
    await state.set_state(CatalogStates.browsing_categories)


# Category selection
@router.callback_query(F.data.startswith("cat_"), StateFilter(CatalogStates.browsing_categories))
async def select_category(callback: CallbackQuery, state: FSMContext):
    """Handle category selection"""
    category_id = int(callback.data.split('_')[1])
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    category = db.get_category(category_id)
    if not category or not category.get('is_active'):
        await callback.answer(get_text('category_not_available', language), show_alert=True)
        return
    
    products = db.get_products_by_category(category_id)
    
    if not products:
        await callback.answer(get_text('no_products_in_category', language), show_alert=True)
        return
    
    await state.update_data(category_id=category_id)
    await callback.message.edit_text(
        get_text('select_product', language),
        reply_markup=get_products_keyboard(products, language)
    )
    await state.set_state(CatalogStates.browsing_products)
    await callback.answer()


# Product selection
@router.callback_query(F.data.startswith("prod_"), StateFilter(CatalogStates.browsing_products))
async def select_product(callback: CallbackQuery, state: FSMContext):
    """Handle product selection - show product details"""
    product_id = int(callback.data.split('_')[1])
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    product = db.get_product(product_id)
    if not product or not product.get('is_active'):
        await callback.answer(get_text('product_not_available', language), show_alert=True)
        return
    
    product_text = format_product_details(product, language)
    
    await callback.message.edit_text(
        product_text,
        reply_markup=get_product_detail_keyboard(product_id, language),
        parse_mode='HTML'
    )
    await state.update_data(product_id=product_id)
    await state.set_state(CatalogStates.viewing_product)
    await callback.answer()


# Add to cart
@router.callback_query(F.data.startswith("add_cart_"), StateFilter(CatalogStates.viewing_product))
async def add_to_cart(callback: CallbackQuery, state: FSMContext):
    """Add product to cart"""
    product_id = int(callback.data.split('_')[2])
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    product = db.get_product(product_id)
    if not product or not product.get('is_active'):
        await callback.answer(get_text('product_not_available', language), show_alert=True)
        return
    
    # Check stock
    if product.get('stock', 0) < 1:
        await callback.answer(get_text('product_out_of_stock', language), show_alert=True)
        return
    
    # Add to cart
    success = db.add_to_cart(callback.from_user.id, product_id, 1)
    
    if success:
        await callback.answer(
            get_text('added_to_cart', language).format(product_name=product['name'].get(language, '')),
            show_alert=True
        )
    else:
        await callback.answer(get_text('error_adding_to_cart', language), show_alert=True)


# Back to categories
@router.callback_query(F.data == "back_to_categories", StateFilter(CatalogStates.browsing_products, CatalogStates.viewing_product))
async def back_to_categories(callback: CallbackQuery, state: FSMContext):
    """Go back to categories list"""
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    categories = db.get_active_categories()
    await callback.message.edit_text(
        get_text('select_category', language),
        reply_markup=get_categories_keyboard(categories, language)
    )
    await state.set_state(CatalogStates.browsing_categories)
    await callback.answer()


# Back to products
@router.callback_query(F.data == "back_to_products", StateFilter(CatalogStates.viewing_product))
async def back_to_products(callback: CallbackQuery, state: FSMContext):
    """Go back to products list"""
    data = await state.get_data()
    category_id = data.get('category_id')
    
    user = db.get_user(callback.from_user.id)
    language = user.get('language', 'uz')
    
    products = db.get_products_by_category(category_id)
    await callback.message.edit_text(
        get_text('select_product', language),
        reply_markup=get_products_keyboard(products, language)
    )
    await state.set_state(CatalogStates.browsing_products)
    await callback.answer()
