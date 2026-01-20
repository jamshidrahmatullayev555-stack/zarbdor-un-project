import 'product.dart';

class CartItem {
  final Product product;
  int quantity;

  CartItem({
    required this.product,
    required this.quantity,
  });

  factory CartItem.fromJson(Map<String, dynamic> json) {
    return CartItem(
      product: Product.fromJson(json['product']),
      quantity: json['quantity'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'product_id': product.id,
      'quantity': quantity,
    };
  }

  double get totalPrice => product.price * quantity;

  bool get canIncrement => quantity < product.stock;
}
