class Neighborhood {
  final int id;
  final Map<String, String> name;
  final int districtId;
  final String? districtName;

  Neighborhood({
    required this.id,
    required this.name,
    required this.districtId,
    this.districtName,
  });

  factory Neighborhood.fromJson(Map<String, dynamic> json) {
    return Neighborhood(
      id: json['id'],
      name: Map<String, String>.from(json['name']),
      districtId: json['district_id'],
      districtName: json['district_name'],
    );
  }

  String getName(String lang) {
    return name[lang] ?? name['uz'] ?? '';
  }
}
