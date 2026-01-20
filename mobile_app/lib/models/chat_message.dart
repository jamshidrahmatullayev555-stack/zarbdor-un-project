class ChatMessage {
  final int? id;
  final int orderId;
  final int senderId;
  final String senderName;
  final String content;
  final String? imageUrl;
  final DateTime timestamp;
  final bool isMine;

  ChatMessage({
    this.id,
    required this.orderId,
    required this.senderId,
    required this.senderName,
    required this.content,
    this.imageUrl,
    required this.timestamp,
    required this.isMine,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json, int currentUserId) {
    return ChatMessage(
      id: json['id'],
      orderId: json['order_id'],
      senderId: json['sender_id'],
      senderName: json['sender_name'],
      content: json['content'],
      imageUrl: json['image_url'],
      timestamp: DateTime.parse(json['timestamp']),
      isMine: json['sender_id'] == currentUserId,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'order_id': orderId,
      'sender_id': senderId,
      'content': content,
      'image_url': imageUrl,
      'timestamp': timestamp.toIso8601String(),
    };
  }
}
