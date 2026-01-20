import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:intl/intl.dart';
import '../config/routes.dart';
import '../models/product.dart';
import '../providers/language_provider.dart';
import '../providers/favorites_provider.dart';

class ProductCard extends StatelessWidget {
  final Product product;

  const ProductCard({
    super.key,
    required this.product,
  });

  @override
  Widget build(BuildContext context) {
    final lang = Provider.of<LanguageProvider>(context);
    final favoritesProvider = Provider.of<FavoritesProvider>(context);
    final formatter = NumberFormat('#,##0', 'en_US');
    final isFavorite = favoritesProvider.isFavorite(product.id);

    return GestureDetector(
      onTap: () {
        Navigator.of(context).pushNamed(
          AppRoutes.productDetail,
          arguments: product,
        );
      },
      child: Card(
        clipBehavior: Clip.antiAlias,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Stack(
              children: [
                AspectRatio(
                  aspectRatio: 1,
                  child: product.mainImage.isNotEmpty
                      ? CachedNetworkImage(
                          imageUrl: product.mainImage,
                          fit: BoxFit.cover,
                          placeholder: (context, url) => Container(
                            color: Colors.grey[200],
                            child: const Center(
                              child: CircularProgressIndicator(),
                            ),
                          ),
                          errorWidget: (context, url, error) => Container(
                            color: Colors.grey[200],
                            child: const Icon(
                              Icons.image_not_supported,
                              size: 50,
                            ),
                          ),
                        )
                      : Container(
                          color: Colors.grey[200],
                          child: const Icon(
                            Icons.image_not_supported,
                            size: 50,
                          ),
                        ),
                ),
                Positioned(
                  top: 8,
                  right: 8,
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.1),
                          blurRadius: 4,
                        ),
                      ],
                    ),
                    child: IconButton(
                      icon: Icon(
                        isFavorite ? Icons.favorite : Icons.favorite_border,
                        color: isFavorite ? Colors.red : Colors.grey[600],
                        size: 20,
                      ),
                      onPressed: () {
                        favoritesProvider.toggleFavorite(product.id);
                      },
                      padding: const EdgeInsets.all(8),
                      constraints: const BoxConstraints(),
                    ),
                  ),
                ),
                if (!product.inStock)
                  Positioned.fill(
                    child: Container(
                      color: Colors.black.withOpacity(0.5),
                      alignment: Alignment.center,
                      child: Text(
                        lang.isUzbek ? 'Tugagan' : 'Нет в наличии',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
              ],
            ),
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    product.getName(lang.currentLanguage),
                    style: Theme.of(context).textTheme.bodyLarge,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '${formatter.format(product.price)} ${lang.translate(lang.sum)}',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      color: Theme.of(context).primaryColor,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
