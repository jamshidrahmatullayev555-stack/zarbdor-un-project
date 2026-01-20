import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../config/constants.dart';

class WebSocketService {
  WebSocketChannel? _channel;
  final String token;
  final int orderId;
  final Function(Map<String, dynamic>) onMessage;

  WebSocketService({
    required this.token,
    required this.orderId,
    required this.onMessage,
  });

  void connect() {
    try {
      final uri = Uri.parse('${AppConstants.wsUrl}/chat/$orderId?token=$token');
      _channel = WebSocketChannel.connect(uri);
      
      _channel!.stream.listen(
        (data) {
          final message = jsonDecode(data);
          onMessage(message);
        },
        onError: (error) {
          print('WebSocket error: $error');
        },
        onDone: () {
          print('WebSocket connection closed');
        },
      );
    } catch (e) {
      print('Failed to connect WebSocket: $e');
    }
  }

  void sendMessage(Map<String, dynamic> message) {
    if (_channel != null) {
      _channel!.sink.add(jsonEncode(message));
    }
  }

  void disconnect() {
    _channel?.sink.close();
    _channel = null;
  }
}
