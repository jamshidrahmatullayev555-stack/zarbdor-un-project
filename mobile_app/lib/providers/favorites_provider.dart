import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/constants.dart';

class FavoritesProvider with ChangeNotifier {
  final SharedPreferences _prefs;
  final Set<int> _favoriteIds = {};

  FavoritesProvider(this._prefs) {
    _loadFavorites();
  }

  Set<int> get favoriteIds => _favoriteIds;
  bool isEmpty => _favoriteIds.isEmpty;
  int get count => _favoriteIds.length;

  void _loadFavorites() {
    final favoritesData = _prefs.getString(AppConstants.keyFavorites);
    if (favoritesData != null) {
      try {
        final List<dynamic> decoded = jsonDecode(favoritesData);
        _favoriteIds.clear();
        _favoriteIds.addAll(decoded.cast<int>());
        notifyListeners();
      } catch (e) {
        print('Error loading favorites: $e');
      }
    }
  }

  Future<void> _saveFavorites() async {
    final encoded = jsonEncode(_favoriteIds.toList());
    await _prefs.setString(AppConstants.keyFavorites, encoded);
  }

  void toggleFavorite(int productId) {
    if (_favoriteIds.contains(productId)) {
      _favoriteIds.remove(productId);
    } else {
      _favoriteIds.add(productId);
    }
    _saveFavorites();
    notifyListeners();
  }

  bool isFavorite(int productId) {
    return _favoriteIds.contains(productId);
  }

  void clear() {
    _favoriteIds.clear();
    _saveFavorites();
    notifyListeners();
  }
}
