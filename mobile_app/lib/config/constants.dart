import 'package:flutter/material.dart';

class AppConstants {
  // API Configuration
  static const String baseUrl = 'http://localhost:8000/api/v1';
  static const String wsUrl = 'ws://localhost:8000/ws';
  
  // Colors
  static const Color primaryColor = Color(0xFFF97316);
  static const Color secondaryColor = Color(0xFF1E293B);
  static const Color backgroundColor = Color(0xFFF8FAFC);
  static const Color errorColor = Color(0xFFEF4444);
  static const Color successColor = Color(0xFF10B981);
  
  // Text Colors
  static const Color textPrimaryColor = Color(0xFF0F172A);
  static const Color textSecondaryColor = Color(0xFF64748B);
  
  // App Info
  static const String appName = 'ZarbdorUn';
  static const String appVersion = '1.0.0';
  
  // Storage Keys
  static const String keyToken = 'auth_token';
  static const String keyUserId = 'user_id';
  static const String keyLanguage = 'language';
  static const String keyCart = 'cart';
  static const String keyFavorites = 'favorites';
  
  // Languages
  static const String langUzbek = 'uz';
  static const String langRussian = 'ru';
  
  // Pagination
  static const int pageSize = 20;
  
  // Image Upload
  static const int maxImageSize = 5 * 1024 * 1024; // 5MB
  static const List<String> allowedImageTypes = ['jpg', 'jpeg', 'png'];
}
