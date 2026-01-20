class Product {
  final int id;
  final Map<String, String> name;
  final Map<String, String> description;
  final double price;
  final int stock;
  final List<String> imageUrls;
  final int categoryId;
  final int sellerId;
  final String? sellerName;
  final bool isActive;
  final DateTime createdAt;

  Product({
    required this.id,
    required this.name,
    required this.description,
    required this.price,
    required this.stock,
    required this.imageUrls,
    required this.categoryId,
    required this.sellerId,
    this.sellerName,
    required this.isActive,
    required this.createdAt,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'],
      name: Map<String, String>.from(json['name']),
      description: Map<String, String>.from(json['description']),
      price: (json['price'] as num).toDouble(),
      stock: json['stock'],
      imageUrls: List<String>.from(json['image_urls'] ?? []),
      categoryId: json['category_id'],
      sellerId: json['seller_id'],
      sellerName: json['seller_name'],
      isActive: json['is_active'] ?? true,
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  String getName(String lang) {
    return name[lang] ?? name['uz'] ?? '';
  }

  String getDescription(String lang) {
    return description[lang] ?? description['uz'] ?? '';
  }

  String get mainImage {
    return imageUrls.isNotEmpty ? imageUrls[0] : '';
  }

  bool get inStock => stock > 0;
}
