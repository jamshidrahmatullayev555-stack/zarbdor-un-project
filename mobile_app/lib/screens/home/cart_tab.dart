import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../config/routes.dart';
import '../../providers/language_provider.dart';
import '../../providers/cart_provider.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/cart_item_widget.dart';

class CartTab extends StatelessWidget {
  const CartTab({super.key});

  @override
  Widget build(BuildContext context) {
    final lang = Provider.of<LanguageProvider>(context);
    final cartProvider = Provider.of<CartProvider>(context);
    final authProvider = Provider.of<AuthProvider>(context);
    final formatter = NumberFormat('#,##0', 'en_US');

    return Scaffold(
      appBar: AppBar(
        title: Text(lang.translate(lang.cart)),
      ),
      body: cartProvider.isEmpty
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.shopping_cart_outlined,
                    size: 100,
                    color: Colors.grey[400],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    lang.translate(lang.emptyCart),
                    style: Theme.of(context).textTheme.bodyLarge,
                  ),
                ],
              ),
            )
          : Column(
              children: [
                Expanded(
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: cartProvider.items.length,
                    itemBuilder: (context, index) {
                      return CartItemWidget(
                        cartItem: cartProvider.items[index],
                      );
                    },
                  ),
                ),
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.1),
                        blurRadius: 10,
                        offset: const Offset(0, -5),
                      ),
                    ],
                  ),
                  child: SafeArea(
                    child: Column(
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              lang.translate(lang.total),
                              style: Theme.of(context).textTheme.titleLarge,
                            ),
                            Text(
                              '${formatter.format(cartProvider.totalAmount)} ${lang.translate(lang.sum)}',
                              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                color: Theme.of(context).primaryColor,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton(
                            onPressed: () {
                              if (authProvider.isGuest) {
                                Navigator.of(context).pushNamed(AppRoutes.login);
                              } else {
                                Navigator.of(context).pushNamed(AppRoutes.checkout);
                              }
                            },
                            child: Text(lang.translate(lang.checkout)),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
    );
  }
}
