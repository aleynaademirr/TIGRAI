import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/icerik.dart';
import '../constants/app_theme.dart';
import '../screens/icerik_detail_screen.dart';
class ChatWidget extends StatefulWidget {
  final int kullaniciId;
  final Icerik? contextIcerik; 
  final bool isEmbedded; 
  const ChatWidget({
    super.key, 
    required this.kullaniciId, 
    this.contextIcerik,
    this.isEmbedded = false,
  });
  @override
  _ChatWidgetState createState() => _ChatWidgetState();
}
class _ChatWidgetState extends State<ChatWidget> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<ChatMessage> _messages = [];
  bool _isLoading = false;
  @override
  void initState() {
    super.initState();
    if (widget.contextIcerik != null) {
      _addBotMessage(
        "Selam! '${widget.contextIcerik!.baslik}' hakkında konuşmak ister misin? \nBu içerik hakkında ne düşünüyorsun?",
        MessageType.greeting
      );
    } else if (!widget.isEmbedded) {
      _addBotMessage(
        "Merhaba! Ben senin AI film ve kitap asistanınım. 🎬📚\nBugün nasıl hissediyorsun? Sana özel bir öneri yapabilirim.",
        MessageType.greeting
      );
    }
  }
  @override
  Widget build(BuildContext context) {
    Widget content = Column(
      children: [
        Expanded(
          child: Container(
             decoration: widget.isEmbedded 
               ? BoxDecoration(
                   color: Colors.black26, 
                   borderRadius: BorderRadius.circular(16),
                   border: Border.all(color: Colors.white10)
                 ) 
               : null,
             margin: widget.isEmbedded ? const EdgeInsets.all(0) : null,
             child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                return _buildMessageBubble(_messages[index]);
              },
            ),
          ),
        ),
        if (_isLoading)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            alignment: Alignment.centerLeft,
            child: Row(
              children: [
                 const SizedBox(width: 44),
                 Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    decoration: BoxDecoration(
                      color: AppTheme.cardDark,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const SizedBox(width:16, height:16, child: CircularProgressIndicator(strokeWidth: 2, color: AppTheme.primaryGreen)),
                        const SizedBox(width: 10),
                        Text('Yazıyor...', style: TextStyle(color: Colors.grey[400], fontSize: 13)),
                      ],
                    ),
                 )
              ],
            ),
          ),
        _buildMessageInput(),
      ],
    );
    if (widget.isEmbedded) {
      return SizedBox(
        height: 500, 
        child: content,
      );
    }
    return content; 
  }
  Widget _buildMessageBubble(ChatMessage message) {
    final isUser = message.isUser;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (!isUser) ...[
            CircleAvatar(
              radius: 16,
              backgroundColor: AppTheme.cardDark,
              child: const Icon(Icons.smart_toy, size: 18, color: AppTheme.primaryGreen),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Column(
              crossAxisAlignment: isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    gradient: isUser 
                      ? const LinearGradient(colors: [AppTheme.primaryBlue, Color(0xFF2B95D6)])
                      : const LinearGradient(colors: [AppTheme.cardDark, Color(0xFF252D38)]),
                    borderRadius: BorderRadius.only(
                      topLeft: const Radius.circular(20),
                      topRight: const Radius.circular(20),
                      bottomLeft: Radius.circular(isUser ? 20 : 4),
                      bottomRight: Radius.circular(isUser ? 4 : 20),
                    ),
                  ),
                  child: SelectableText(
                    message.text,
                    style: const TextStyle(
                      color: Colors.white, 
                      fontSize: 15, 
                      height: 1.4,
                      fontFamily: 'Roboto', 
                    ),
                  ),
                ),
                if (message.recommendedContent != null)
                  _buildRecommendationCard(message.recommendedContent!),
              ],
            ),
          ),
          if (isUser) ...[
            const SizedBox(width: 8),
            const CircleAvatar(
              radius: 16,
              backgroundColor: AppTheme.primaryBlue,
              child: Icon(Icons.person, size: 18, color: Colors.white),
            ),
          ],
        ],
      ),
    );
  }
  Widget _buildRecommendationCard(Icerik content) {
    Color accentColor;
    IconData icon;
    if (content.tur == 'Film') { accentColor = AppTheme.primaryGreen; icon = Icons.movie; }
    else if (content.tur == 'Dizi') { accentColor = AppTheme.primaryBlue; icon = Icons.tv; }
    else { accentColor = AppTheme.primaryOrange; icon = Icons.book; }
    return Container(
      width: 260,
      margin: const EdgeInsets.only(top: 12),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: accentColor.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: accentColor.withOpacity(0.1),
              borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
            ),
            child: Row(
              children: [
                Icon(icon, size: 16, color: accentColor),
                const SizedBox(width: 8),
                Text('Sana Özel Öneri', style: TextStyle(color: accentColor, fontWeight: FontWeight.bold, fontSize: 12)),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(content.baslik, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                const SizedBox(height: 12),
                ElevatedButton(
                  onPressed: () {
                       Navigator.push(context, MaterialPageRoute(
                         builder: (_) => IcerikDetailScreen(icerik: content, kullaniciId: widget.kullaniciId)
                       ));
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: accentColor,
                    minimumSize: Size.zero,
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  ),
                  child: const Text('İncele', style: TextStyle(fontSize: 12)),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  Widget _buildMessageInput() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        border: Border(top: BorderSide(color: Colors.white.withOpacity(0.05))),
      ),
      child: Row(
        children: [
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: AppTheme.backgroundDark,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: Colors.white10),
              ),
              child: TextField(
                controller: _messageController,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  hintText: 'Mesaj yaz...',
                  hintStyle: TextStyle(color: Colors.grey[600]),
                  border: InputBorder.none,
                  contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                ),
                onSubmitted: (text) {
                  if (text.trim().isNotEmpty) _sendMessage(text.trim());
                },
              ),
            ),
          ),
          const SizedBox(width: 12),
          GestureDetector(
            onTap: _isLoading ? null : () {
              if (_messageController.text.trim().isNotEmpty) {
                 _sendMessage(_messageController.text.trim());
              }
            },
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: const BoxDecoration(color: AppTheme.primaryGreen, shape: BoxShape.circle),
              child: Icon(_isLoading ? Icons.hourglass_top : Icons.send_rounded, color: Colors.black, size: 20),
            ),
          ),
        ],
      ),
    );
  }
  void _sendMessage(String message) async {
    if (message.trim().isEmpty || _isLoading) return;
    setState(() {
      _messages.add(ChatMessage(text: message, isUser: true, timestamp: DateTime.now()));
      _isLoading = true;
    });
    _messageController.clear();
    _scrollToBottom();
    String apiMessage = message;
    if (widget.contextIcerik != null && _messages.length <= 1) { 
       apiMessage = "Şu içerik hakkında konuşuyoruz: ${widget.contextIcerik!.baslik} (${widget.contextIcerik!.tur}). Kullanıcı dedi ki: $message";
    }
    try {
      final response = await ApiService.sendChatMessage(
        message: apiMessage,
        kullaniciId: widget.kullaniciId,
      );
      setState(() {
        _messages.add(ChatMessage(
          text: response['bot_response'],
          isUser: false,
          timestamp: DateTime.now(),
          messageType: _getMessageType(response['response_type']),
          recommendedContent: response['recommended_content'] != null
              ? Icerik.fromJson(response['recommended_content'])
              : null,
        ));
        _isLoading = false;
      });
      _scrollToBottom();
    } catch (e) {
      setState(() {
        _messages.add(ChatMessage(text: 'Bir hata oldu: $e', isUser: false, timestamp: DateTime.now(), messageType: MessageType.error));
        _isLoading = false;
      });
    }
  }
  void _addBotMessage(String text, MessageType type) {
    setState(() {
      _messages.add(ChatMessage(text: text, isUser: false, timestamp: DateTime.now(), messageType: type));
    });
  }
  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(_scrollController.position.maxScrollExtent, duration: const Duration(milliseconds: 300), curve: Curves.easeOut);
      }
    });
  }
  MessageType _getMessageType(String responseType) {
    switch (responseType) {
      case 'recommendation': return MessageType.recommendation;
      case 'greeting': return MessageType.greeting;
      case 'error': return MessageType.error;
      default: return MessageType.general;
    }
  }
}
class ChatMessage {
  final String text;
  final bool isUser;
  final DateTime timestamp;
  final MessageType messageType;
  final Icerik? recommendedContent;
  ChatMessage({
    required this.text,
    required this.isUser,
    required this.timestamp,
    this.messageType = MessageType.general,
    this.recommendedContent,
  });
}
enum MessageType { general, greeting, recommendation, error, help }