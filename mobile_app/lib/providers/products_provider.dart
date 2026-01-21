import 'package:flutter/foundation.dart';
import '../models/product.dart';
import '../models/category.dart';
import '../services/api_service.dart';

class ProductsProvider with ChangeNotifier {
  final ApiService _apiService;
  
  List<ProductCategory> _categories = [];
  List<Product> _products = [];
  int? _selectedCategoryId;
  String _searchQuery = '';
  bool _isLoading = false;
  bool _hasMore = true;
  int _currentPage = 1;

  ProductsProvider(this._apiService) {
    loadCategories();
    loadProducts();
  }

  List<ProductCategory> get categories => _categories;
  List<Product> get products => _products;
  int? get selectedCategoryId => _selectedCategoryId;
  String get searchQuery => _searchQuery;
  bool get isLoading => _isLoading;
  bool get hasMore => _hasMore;

  Future<void> loadCategories() async {
    try {
      final data = await _apiService.getCategories();
      _categories = data.map((json) => ProductCategory.fromJson(json)).toList();
      notifyListeners();
    } catch (e) {
      print('Error loading categories: $e');
    }
  }

  Future<void> loadProducts({bool refresh = false}) async {
    if (_isLoading) return;
    if (refresh) {
      _currentPage = 1;
      _products = [];
      _hasMore = true;
    }

    _isLoading = true;
    notifyListeners();

    try {
      final data = await _apiService.getProducts(
        categoryId: _selectedCategoryId,
        search: _searchQuery,
        page: _currentPage,
      );
      
      final newProducts = (data['items'] as List)
          .map((json) => Product.fromJson(json))
          .toList();
      
      if (refresh) {
        _products = newProducts;
      } else {
        _products.addAll(newProducts);
      }
      
      _hasMore = newProducts.length >= 20;
      _currentPage++;
    } catch (e) {
      print('Error loading products: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void setCategory(int? categoryId) {
    if (_selectedCategoryId != categoryId) {
      _selectedCategoryId = categoryId;
      loadProducts(refresh: true);
    }
  }

  void setSearchQuery(String query) {
    if (_searchQuery != query) {
      _searchQuery = query;
      loadProducts(refresh: true);
    }
  }

  Future<Product?> getProduct(int id) async {
    try {
      final data = await _apiService.getProduct(id);
      return Product.fromJson(data);
    } catch (e) {
      print('Error loading product: $e');
      return null;
    }
  }
}
