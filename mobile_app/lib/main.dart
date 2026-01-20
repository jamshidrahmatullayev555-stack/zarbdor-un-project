import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'config/theme.dart';
import 'config/routes.dart';
import 'services/api_service.dart';
import 'providers/auth_provider.dart';
import 'providers/language_provider.dart';
import 'providers/products_provider.dart';
import 'providers/cart_provider.dart';
import 'providers/favorites_provider.dart';
import 'providers/orders_provider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final prefs = await SharedPreferences.getInstance();
  final apiService = ApiService(prefs);

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => LanguageProvider(prefs)),
        ChangeNotifierProvider(create: (_) => AuthProvider(apiService, prefs)),
        ChangeNotifierProvider(create: (_) => ProductsProvider(apiService)),
        ChangeNotifierProvider(create: (_) => CartProvider(prefs)),
        ChangeNotifierProvider(create: (_) => FavoritesProvider(prefs)),
        ChangeNotifierProvider(create: (_) => OrdersProvider(apiService)),
      ],
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ZarbdorUn',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      initialRoute: AppRoutes.splash,
      routes: AppRoutes.routes,
    );
  }
}
