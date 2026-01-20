class User {
  final int id;
  final String phoneNumber;
  final String? firstName;
  final String? lastName;
  final String? avatarUrl;
  final String role;
  final DateTime createdAt;

  User({
    required this.id,
    required this.phoneNumber,
    this.firstName,
    this.lastName,
    this.avatarUrl,
    required this.role,
    required this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      phoneNumber: json['phone_number'],
      firstName: json['first_name'],
      lastName: json['last_name'],
      avatarUrl: json['avatar_url'],
      role: json['role'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'phone_number': phoneNumber,
      'first_name': firstName,
      'last_name': lastName,
      'avatar_url': avatarUrl,
      'role': role,
      'created_at': createdAt.toIso8601String(),
    };
  }

  String get fullName {
    if (firstName != null && lastName != null) {
      return '$firstName $lastName';
    }
    return phoneNumber;
  }
}
