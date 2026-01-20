import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:intl/intl.dart';
import '../../config/routes.dart';
import '../../models/product.dart';
import '../../providers/language_provider.dart';
import '../../providers/cart_provider.dart';
import '../../providers/favorites_provider.dart';
import '../../providers/auth_provider.dart';

class ProductDetailScreen extends StatefulWidget {
  const ProductDetailScreen({super.key});

  @override
  State<ProductDetailScreen> createState() => _ProductDetailScreenState();
}

class _ProductDetailScreenState extends State<ProductDetailScreen> {
  int _currentImageIndex = 0;
  int _quantity = 1;

  @override
  Widget build(BuildContext context) {
    final lang = Provider.of<LanguageProvider>(context);
    final cartProvider = Provider.of<CartProvider>(context);
    final favoritesProvider = Provider.of<FavoritesProvider>(context);
    final authProvider = Provider.of<AuthProvider>(context);
    final product = ModalRoute.of(context)?.settings.arguments as Product?;
    final formatter = NumberFormat('#,##0', 'en_US');

    if (product == null) {
      return Scaffold(
        appBar: AppBar(),
        body: const Center(child: Text('Product not found')),
      );
    }

    final isFavorite = favoritesProvider.isFavorite(product.id);

    return Scaffold(
      appBar: AppBar(
        actions: [
          IconButton(
            icon: Icon(
              isFavorite ? Icons.favorite : Icons.favorite_border,
              color: isFavorite ? Colors.red : null,
            ),
            onPressed: () {
              favoritesProvider.toggleFavorite(product.id);
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView(
              children: [
                // Image Carousel
                SizedBox(
                  height: 300,
                  child: product.imageUrls.isNotEmpty
                      ? Stack(
                          children: [
                            PageView.builder(
                              itemCount: product.imageUrls.length,
                              onPageChanged: (index) {
                                setState(() {
                                  _currentImageIndex = index;
                                });
                              },
                              itemBuilder: (context, index) {
                                return CachedNetworkImage(
                                  imageUrl: product.imageUrls[index],
                                  fit: BoxFit.cover,
                                  placeholder: (context, url) => const Center(
                                    child: CircularProgressIndicator(),
                                  ),
                                  errorWidget: (context, url, error) => const Icon(
                                    Icons.image_not_supported,
                                    size: 100,
                                  ),
                                );
                              },
                            ),
                            if (product.imageUrls.length > 1)
                              Positioned(
                                bottom: 16,
                                left: 0,
                                right: 0,
                                child: Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: List.generate(
                                    product.imageUrls.length,
                                    (index) => Container(
                                      margin: const EdgeInsets.symmetric(horizontal: 4),
                                      width: 8,
                                      height: 8,
                                      decoration: BoxDecoration(
                                        shape: BoxShape.circle,
                                        color: _currentImageIndex == index
                                            ? Theme.of(context).primaryColor
                                            : Colors.white,
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                          ],
                        )
                      : Container(
                          color: Colors.grey[200],
                          child: const Icon(
                            Icons.image_not_supported,
                            size: 100,
                          ),
                        ),
                ),
                
                Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        product.getName(lang.currentLanguage),
                        style: Theme.of(context).textTheme.displaySmall,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '${formatter.format(product.price)} ${lang.translate(lang.sum)}',
                        style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                          color: Theme.of(context).primaryColor,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      if (product.sellerName != null) ...[
                        Row(
                          children: [
                            const Icon(Icons.store, size: 20),
                            const SizedBox(width: 8),
                            Text(
                              product.sellerName!,
                              style: Theme.of(context).textTheme.bodyLarge,
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                      ],
                      Text(
                        lang.isUzbek ? 'Tavsif' : 'Описание',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        product.getDescription(lang.currentLanguage),
                        style: Theme.of(context).textTheme.bodyLarge,
                      ),
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          Icon(
                            product.inStock ? Icons.check_circle : Icons.cancel,
                            color: product.inStock ? Colors.green : Colors.red,
                            size: 20,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            product.inStock
                                ? (lang.isUzbek ? 'Omborda bor' : 'В наличии')
                                : (lang.isUzbek ? 'Tugagan' : 'Нет в наличии'),
                            style: Theme.of(context).textTheme.bodyLarge,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          
          // Bottom Actions
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
              child: Row(
                children: [
                  // Quantity Selector
                  Container(
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey.shade300),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      children: [
                        IconButton(
                          icon: const Icon(Icons.remove),
                          onPressed: _quantity > 1
                              ? () {
                                  setState(() {
                                    _quantity--;
                                  });
                                }
                              : null,
                        ),
                        Text(
                          '$_quantity',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        IconButton(
                          icon: const Icon(Icons.add),
                          onPressed: _quantity < product.stock
                              ? () {
                                  setState(() {
                                    _quantity++;
                                  });
                                }
                              : null,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 16),
                  
                  // Add to Cart Button
                  Expanded(
                    child: ElevatedButton(
                      onPressed: product.inStock
                          ? () {
                              cartProvider.addItem(product, quantity: _quantity);
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text(
                                    lang.isUzbek
                                        ? 'Savatga qo\'shildi'
                                        : 'Добавлено в корзину',
                                  ),
                                  duration: const Duration(seconds: 2),
                                ),
                              );
                            }
                          : null,
                      child: Text(lang.translate(lang.addToCart)),
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
