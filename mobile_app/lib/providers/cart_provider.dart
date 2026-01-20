import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/cart_item.dart';
import '../models/product.dart';
import '../config/constants.dart';

class CartProvider with ChangeNotifier {
  final SharedPreferences _prefs;
  final List<CartItem> _items = [];

  CartProvider(this._prefs) {
    _loadCart();
  }

  List<CartItem> get items => _items;
  int get itemCount => _items.fold(0, (sum, item) => sum + item.quantity);
  bool get isEmpty => _items.isEmpty;

  double get totalAmount {
    return _items.fold(0.0, (sum, item) => sum + item.totalPrice);
  }

  void _loadCart() {
    final cartData = _prefs.getString(AppConstants.keyCart);
    if (cartData != null) {
      try {
        final List<dynamic> decoded = jsonDecode(cartData);
        _items.clear();
        _items.addAll(decoded.map((json) => CartItem.fromJson(json)));
        notifyListeners();
      } catch (e) {
        print('Error loading cart: $e');
      }
    }
  }

  Future<void> _saveCart() async {
    final encoded = jsonEncode(_items.map((item) => item.toJson()).toList());
    await _prefs.setString(AppConstants.keyCart, encoded);
  }

  void addItem(Product product, {int quantity = 1}) {
    final existingIndex = _items.indexWhere((item) => item.product.id == product.id);
    
    if (existingIndex >= 0) {
      final newQuantity = _items[existingIndex].quantity + quantity;
      if (newQuantity <= product.stock) {
        _items[existingIndex].quantity = newQuantity;
      }
    } else {
      if (quantity <= product.stock) {
        _items.add(CartItem(product: product, quantity: quantity));
      }
    }
    
    _saveCart();
    notifyListeners();
  }

  void updateQuantity(int productId, int quantity) {
    final index = _items.indexWhere((item) => item.product.id == productId);
    if (index >= 0) {
      if (quantity <= 0) {
        _items.removeAt(index);
      } else if (quantity <= _items[index].product.stock) {
        _items[index].quantity = quantity;
      }
      _saveCart();
      notifyListeners();
    }
  }

  void removeItem(int productId) {
    _items.removeWhere((item) => item.product.id == productId);
    _saveCart();
    notifyListeners();
  }

  void clear() {
    _items.clear();
    _saveCart();
    notifyListeners();
  }

  bool isInCart(int productId) {
    return _items.any((item) => item.product.id == productId);
  }

  int getQuantity(int productId) {
    final item = _items.firstWhere(
      (item) => item.product.id == productId,
      orElse: () => CartItem(product: Product(
        id: 0,
        name: {},
        description: {},
        price: 0,
        stock: 0,
        imageUrls: [],
        categoryId: 0,
        sellerId: 0,
        isActive: false,
        createdAt: DateTime.now(),
      ), quantity: 0),
    );
    return item.quantity;
  }
}
