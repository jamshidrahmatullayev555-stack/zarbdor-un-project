import 'package:flutter/material.dart';
import '../screens/splash_screen.dart';
import '../screens/no_internet_screen.dart';
import '../screens/auth/login_screen.dart';
import '../screens/auth/verify_screen.dart';
import '../screens/home/main_screen.dart';
import '../screens/products/product_detail_screen.dart';
import '../screens/cart/checkout_screen.dart';
import '../screens/orders/orders_screen.dart';
import '../screens/orders/order_detail_screen.dart';
import '../screens/chat/chat_screen.dart';
import '../screens/profile/language_screen.dart';

class AppRoutes {
  static const String splash = '/';
  static const String noInternet = '/no-internet';
  static const String login = '/login';
  static const String verify = '/verify';
  static const String main = '/main';
  static const String productDetail = '/product-detail';
  static const String checkout = '/checkout';
  static const String orders = '/orders';
  static const String orderDetail = '/order-detail';
  static const String chat = '/chat';
  static const String language = '/language';

  static Map<String, WidgetBuilder> get routes => {
    splash: (context) => const SplashScreen(),
    noInternet: (context) => const NoInternetScreen(),
    login: (context) => const LoginScreen(),
    verify: (context) => const VerifyScreen(),
    main: (context) => const MainScreen(),
    productDetail: (context) => const ProductDetailScreen(),
    checkout: (context) => const CheckoutScreen(),
    orders: (context) => const OrdersScreen(),
    orderDetail: (context) => const OrderDetailScreen(),
    chat: (context) => const ChatScreen(),
    language: (context) => const LanguageScreen(),
  };
}
