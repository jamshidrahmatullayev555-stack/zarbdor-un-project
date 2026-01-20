import 'package:flutter/foundation.dart';
import '../models/chat_message.dart';
import '../services/api_service.dart';
import '../services/websocket_service.dart';

class ChatProvider with ChangeNotifier {
  final ApiService _apiService;
  final int orderId;
  final int currentUserId;
  
  List<ChatMessage> _messages = [];
  WebSocketService? _wsService;
  bool _isLoading = false;

  ChatProvider(this._apiService, this.orderId, this.currentUserId) {
    loadMessages();
  }

  List<ChatMessage> get messages => _messages;
  bool get isLoading => _isLoading;

  Future<void> loadMessages() async {
    _isLoading = true;
    notifyListeners();

    try {
      final data = await _apiService.getChatMessages(orderId);
      _messages = data
          .map((json) => ChatMessage.fromJson(json, currentUserId))
          .toList();
    } catch (e) {
      print('Error loading messages: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void connectWebSocket(String token) {
    _wsService = WebSocketService(
      token: token,
      orderId: orderId,
      onMessage: (message) {
        final chatMessage = ChatMessage.fromJson(message, currentUserId);
        _messages.add(chatMessage);
        notifyListeners();
      },
    );
    _wsService!.connect();
  }

  Future<void> sendMessage(String content, {String? imageUrl}) async {
    try {
      final data = await _apiService.sendChatMessage(
        orderId,
        content,
        imageUrl: imageUrl,
      );
      
      // WebSocket will handle adding the message to the list
      if (_wsService == null) {
        final message = ChatMessage.fromJson(data, currentUserId);
        _messages.add(message);
        notifyListeners();
      }
    } catch (e) {
      print('Error sending message: $e');
    }
  }

  @override
  void dispose() {
    _wsService?.disconnect();
    super.dispose();
  }
}
