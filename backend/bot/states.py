from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    """User registration states"""
    waiting_for_phone = State()
    waiting_for_verification_code = State()
    waiting_for_language = State()

class AddProductStates(StatesGroup):
    """Add product states for admin"""
    waiting_for_category = State()
    waiting_for_name_uz = State()
    waiting_for_name_ru = State()
    waiting_for_description_uz = State()
    waiting_for_description_ru = State()
    waiting_for_price = State()
    waiting_for_discount_price = State()
    waiting_for_stock = State()
    waiting_for_image = State()

class EditProductStates(StatesGroup):
    """Edit product states"""
    waiting_for_product_selection = State()
    waiting_for_field_selection = State()
    waiting_for_new_value = State()

class AddCategoryStates(StatesGroup):
    """Add category states"""
    waiting_for_name_uz = State()
    waiting_for_name_ru = State()
    waiting_for_description_uz = State()
    waiting_for_description_ru = State()

class AddNeighborhoodStates(StatesGroup):
    """Add neighborhood states"""
    waiting_for_name_uz = State()
    waiting_for_name_ru = State()
    waiting_for_delivery_price = State()

class OrderStates(StatesGroup):
    """Order placement states"""
    waiting_for_full_name = State()
    waiting_for_phone = State()
    waiting_for_neighborhood = State()
    waiting_for_address = State()
    waiting_for_payment_method = State()
    waiting_for_notes = State()
    waiting_for_confirmation = State()

class AddAdminStates(StatesGroup):
    """Add admin states"""
    waiting_for_admin_id = State()
    waiting_for_role = State()

class BroadcastStates(StatesGroup):
    """Broadcast message states"""
    waiting_for_message = State()
    waiting_for_confirmation = State()

class SupportStates(StatesGroup):
    """Customer support chat states"""
    in_chat = State()
    waiting_for_message = State()

class SearchStates(StatesGroup):
    """Product search states"""
    waiting_for_query = State()

class CatalogStates(StatesGroup):
    """Product catalog browsing states"""
    browsing_categories = State()
    browsing_products = State()
    viewing_product = State()

class UserbotStates(StatesGroup):
    """Userbot configuration states"""
    waiting_for_api_id = State()
    waiting_for_api_hash = State()
    waiting_for_phone = State()
    waiting_for_code = State()
