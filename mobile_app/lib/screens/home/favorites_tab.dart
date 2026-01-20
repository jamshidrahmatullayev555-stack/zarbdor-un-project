import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/language_provider.dart';
import '../../providers/products_provider.dart';
import '../../providers/favorites_provider.dart';
import '../../widgets/product_card.dart';

class FavoritesTab extends StatelessWidget {
  const FavoritesTab({super.key});

  @override
  Widget build(BuildContext context) {
    final lang = Provider.of<LanguageProvider>(context);
    final favoritesProvider = Provider.of<FavoritesProvider>(context);
    final productsProvider = Provider.of<ProductsProvider>(context);

    final favoriteProducts = productsProvider.products
        .where((p) => favoritesProvider.isFavorite(p.id))
        .toList();

    return Scaffold(
      appBar: AppBar(
        title: Text(lang.translate(lang.favorites)),
      ),
      body: favoriteProducts.isEmpty
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.favorite_outline_rounded,
                    size: 100,
                    color: Colors.grey[400],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    lang.isUzbek 
                        ? 'Sevimli mahsulotlar yo\'q' 
                        : 'Нет избранных товаров',
                    style: Theme.of(context).textTheme.bodyLarge,
                  ),
                ],
              ),
            )
          : GridView.builder(
              padding: const EdgeInsets.all(16),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                childAspectRatio: 0.7,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
              ),
              itemCount: favoriteProducts.length,
              itemBuilder: (context, index) {
                return ProductCard(product: favoriteProducts[index]);
              },
            ),
    );
  }
}
