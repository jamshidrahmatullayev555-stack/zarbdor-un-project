class Category {
  final int id;
  final Map<String, String> name;
  final String? imageUrl;
  final bool isActive;

  Category({
    required this.id,
    required this.name,
    this.imageUrl,
    required this.isActive,
  });

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: json['id'],
      name: Map<String, String>.from(json['name']),
      imageUrl: json['image_url'],
      isActive: json['is_active'] ?? true,
    );
  }

  String getName(String lang) {
    return name[lang] ?? name['uz'] ?? '';
  }
}
