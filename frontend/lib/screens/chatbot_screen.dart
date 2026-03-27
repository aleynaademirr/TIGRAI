import 'package:flutter/material.dart';
import '../constants/app_theme.dart';
import 'smart_search_screen.dart';
import 'home_screen.dart';
import '../widgets/chat_widget.dart'; 
class ChatbotScreen extends StatelessWidget {
  final int kullaniciId;
  const ChatbotScreen({super.key, required this.kullaniciId});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundDark,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded),
          onPressed: () {
            Navigator.pushReplacement(
              context, 
              PageRouteBuilder(
                pageBuilder: (_, __, ___) => const HomeScreen(),
                transitionDuration: Duration.zero,
                reverseTransitionDuration: Duration.zero,
              )
            );
          },
        ),
        backgroundColor: AppTheme.cardDark,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: AppTheme.primaryGreen.withOpacity(0.2),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.smart_toy, color: AppTheme.primaryGreen, size: 20),
            ),
            const SizedBox(width: 12),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('AI Asistan', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                Text('Çevrimiçi', style: TextStyle(fontSize: 12, color: AppTheme.primaryGreen)),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.saved_search),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => SmartSearchScreen(kullaniciId: kullaniciId),
                ),
              );
            },
            tooltip: 'Akıllı Arama',
          ),
        ],
      ),
      body: ChatWidget(kullaniciId: kullaniciId), 
    );
  }
}