import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/language_provider.dart';
import 'home_tab.dart';
import 'favorites_tab.dart';
import 'cart_tab.dart';
import 'profile_tab.dart';

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _currentIndex = 0;

  final List<Widget> _tabs = const [
    HomeTab(),
    FavoritesTab(),
    CartTab(),
    ProfileTab(),
  ];

  @override
  Widget build(BuildContext context) {
    final lang = Provider.of<LanguageProvider>(context);

    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _tabs,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        items: [
          BottomNavigationBarItem(
            icon: const Icon(Icons.home_rounded),
            label: lang.translate(lang.home),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.favorite_rounded),
            label: lang.translate(lang.favorites),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.shopping_cart_rounded),
            label: lang.translate(lang.cart),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.person_rounded),
            label: lang.translate(lang.profile),
          ),
        ],
      ),
    );
  }
}
