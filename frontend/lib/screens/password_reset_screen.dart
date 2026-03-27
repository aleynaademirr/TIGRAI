import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../constants/app_theme.dart';
class PasswordResetScreen extends StatefulWidget {
  const PasswordResetScreen({super.key});
  @override
  _PasswordResetScreenState createState() => _PasswordResetScreenState();
}
class _PasswordResetScreenState extends State<PasswordResetScreen> {
  final _emailController = TextEditingController();
  final _tokenController = TextEditingController();
  final _newPasswordController = TextEditingController();
  final bool _isLoading = false;
  bool _emailSent = false;
  String? _errorMessage;
  @override
  void dispose() {
    _emailController.dispose();
    _tokenController.dispose();
    _newPasswordController.dispose();
    super.dispose();
  }
  Future<void> _sendResetEmail() async {
    if (_emailController.text.trim().isEmpty) {
      _showErrorDialog('Email adresi gerekli');
      return;
    }
    _showLoadingDialog();
    try {
      final response = await ApiService.forgotPassword(_emailController.text.trim());
      if (!mounted) return;
      Navigator.pop(context); 
      setState(() {
        _emailSent = true;
      });
      if (!mounted) return;
      _showSuccessDialog(response['message'] ?? 'Kod gönderildi');
    } catch (e) {
      if (!mounted) return;
      Navigator.pop(context); 
      _showErrorDialog(e.toString().replaceAll("Exception: ", ""));
    }
  }
  Future<void> _resetPassword() async {
    if (_tokenController.text.trim().isEmpty || _newPasswordController.text.trim().isEmpty) {
      _showErrorDialog('Tüm alanları doldurun');
      return;
    }
    if (_newPasswordController.text.length < 6) {
      _showErrorDialog('Şifre en az 6 karakter olmalı');
      return;
    }
    _showLoadingDialog();
    try {
      final response = await ApiService.resetPassword(
        _tokenController.text.trim(),
        _newPasswordController.text.trim(),
      );
      if (!mounted) return;
      Navigator.pop(context); 
      await _showSuccessDialog(response['message'] ?? 'Şifre değiştirildi', closeScreen: true);
    } catch (e) {
      if (!mounted) return;
      Navigator.pop(context); 
      _showErrorDialog(e.toString().replaceAll("Exception: ", ""));
    }
  }
  void _showLoadingDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => const Center(
        child: Card(
          color: AppTheme.cardDark,
          child: Padding(
            padding: EdgeInsets.all(20),
            child: CircularProgressIndicator(color: AppTheme.primaryGreen),
          ),
        ),
      ),
    );
  }
  Future<void> _showSuccessDialog(String message, {bool closeScreen = false}) async {
    await showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppTheme.cardDark,
        title: const Text('Başarılı', style: TextStyle(color: AppTheme.primaryGreen)),
        content: Text(message, style: const TextStyle(color: Colors.white)),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(ctx);
              if (closeScreen) Navigator.pop(context);
            },
            child: const Text('Tamam', style: TextStyle(color: AppTheme.primaryBlue)),
          ),
        ],
      ),
    );
  }
  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppTheme.cardDark,
        title: const Text('Hata', style: TextStyle(color: Colors.red)),
        content: Text(message, style: const TextStyle(color: Colors.white)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Tamam', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundDark,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text('Şifremi Unuttum'),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 20),
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: AppTheme.primaryGreen.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.lock_reset,
                  size: 60,
                  color: AppTheme.primaryGreen,
                ),
              ),
              const SizedBox(height: 30),
              Text(
                _emailSent ? 'Kodu Girin' : 'Email Adresiniz',
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 10),
              Text(
                _emailSent
                    ? 'Email adresinize gönderilen 8 haneli kodu girin'
                    : 'Şifre sıfırlama kodu göndereceğiz',
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[400],
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 40),
              if (_errorMessage != null)
                Container(
                  padding: const EdgeInsets.all(12),
                  margin: const EdgeInsets.only(bottom: 20),
                  decoration: BoxDecoration(
                    color: Colors.red.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.red.withOpacity(0.3)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.error_outline, color: Colors.red, size: 20),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          _errorMessage!,
                          style: const TextStyle(color: Colors.red),
                        ),
                      ),
                    ],
                  ),
                ),
              if (!_emailSent) ...[
                TextField(
                  controller: _emailController,
                  keyboardType: TextInputType.emailAddress,
                  style: const TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    labelText: 'Email',
                    labelStyle: TextStyle(color: Colors.grey[400]),
                    prefixIcon: const Icon(Icons.email, color: AppTheme.primaryGreen),
                    filled: true,
                    fillColor: AppTheme.cardDark,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide.none,
                    ),
                  ),
                ),
              ] else ...[
                TextField(
                  controller: _tokenController,
                  style: const TextStyle(color: Colors.white, fontSize: 18, letterSpacing: 2),
                  textAlign: TextAlign.center,
                  decoration: InputDecoration(
                    labelText: 'Sıfırlama Kodu',
                    labelStyle: TextStyle(color: Colors.grey[400]),
                    hintText: 'ABCD1234',
                    hintStyle: TextStyle(color: Colors.grey[600]),
                    filled: true,
                    fillColor: AppTheme.cardDark,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide.none,
                    ),
                  ),
                ),
                const SizedBox(height: 20),
                TextField(
                  controller: _newPasswordController,
                  obscureText: true,
                  style: const TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    labelText: 'Yeni Şifre',
                    labelStyle: TextStyle(color: Colors.grey[400]),
                    prefixIcon: const Icon(Icons.lock, color: AppTheme.primaryGreen),
                    filled: true,
                    fillColor: AppTheme.cardDark,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide.none,
                    ),
                  ),
                ),
              ],
              const SizedBox(height: 30),
              ElevatedButton(
                onPressed: _isLoading ? null : (_emailSent ? _resetPassword : _sendResetEmail),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primaryGreen,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: _isLoading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      )
                    : Text(
                        _emailSent ? 'Şifreyi Değiştir' : 'Kod Gönder',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.black,
                        ),
                      ),
              ),
              const SizedBox(height: 20),
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text(
                  'Giriş ekranına dön',
                  style: TextStyle(color: AppTheme.primaryGreen),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}