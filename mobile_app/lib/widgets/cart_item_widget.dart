import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:intl/intl.dart';
import '../models/cart_item.dart';
import '../providers/language_provider.dart';
import '../providers/cart_provider.dart';

class CartItemWidget extends StatelessWidget {
  final CartItem cartItem;

  const CartItemWidget({
    super.key,
    required this.cartItem,
  });

  @override
  Widget build(BuildContext context) {
    final lang = Provider.of<LanguageProvider>(context);
    final cartProvider = Provider.of<CartProvider>(context);
    final formatter = NumberFormat('#,##0', 'en_US');

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: cartItem.product.mainImage.isNotEmpty
                  ? CachedNetworkImage(
                      imageUrl: cartItem.product.mainImage,
                      width: 80,
                      height: 80,
                      fit: BoxFit.cover,
                      placeholder: (context, url) => Container(
                        width: 80,
                        height: 80,
                        color: Colors.grey[200],
                        child: const Center(
                          child: CircularProgressIndicator(),
                        ),
                      ),
                      errorWidget: (context, url, error) => Container(
                        width: 80,
                        height: 80,
                        color: Colors.grey[200],
                        child: const Icon(Icons.image_not_supported),
                      ),
                    )
                  : Container(
                      width: 80,
                      height: 80,
                      color: Colors.grey[200],
                      child: const Icon(Icons.image_not_supported),
                    ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    cartItem.product.getName(lang.currentLanguage),
                    style: Theme.of(context).textTheme.bodyLarge,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '${formatter.format(cartItem.product.price)} ${lang.translate(lang.sum)}',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Container(
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.grey.shade300),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(
                          children: [
                            InkWell(
                              onTap: () {
                                if (cartItem.quantity > 1) {
                                  cartProvider.updateQuantity(
                                    cartItem.product.id,
                                    cartItem.quantity - 1,
                                  );
                                }
                              },
                              child: Container(
                                padding: const EdgeInsets.all(8),
                                child: Icon(
                                  Icons.remove,
                                  size: 16,
                                  color: cartItem.quantity > 1
                                      ? Colors.black
                                      : Colors.grey,
                                ),
                              ),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 12),
                              child: Text(
                                '${cartItem.quantity}',
                                style: Theme.of(context).textTheme.bodyLarge,
                              ),
                            ),
                            InkWell(
                              onTap: () {
                                if (cartItem.canIncrement) {
                                  cartProvider.updateQuantity(
                                    cartItem.product.id,
                                    cartItem.quantity + 1,
                                  );
                                }
                              },
                              child: Container(
                                padding: const EdgeInsets.all(8),
                                child: Icon(
                                  Icons.add,
                                  size: 16,
                                  color: cartItem.canIncrement
                                      ? Theme.of(context).primaryColor
                                      : Colors.grey,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const Spacer(),
                      IconButton(
                        icon: const Icon(Icons.delete_outline),
                        color: Colors.red,
                        onPressed: () {
                          cartProvider.removeItem(cartItem.product.id);
                        },
                      ),
                    ],
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
