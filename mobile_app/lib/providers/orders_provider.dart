import 'package:flutter/foundation.dart';
import '../models/order.dart';
import '../services/api_service.dart';

class OrdersProvider with ChangeNotifier {
  final ApiService _apiService;
  
  List<Order> _orders = [];
  bool _isLoading = false;
  String? _error;

  OrdersProvider(this._apiService);

  List<Order> get orders => _orders;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadOrders() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final data = await _apiService.getMyOrders();
      _orders = data.map((json) => Order.fromJson(json)).toList();
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<Order?> getOrder(int id) async {
    try {
      final data = await _apiService.getOrder(id);
      return Order.fromJson(data);
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return null;
    }
  }

  Future<Order?> createOrder({
    required List<Map<String, dynamic>> items,
    required String deliveryAddress,
    double? deliveryLat,
    double? deliveryLon,
    String? notes,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final data = await _apiService.createOrder({
        'items': items,
        'delivery_address': deliveryAddress,
        if (deliveryLat != null) 'delivery_lat': deliveryLat,
        if (deliveryLon != null) 'delivery_lon': deliveryLon,
        if (notes != null && notes.isNotEmpty) 'notes': notes,
      });
      
      final order = Order.fromJson(data);
      _orders.insert(0, order);
      _isLoading = false;
      notifyListeners();
      return order;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return null;
    }
  }

  Future<bool> cancelOrder(int id) async {
    try {
      await _apiService.cancelOrder(id);
      final index = _orders.indexWhere((order) => order.id == id);
      if (index >= 0) {
        _orders[index] = Order(
          id: _orders[index].id,
          customerId: _orders[index].customerId,
          status: 'cancelled',
          totalAmount: _orders[index].totalAmount,
          notes: _orders[index].notes,
          deliveryAddress: _orders[index].deliveryAddress,
          deliveryLat: _orders[index].deliveryLat,
          deliveryLon: _orders[index].deliveryLon,
          courierId: _orders[index].courierId,
          courierName: _orders[index].courierName,
          items: _orders[index].items,
          createdAt: _orders[index].createdAt,
          deliveredAt: _orders[index].deliveredAt,
        );
        notifyListeners();
      }
      return true;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }
}
