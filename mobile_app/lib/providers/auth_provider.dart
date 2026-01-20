import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';
import '../services/api_service.dart';
import '../config/constants.dart';

class AuthProvider with ChangeNotifier {
  final ApiService _apiService;
  final SharedPreferences _prefs;
  
  User? _user;
  bool _isAuthenticated = false;
  bool _isLoading = false;
  String? _error;

  AuthProvider(this._apiService, this._prefs) {
    _loadAuth();
  }

  User? get user => _user;
  bool get isAuthenticated => _isAuthenticated;
  bool get isGuest => !_isAuthenticated;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> _loadAuth() async {
    final token = _prefs.getString(AppConstants.keyToken);
    if (token != null) {
      try {
        final userData = await _apiService.getCurrentUser();
        _user = User.fromJson(userData);
        _isAuthenticated = true;
        notifyListeners();
      } catch (e) {
        await logout();
      }
    }
  }

  Future<bool> sendOtp(String phoneNumber) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await _apiService.sendOtp(phoneNumber);
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> verifyOtp(String phoneNumber, String otp) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final result = await _apiService.verifyOtp(phoneNumber, otp);
      
      await _prefs.setString(AppConstants.keyToken, result['access_token']);
      await _prefs.setInt(AppConstants.keyUserId, result['user']['id']);
      
      _user = User.fromJson(result['user']);
      _isAuthenticated = true;
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    await _prefs.remove(AppConstants.keyToken);
    await _prefs.remove(AppConstants.keyUserId);
    _user = null;
    _isAuthenticated = false;
    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
