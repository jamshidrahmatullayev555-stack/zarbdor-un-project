class Order {
  final int id;
  final int customerId;
  final String status;
  final double totalAmount;
  final String? notes;
  final String deliveryAddress;
  final double? deliveryLat;
  final double? deliveryLon;
  final int? courierId;
  final String? courierName;
  final List<OrderItem> items;
  final DateTime createdAt;
  final DateTime? deliveredAt;

  Order({
    required this.id,
    required this.customerId,
    required this.status,
    required this.totalAmount,
    this.notes,
    required this.deliveryAddress,
    this.deliveryLat,
    this.deliveryLon,
    this.courierId,
    this.courierName,
    required this.items,
    required this.createdAt,
    this.deliveredAt,
  });

  factory Order.fromJson(Map<String, dynamic> json) {
    return Order(
      id: json['id'],
      customerId: json['customer_id'],
      status: json['status'],
      totalAmount: (json['total_amount'] as num).toDouble(),
      notes: json['notes'],
      deliveryAddress: json['delivery_address'],
      deliveryLat: json['delivery_lat']?.toDouble(),
      deliveryLon: json['delivery_lon']?.toDouble(),
      courierId: json['courier_id'],
      courierName: json['courier_name'],
      items: (json['items'] as List?)
          ?.map((item) => OrderItem.fromJson(item))
          .toList() ?? [],
      createdAt: DateTime.parse(json['created_at']),
      deliveredAt: json['delivered_at'] != null 
          ? DateTime.parse(json['delivered_at']) 
          : null,
    );
  }

  String getStatusText(String lang) {
    final statusMap = {
      'pending': {'uz': 'Kutilmoqda', 'ru': 'Ожидание'},
      'confirmed': {'uz': 'Tasdiqlandi', 'ru': 'Подтверждено'},
      'preparing': {'uz': 'Tayyorlanmoqda', 'ru': 'Готовится'},
      'ready': {'uz': 'Tayyor', 'ru': 'Готово'},
      'picked_up': {'uz': 'Olib ketildi', 'ru': 'Забрано'},
      'in_transit': {'uz': 'Yo\'lda', 'ru': 'В пути'},
      'delivered': {'uz': 'Yetkazildi', 'ru': 'Доставлено'},
      'cancelled': {'uz': 'Bekor qilindi', 'ru': 'Отменено'},
    };
    return statusMap[status]?[lang] ?? status;
  }
}

class OrderItem {
  final int productId;
  final Map<String, String> productName;
  final int quantity;
  final double price;
  final String? imageUrl;

  OrderItem({
    required this.productId,
    required this.productName,
    required this.quantity,
    required this.price,
    this.imageUrl,
  });

  factory OrderItem.fromJson(Map<String, dynamic> json) {
    return OrderItem(
      productId: json['product_id'],
      productName: Map<String, String>.from(json['product_name']),
      quantity: json['quantity'],
      price: (json['price'] as num).toDouble(),
      imageUrl: json['image_url'],
    );
  }

  String getName(String lang) {
    return productName[lang] ?? productName['uz'] ?? '';
  }

  double get totalPrice => price * quantity;
}
