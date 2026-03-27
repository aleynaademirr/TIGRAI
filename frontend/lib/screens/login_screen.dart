import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_provider.dart';
import '../constants/app_theme.dart';
import '../constants/app_constants.dart';
import 'password_reset_screen.dart';
import 'home_screen.dart';
import 'admin_screen.dart';
enum AuthMode { login, register }
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}
class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _kullaniciAdiController = TextEditingController(); 
  final _emailController = TextEditingController();        
  final _passwordController = TextEditingController();     
  AuthMode _authMode = AuthMode.login;
  bool _isAdminLogin = false;
  bool _obscurePassword = true;
  @override
  void dispose() {
    _kullaniciAdiController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }
  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    final provider = Provider.of<AppProvider>(context, listen: false);
    try {
      if (_authMode == AuthMode.login) {
        await provider.login(
          _emailController.text.trim(), 
          _passwordController.text.trim()
        );
        if (mounted && provider.currentUser != null) {
           if (_isAdminLogin) {
             if (provider.currentUser!.isAdmin) {
               Navigator.of(context).pushReplacement(
                 MaterialPageRoute(builder: (context) => const AdminScreen()),
               );
             } else {
               provider.logout();
               ScaffoldMessenger.of(context).showSnackBar(
                 const SnackBar(content: Text('Bu hesap yönetici yetkisine sahip değil!'), backgroundColor: Colors.red),
               );
             }
           } else {
             Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (context) => const HomeScreen()),
            );
           }
        }
      } else {
        await provider.register(
          _kullaniciAdiController.text.trim(),
          _emailController.text.trim(),
          _passwordController.text.trim(),
        );
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Kayıt başarılı! Lütfen giriş yapın.'), backgroundColor: Colors.green),
          );
          setState(() {
            _authMode = AuthMode.login;
          });
        }
      }
    } catch (e) {
      if (mounted) {
         ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Hata: ${e.toString().replaceAll("Exception: ", "")}'), 
            backgroundColor: Colors.red
          ),
        );
      }
    }
  }
  void _switchAuthMode() {
    setState(() {
      _authMode = _authMode == AuthMode.login ? AuthMode.register : AuthMode.login;
    });
    Provider.of<AppProvider>(context, listen: false).clearError();
  }
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundDark,
      body: Container(
        decoration: BoxDecoration(
           gradient: RadialGradient(
            center: Alignment.topLeft,
            radius: 1.5,
            colors: [
              const Color(0xFF1F262E), 
              AppTheme.backgroundDark,
            ],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: Consumer<AppProvider>(
                builder: (context, provider, child) {
                  return Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      _buildLogo(),
                      const SizedBox(height: 48),
                      Container(
                        width: double.infinity,
                        constraints: const BoxConstraints(maxWidth: 400),
                        padding: const EdgeInsets.all(32),
                        decoration: BoxDecoration(
                          color: AppTheme.cardDark.withOpacity(0.9), 
                          borderRadius: BorderRadius.circular(24),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.3),
                              blurRadius: 20,
                              offset: const Offset(0, 10),
                            ),
                          ],
                          border: Border.all(color: Colors.white.withOpacity(0.05)),
                        ),
                        child: Form(
                          key: _formKey,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              Text(
                                _authMode == AuthMode.login ? 'Tekrar Hoşgeldin!' : 'Hesap Oluştur',
                                style: const TextStyle(
                                  fontSize: 24,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                ),
                                textAlign: TextAlign.center,
                              ),
                              const SizedBox(height: 8),
                              Text(
                                _authMode == AuthMode.login 
                                    ? 'Devam etmek için giriş yapın' 
                                    : 'Aramıza katılın',
                                style: TextStyle(
                                  fontSize: 14,
                                  color: Colors.grey[400],
                                ),
                                textAlign: TextAlign.center,
                              ),
                              const SizedBox(height: 32),
                              if (_authMode == AuthMode.register)
                                Column(
                                  children: [
                                    TextFormField(
                                      controller: _kullaniciAdiController,
                                      style: const TextStyle(color: Colors.white),
                                      decoration: InputDecoration(
                                        labelText: 'Kullanıcı Adı',
                                        labelStyle: const TextStyle(color: Colors.white70),
                                        prefixIcon: Icon(Icons.person_outline, color: AppTheme.primaryGreen.withOpacity(0.7)),
                                        fillColor: AppTheme.backgroundDark,
                                        filled: true,
                                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                                      ),
                                      validator: (value) {
                                        if (value == null || value.trim().isEmpty) return 'Gerekli';
                                        return null;
                                      },
                                    ),
                                    const SizedBox(height: 20),
                                  ],
                                ),
                              TextFormField(
                                controller: _emailController,
                                style: const TextStyle(color: Colors.white),
                                decoration: InputDecoration(
                                  labelText: 'E-posta',
                                  labelStyle: const TextStyle(color: Colors.white70),
                                  prefixIcon: Icon(Icons.email_outlined, color: AppTheme.primaryBlue.withOpacity(0.7)),
                                  fillColor: AppTheme.backgroundDark,
                                  filled: true,
                                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                                ),
                                keyboardType: TextInputType.emailAddress,
                                validator: (value) {
                                  if (value == null || !value.contains('@')) return 'Geçerli bir email girin';
                                  return null;
                                },
                              ),
                              const SizedBox(height: 20),
                              TextFormField(
                                controller: _passwordController,
                                style: const TextStyle(color: Colors.white),
                                obscureText: _obscurePassword,
                                decoration: InputDecoration(
                                  labelText: 'Şifre',
                                  labelStyle: const TextStyle(color: Colors.white70),
                                  prefixIcon: Icon(Icons.lock_outline, color: Colors.orange.withOpacity(0.7)),
                                  suffixIcon: IconButton(
                                    icon: Icon(_obscurePassword ? Icons.visibility_outlined : Icons.visibility_off_outlined),
                                    color: Colors.white70,
                                    onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                                  ),
                                  fillColor: AppTheme.backgroundDark,
                                  filled: true,
                                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                                ),
                                validator: (value) {
                                  if (value == null || value.length < 6) return 'En az 6 karakter';
                                  return null;
                                },
                              ),
                              const SizedBox(height: 32),
                              if (provider.error != null)
                                Container(
                                  padding: const EdgeInsets.all(12),
                                  margin: const EdgeInsets.only(bottom: 16),
                                  decoration: BoxDecoration(
                                    color: Colors.red.withOpacity(0.1),
                                    borderRadius: BorderRadius.circular(12),
                                    border: Border.all(color: Colors.red.withOpacity(0.3)),
                                  ),
                                  child: Text(
                                    provider.error!.replaceAll('Exception: ', ''),
                                    style: TextStyle(color: Colors.red[200], fontSize: 13),
                                    textAlign: TextAlign.center,
                                  ),
                                ),
                              SizedBox(
                                height: 56,
                                child: ElevatedButton(
                                  onPressed: provider.isLoading ? null : _submit,
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: _isAdminLogin
                                        ? AppTheme.primaryOrange
                                        : (_authMode == AuthMode.login 
                                            ? AppTheme.primaryGreen 
                                            : AppTheme.primaryBlue),
                                    foregroundColor: Colors.black,
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(16),
                                    ),
                                  ),
                                  child: provider.isLoading
                                      ? const CircularProgressIndicator(color: Colors.black)
                                      : Text(
                                          _authMode == AuthMode.login ? 'Giriş Yap' : 'Kayıt Ol',
                                          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                                        ),
                                ),
                              ),
                              if (_authMode == AuthMode.login) ...[
                                const SizedBox(height: 12),
                                TextButton(
                                  onPressed: () {
                                    Navigator.push(
                                      context,
                                      MaterialPageRoute(
                                        builder: (_) => const PasswordResetScreen(),
                                      ),
                                    );
                                  },
                                  child: const Text(
                                    'Şifremi Unuttum',
                                    style: TextStyle(
                                      color: AppTheme.primaryGreen,
                                      fontSize: 14,
                                    ),
                                  ),
                                ),
                              ],
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 24),
                      Column(
                        children: [
                          if (_authMode == AuthMode.login && !_isAdminLogin)
                            Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Text(
                                  'Hesabınız yok mu?',
                                  style: TextStyle(color: Colors.grey[500]),
                                ),
                                TextButton(
                                  onPressed: _switchAuthMode,
                                  child: const Text(
                                    'Hemen Kaydol',
                                    style: TextStyle(
                                      color: Colors.white,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ],
                            )
                          else if (_authMode == AuthMode.register)
                            Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Text(
                                  'Zaten hesabınız var mı?',
                                  style: TextStyle(color: Colors.grey[500]),
                                ),
                                TextButton(
                                  onPressed: _switchAuthMode,
                                  child: const Text(
                                    'Giriş Yap',
                                    style: TextStyle(
                                      color: Colors.white,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          if (_authMode == AuthMode.login)
                            TextButton(
                              onPressed: () {
                                setState(() {
                                  _isAdminLogin = !_isAdminLogin;
                                  if (_isAdminLogin) _authMode = AuthMode.login;
                                });
                              },
                              child: Text(
                                _isAdminLogin ? 'Kullanıcı Girişi' : 'Yönetici Girişi',
                                style: TextStyle(
                                  color: _isAdminLogin ? AppTheme.primaryGreen : AppTheme.primaryOrange,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                        ],
                      ),
                    ],
                  );
                },
              ),
            ),
          ),
        ),
      ),
    );
  }
  Widget _buildLogo() {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: AppTheme.primaryGreen.withOpacity(0.1),
            shape: BoxShape.circle,
            border: Border.all(color: AppTheme.primaryGreen.withOpacity(0.2), width: 2),
          ),
          child: const Icon(Icons.movie_filter_rounded, size: 64, color: AppTheme.primaryGreen),
        ),
        const SizedBox(height: 16),
        RichText(
          textAlign: TextAlign.center,
          text: const TextSpan(
            style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, letterSpacing: 1),
            children: [
              TextSpan(text: 'TIG', style: TextStyle(color: Colors.white)),
              TextSpan(text: 'RAI', style: TextStyle(color: AppTheme.primaryGreen)),
            ],
          ),
        ),
      ],
    );
  }
}