import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:image_picker/image_picker.dart';
import 'package:intl/intl.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../config/constants.dart';
import '../../providers/language_provider.dart';
import '../../providers/chat_provider.dart';
import '../../providers/auth_provider.dart';
import '../../services/api_service.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _messageController = TextEditingController();
  final _scrollController = ScrollController();
  ChatProvider? _chatProvider;
  bool _isInitialized = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (!_isInitialized) {
      _initialize();
      _isInitialized = true;
    }
  }

  Future<void> _initialize() async {
    final orderId = ModalRoute.of(context)?.settings.arguments as int?;
    if (orderId == null) return;

    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final prefs = await SharedPreferences.getInstance();
    final apiService = ApiService(prefs);

    _chatProvider = ChatProvider(
      apiService,
      orderId,
      authProvider.user?.id ?? 0,
    );

    final token = prefs.getString(AppConstants.keyToken);
    if (token != null) {
      _chatProvider!.connectWebSocket(token);
    }

    setState(() {});

    _chatProvider!.addListener(() {
      if (mounted) {
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (_scrollController.hasClients) {
            _scrollController.animateTo(
              _scrollController.position.maxScrollExtent,
              duration: const Duration(milliseconds: 300),
              curve: Curves.easeOut,
            );
          }
        });
      }
    });
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    _chatProvider?.dispose();
    super.dispose();
  }

  Future<void> _sendMessage() async {
    final content = _messageController.text.trim();
    if (content.isEmpty || _chatProvider == null) return;

    _messageController.clear();
    await _chatProvider!.sendMessage(content);
  }

  Future<void> _pickImage() async {
    final picker = ImagePicker();
    final image = await picker.pickImage(source: ImageSource.gallery);
    
    if (image != null && _chatProvider != null) {
      final prefs = await SharedPreferences.getInstance();
      final apiService = ApiService(prefs);
      
      try {
        final imageUrl = await apiService.uploadImage(image.path);
        await _chatProvider!.sendMessage('📷 Image', imageUrl: imageUrl);
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Failed to upload image: $e')),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final lang = Provider.of<LanguageProvider>(context);
    final dateFormatter = DateFormat('HH:mm');

    if (_chatProvider == null) {
      return Scaffold(
        appBar: AppBar(
          title: Text(lang.translate(lang.chat)),
        ),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    return ChangeNotifierProvider.value(
      value: _chatProvider,
      child: Scaffold(
        appBar: AppBar(
          title: Text(lang.translate(lang.chat)),
        ),
        body: Column(
          children: [
            Expanded(
              child: Consumer<ChatProvider>(
                builder: (context, provider, child) {
                  if (provider.isLoading) {
                    return const Center(child: CircularProgressIndicator());
                  }

                  if (provider.messages.isEmpty) {
                    return Center(
                      child: Text(
                        lang.isUzbek 
                            ? 'Xabarlar yo\'q'
                            : 'Нет сообщений',
                        style: Theme.of(context).textTheme.bodyLarge,
                      ),
                    );
                  }

                  return ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(16),
                    itemCount: provider.messages.length,
                    itemBuilder: (context, index) {
                      final message = provider.messages[index];
                      return Align(
                        alignment: message.isMine
                            ? Alignment.centerRight
                            : Alignment.centerLeft,
                        child: Container(
                          margin: const EdgeInsets.only(bottom: 12),
                          padding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 10,
                          ),
                          constraints: BoxConstraints(
                            maxWidth: MediaQuery.of(context).size.width * 0.7,
                          ),
                          decoration: BoxDecoration(
                            color: message.isMine
                                ? Theme.of(context).primaryColor
                                : Colors.grey[200],
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              if (!message.isMine)
                                Text(
                                  message.senderName,
                                  style: TextStyle(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w600,
                                    color: message.isMine
                                        ? Colors.white70
                                        : Colors.black54,
                                  ),
                                ),
                              if (message.imageUrl != null) ...[
                                const SizedBox(height: 4),
                                ClipRRect(
                                  borderRadius: BorderRadius.circular(8),
                                  child: Image.network(
                                    message.imageUrl!,
                                    width: 200,
                                    fit: BoxFit.cover,
                                  ),
                                ),
                              ],
                              if (message.content.isNotEmpty) ...[
                                const SizedBox(height: 4),
                                Text(
                                  message.content,
                                  style: TextStyle(
                                    fontSize: 15,
                                    color: message.isMine
                                        ? Colors.white
                                        : Colors.black87,
                                  ),
                                ),
                              ],
                              const SizedBox(height: 4),
                              Text(
                                dateFormatter.format(message.timestamp),
                                style: TextStyle(
                                  fontSize: 11,
                                  color: message.isMine
                                      ? Colors.white70
                                      : Colors.black54,
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  );
                },
              ),
            ),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 10,
                    offset: const Offset(0, -5),
                  ),
                ],
              ),
              child: SafeArea(
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.image),
                      onPressed: _pickImage,
                    ),
                    Expanded(
                      child: TextField(
                        controller: _messageController,
                        decoration: InputDecoration(
                          hintText: lang.translate(lang.sendMessage),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(24),
                          ),
                          contentPadding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 8,
                          ),
                        ),
                        maxLines: null,
                        textInputAction: TextInputAction.send,
                        onSubmitted: (_) => _sendMessage(),
                      ),
                    ),
                    const SizedBox(width: 8),
                    IconButton(
                      icon: const Icon(Icons.send),
                      color: Theme.of(context).primaryColor,
                      onPressed: _sendMessage,
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
