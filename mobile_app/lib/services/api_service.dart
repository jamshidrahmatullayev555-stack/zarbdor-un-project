import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/constants.dart';

class ApiService {
  late Dio _dio;
  final SharedPreferences _prefs;

  ApiService(this._prefs) {
    _dio = Dio(BaseOptions(
      baseUrl: AppConstants.baseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        final token = _prefs.getString(AppConstants.keyToken);
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (error, handler) {
        if (error.response?.statusCode == 401) {
          _prefs.remove(AppConstants.keyToken);
          _prefs.remove(AppConstants.keyUserId);
        }
        return handler.next(error);
      },
    ));
  }

  // Auth
  Future<Map<String, dynamic>> sendOtp(String phoneNumber) async {
    final response = await _dio.post('/auth/send-otp', data: {
      'phone_number': phoneNumber,
    });
    return response.data;
  }

  Future<Map<String, dynamic>> verifyOtp(String phoneNumber, String otp) async {
    final response = await _dio.post('/auth/verify-otp', data: {
      'phone_number': phoneNumber,
      'otp': otp,
    });
    return response.data;
  }

  Future<Map<String, dynamic>> getCurrentUser() async {
    final response = await _dio.get('/users/me');
    return response.data;
  }

  // Categories
  Future<List<dynamic>> getCategories() async {
    final response = await _dio.get('/categories');
    return response.data;
  }

  // Products
  Future<Map<String, dynamic>> getProducts({
    int? categoryId,
    String? search,
    int page = 1,
    int limit = 20,
  }) async {
    final response = await _dio.get('/products', queryParameters: {
      if (categoryId != null) 'category_id': categoryId,
      if (search != null && search.isNotEmpty) 'search': search,
      'page': page,
      'limit': limit,
    });
    return response.data;
  }

  Future<Map<String, dynamic>> getProduct(int id) async {
    final response = await _dio.get('/products/$id');
    return response.data;
  }

  // Orders
  Future<Map<String, dynamic>> createOrder(Map<String, dynamic> orderData) async {
    final response = await _dio.post('/orders', data: orderData);
    return response.data;
  }

  Future<List<dynamic>> getMyOrders({int page = 1, int limit = 20}) async {
    final response = await _dio.get('/orders/my', queryParameters: {
      'page': page,
      'limit': limit,
    });
    return response.data;
  }

  Future<Map<String, dynamic>> getOrder(int id) async {
    final response = await _dio.get('/orders/$id');
    return response.data;
  }

  Future<void> cancelOrder(int id) async {
    await _dio.post('/orders/$id/cancel');
  }

  // Chat
  Future<List<dynamic>> getChatMessages(int orderId) async {
    final response = await _dio.get('/chat/$orderId/messages');
    return response.data;
  }

  Future<Map<String, dynamic>> sendChatMessage(
    int orderId,
    String content, {
    String? imageUrl,
  }) async {
    final response = await _dio.post('/chat/$orderId/messages', data: {
      'content': content,
      if (imageUrl != null) 'image_url': imageUrl,
    });
    return response.data;
  }

  // Image Upload
  Future<String> uploadImage(String filePath) async {
    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(filePath),
    });
    final response = await _dio.post('/upload/image', data: formData);
    return response.data['url'];
  }

  // Neighborhoods
  Future<List<dynamic>> getNeighborhoods() async {
    final response = await _dio.get('/neighborhoods');
    return response.data;
  }
}
