import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/constants.dart';

class LanguageProvider with ChangeNotifier {
  final SharedPreferences _prefs;
  String _currentLanguage = AppConstants.langUzbek;

  LanguageProvider(this._prefs) {
    _loadLanguage();
  }

  String get currentLanguage => _currentLanguage;
  bool get isUzbek => _currentLanguage == AppConstants.langUzbek;
  bool get isRussian => _currentLanguage == AppConstants.langRussian;

  void _loadLanguage() {
    _currentLanguage = _prefs.getString(AppConstants.keyLanguage) ?? AppConstants.langUzbek;
  }

  Future<void> setLanguage(String lang) async {
    if (lang == AppConstants.langUzbek || lang == AppConstants.langRussian) {
      _currentLanguage = lang;
      await _prefs.setString(AppConstants.keyLanguage, lang);
      notifyListeners();
    }
  }

  String translate(Map<String, String> translations) {
    return translations[_currentLanguage] ?? translations[AppConstants.langUzbek] ?? '';
  }

  // Common translations
  Map<String, String> get appName => {
    'uz': 'ZarbdorUn',
    'ru': 'ZarbdorUn',
  };

  Map<String, String> get home => {
    'uz': 'Bosh sahifa',
    'ru': 'Главная',
  };

  Map<String, String> get favorites => {
    'uz': 'Sevimlilar',
    'ru': 'Избранное',
  };

  Map<String, String> get cart => {
    'uz': 'Savat',
    'ru': 'Корзина',
  };

  Map<String, String> get profile => {
    'uz': 'Profil',
    'ru': 'Профиль',
  };

  Map<String, String> get login => {
    'uz': 'Kirish',
    'ru': 'Войти',
  };

  Map<String, String> get logout => {
    'uz': 'Chiqish',
    'ru': 'Выйти',
  };

  Map<String, String> get continueAsGuest => {
    'uz': 'Mehmon sifatida davom etish',
    'ru': 'Продолжить как гость',
  };

  Map<String, String> get search => {
    'uz': 'Qidirish',
    'ru': 'Поиск',
  };

  Map<String, String> get addToCart => {
    'uz': 'Savatga qo\'shish',
    'ru': 'Добавить в корзину',
  };

  Map<String, String> get checkout => {
    'uz': 'Buyurtma berish',
    'ru': 'Оформить заказ',
  };

  Map<String, String> get myOrders => {
    'uz': 'Mening buyurtmalarim',
    'ru': 'Мои заказы',
  };

  Map<String, String> get language => {
    'uz': 'Til',
    'ru': 'Язык',
  };

  Map<String, String> get emptyCart => {
    'uz': 'Savat bo\'sh',
    'ru': 'Корзина пуста',
  };

  Map<String, String> get total => {
    'uz': 'Jami',
    'ru': 'Итого',
  };

  Map<String, String> get sum => {
    'uz': 'so\'m',
    'ru': 'сум',
  };

  Map<String, String> get noInternet => {
    'uz': 'Internet aloqasi yo\'q',
    'ru': 'Нет интернета',
  };

  Map<String, String> get retry => {
    'uz': 'Qayta urinish',
    'ru': 'Повторить',
  };

  Map<String, String> get phoneNumber => {
    'uz': 'Telefon raqam',
    'ru': 'Номер телефона',
  };

  Map<String, String> get verificationCode => {
    'uz': 'Tasdiqlash kodi',
    'ru': 'Код подтверждения',
  };

  Map<String, String> get verify => {
    'uz': 'Tasdiqlash',
    'ru': 'Подтвердить',
  };

  Map<String, String> get deliveryAddress => {
    'uz': 'Yetkazib berish manzili',
    'ru': 'Адрес доставки',
  };

  Map<String, String> get notes => {
    'uz': 'Izoh',
    'ru': 'Примечание',
  };

  Map<String, String> get placeOrder => {
    'uz': 'Buyurtma berish',
    'ru': 'Разместить заказ',
  };

  Map<String, String> get chat => {
    'uz': 'Chat',
    'ru': 'Чат',
  };

  Map<String, String> get sendMessage => {
    'uz': 'Xabar yuborish',
    'ru': 'Отправить сообщение',
  };
}
