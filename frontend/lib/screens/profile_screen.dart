import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_provider.dart';
import '../widgets/bottom_nav_bar.dart'; 
import '../services/api_service.dart';
import 'icerik_detail_screen.dart'; 
class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});
  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}
class _ProfileScreenState extends State<ProfileScreen> {
  // _history listesi kaldırıldı, artık Provider'dan gelecek
  int _selectedTab = 0; // 0: Geçmiş, 1: İzlenecekler

  @override
  void initState() {
    super.initState();
    // Veriler zaten Provider'da olmalı, yoksa yükle
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final provider = Provider.of<AppProvider>(context, listen: false);
      if (provider.currentUser != null) {
        if (provider.userHistory.isEmpty) provider.loadUserHistory();
        provider.loadWatchlist(); // Watchlist de yükle
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final appProvider = Provider.of<AppProvider>(context);
    final user = appProvider.currentUser;

    if (user == null) {
      return const Scaffold(
        body: Center(child: Text("Giriş yapmalısınız")),
      );
    }
    
    // Provider'dan veriyi al
    final history = appProvider.userHistory;

    return Scaffold(
      backgroundColor: const Color(0xFF121212),
      appBar: AppBar(
        title: const Text('Profilim', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout, color: Colors.redAccent),
            onPressed: () {
              appProvider.logout();
              Navigator.pushReplacementNamed(context, '/login');
            },
          )
        ],
      ),
      body: SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildProfileHeader(user.kullaniciAdi, user.email ?? ''),
                  const SizedBox(height: 24),
                  _buildStatsRow(history), // History parametresi eklendi
                  const SizedBox(height: 24),
                  const SizedBox(height: 24),
                  Row(
                    children: [
                      _buildTabButton("Geçmiş", 0),
                      const SizedBox(width: 8),
                      _buildTabButton("İzlenecekler", 1),
                      const SizedBox(width: 8),
                      _buildTabButton("Okunacaklar", 2),
                    ],
                  ),
                  const SizedBox(height: 16),
                  
                  _buildContentList(history, appProvider.watchlist),
                ],
              ),
            ),
      bottomNavigationBar: const BottomNavBar(currentIndex: 2), 
    );
  }

  Widget _buildContentList(List<dynamic> history, List<dynamic> watchlist) {
    if (_selectedTab == 0) {
      // GEÇMİŞ - Kategorili ve Puan Sıralı
      if (history.isEmpty) return _buildEmptyState("Henüz aktivite yok", "İzlediklerinizi veya okuduklarınızı oylayın");

      final movies = history.where((i) => i['tur'] == 'Film').toList();
      final series = history.where((i) => i['tur'] == 'Dizi').toList();
      final books = history.where((i) => i['tur'] == 'Kitap').toList();

      // Puan sıralaması (Yüksekten düşüğe)
      movies.sort((a, b) => ((b['puan'] ?? 0) as num).compareTo((a['puan'] ?? 0) as num));
      series.sort((a, b) => ((b['puan'] ?? 0) as num).compareTo((a['puan'] ?? 0) as num));
      books.sort((a, b) => ((b['puan'] ?? 0) as num).compareTo((a['puan'] ?? 0) as num));

      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (movies.isNotEmpty) ...[
            _buildSectionHeader("🎬 Filmler"),
            _buildGroupList(movies),
            const SizedBox(height: 16),
          ],
          if (series.isNotEmpty) ...[
            _buildSectionHeader("📺 Diziler"),
            _buildGroupList(series),
            const SizedBox(height: 16),
          ],
          if (books.isNotEmpty) ...[
            _buildSectionHeader("📚 Kitaplar"),
            _buildGroupList(books),
          ],
        ],
      );
    } else if (_selectedTab == 1) {
      // İZLENECEKLER (Film & Dizi)
      final movieSeriesList = watchlist.where((item) => item['tur'] == 'Film' || item['tur'] == 'Dizi').toList();
      if (movieSeriesList.isEmpty) return _buildEmptyState("İzlenecekler listeniz boş", "Film veya dizi ekleyerek başlayın");
      return ListView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: movieSeriesList.length,
        itemBuilder: (context, index) => _buildWatchlistItem(movieSeriesList[index]),
      );
    } else {
      // OKUNACAKLAR (Kitap)
      final bookList = watchlist.where((item) => item['tur'] == 'Kitap').toList();
      if (bookList.isEmpty) return _buildEmptyState("Okuma listeniz boş", "İlginizi çeken kitapları ekleyin");
      return ListView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: bookList.length,
        itemBuilder: (context, index) => _buildWatchlistItem(bookList[index]),
      );
    }
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Text(
        title,
        style: const TextStyle(color: Colors.amber, fontSize: 18, fontWeight: FontWeight.bold),
      ),
    );
  }

  Widget _buildGroupList(List<dynamic> items) {
    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: items.length,
      itemBuilder: (context, index) => _buildHistoryItem(items[index]),
    );
  }


  Widget _buildProfileHeader(String username, String email) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF2C3E50), Color(0xFF4CA1AF)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.3),
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 35,
                backgroundColor: Colors.white.withOpacity(0.2),
                child: Text(
                  username.isNotEmpty ? username[0].toUpperCase() : '?',
                  style: const TextStyle(fontSize: 30, color: Colors.white, fontWeight: FontWeight.bold),
                ),
              ),
              const SizedBox(width: 20),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      username,
                      style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
                    const SizedBox(height: 5),
                    Text(
                      email,
                      style: const TextStyle(fontSize: 14, color: Colors.white70),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: () => _showChangePasswordDialog(context),
              icon: const Icon(Icons.lock_reset, color: Colors.white),
              label: const Text('Şifre Değiştir', style: TextStyle(color: Colors.white)),
              style: OutlinedButton.styleFrom(
                side: const BorderSide(color: Colors.white30),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showChangePasswordDialog(BuildContext context) {
    final oldPasswordController = TextEditingController();
    final newPasswordController = TextEditingController();
    
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1E1E1E),
        title: const Text('Şifre Değiştir', style: TextStyle(color: Colors.white)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: oldPasswordController,
              obscureText: true,
              style: const TextStyle(color: Colors.white),
              decoration: const InputDecoration(
                labelText: 'Mevcut Şifre',
                labelStyle: TextStyle(color: Colors.grey),
                enabledBorder: UnderlineInputBorder(borderSide: BorderSide(color: Colors.grey)),
              ),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: newPasswordController,
              obscureText: true,
              style: const TextStyle(color: Colors.white),
              decoration: const InputDecoration(
                labelText: 'Yeni Şifre',
                labelStyle: TextStyle(color: Colors.grey),
                enabledBorder: UnderlineInputBorder(borderSide: BorderSide(color: Colors.grey)),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('İptal', style: TextStyle(color: Colors.grey)),
          ),
          TextButton(
            onPressed: () async {
              if (newPasswordController.text.length < 6) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Yeni şifre en az 6 karakter olmalı')),
                );
                return;
              }
              try {
                final provider = Provider.of<AppProvider>(context, listen: false);
                if (provider.currentUser == null) return;
                
                await ApiService.changePassword(
                  provider.currentUser!.id, 
                  oldPasswordController.text, 
                  newPasswordController.text
                );
                
                if (!mounted) return;
                Navigator.pop(ctx);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Şifreniz başarıyla değiştirildi!'), backgroundColor: Colors.green),
                );
              } catch (e) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Hata: ${e.toString().replaceAll("Exception: ", "")}'), backgroundColor: Colors.red),
                );
              }
            },
            child: const Text('Kaydet', style: TextStyle(color: Colors.amber)),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsRow(List<dynamic> history) {
    int watchedCount = history.where((i) => i['tur'] == 'Film' || i['tur'] == 'Dizi').length;
    int readCount = history.where((i) => i['tur'] == 'Kitap').length;

    double avgScore = 0;
    if (history.isNotEmpty) {
      avgScore = history.fold(0.0, (sum, item) => sum + ((item['puan'] ?? 0) as num).toDouble()) / history.length;
    }
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        Expanded(child: _buildStatCard("İzlenen", "$watchedCount", Icons.movie_filter)),
        const SizedBox(width: 8),
        Expanded(child: _buildStatCard("Okunan", "$readCount", Icons.menu_book)),
        const SizedBox(width: 8),
        Expanded(child: _buildStatCard("Ort. Puan", avgScore.toStringAsFixed(1), Icons.star_half)),
      ],
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E1E1E),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        children: [
          Icon(icon, color: Colors.amber, size: 28),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: const TextStyle(fontSize: 12, color: Colors.grey),
          ),
        ],
      ),
    );
  }
  Widget _buildHistoryItem(dynamic item) {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => IcerikDetailScreen(icerikId: item['id']),
          ),
        );
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: const Color(0xFF1E1E1E),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: item['poster_url'] != null && item['poster_url'].toString().startsWith('http')
                  ? Image.network(
                      item['poster_url'],
                      width: 50,
                      height: 75,
                      fit: BoxFit.cover,
                    )
                  : Container(
                      width: 50,
                      height: 75,
                      color: Colors.grey[800],
                      child: const Icon(Icons.movie, color: Colors.white54),
                    ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    item['baslik'] ?? 'Bilinmeyen Başlık',
                    style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    item['tur'] ?? 'Genel',
                    style: TextStyle(color: Colors.amber[200], fontSize: 13),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      const Icon(Icons.star, color: Colors.amber, size: 16),
                      const SizedBox(width: 4),
                      Text(
                        "${item['puan'] ?? 0}/10",
                        style: const TextStyle(color: Colors.white70, fontWeight: FontWeight.w600),
                      ),
                    ],
                  )
                ],
              ),
            ),
            const Icon(Icons.chevron_right, color: Colors.grey),
          ],
        ),
      ),
    );
  }
  Widget _buildEmptyState([String title = "Henüz bir içerik yok", String subtitle = "Biraz keşfe çık!"]) {
    return Container(
      padding: const EdgeInsets.all(40),
      child: Column(
        children: [
          Icon(Icons.history_toggle_off, size: 60, color: Colors.grey[800]),
          const SizedBox(height: 16),
          Text(
            title,
            style: const TextStyle(color: Colors.grey, fontSize: 16),
          ),
          const SizedBox(height: 8),
          Text(
            subtitle,
            textAlign: TextAlign.center,
            style: const TextStyle(color: Colors.grey, fontSize: 12),
          ),
        ],
      ),
    );
  }

  Widget _buildTabButton(String title, int index) {
    bool isSelected = _selectedTab == index;
    return Expanded(
      child: GestureDetector(
        onTap: () => setState(() => _selectedTab = index),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: isSelected ? Colors.amber : const Color(0xFF1E1E1E),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: isSelected ? Colors.amber : Colors.white10),
          ),
          alignment: Alignment.center,
          child: Text(
            title,
            style: TextStyle(
              color: isSelected ? Colors.black : Colors.white70,
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildWatchlistItem(dynamic item) {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => IcerikDetailScreen(icerikId: item['id']),
          ),
        );
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: const Color(0xFF1E1E1E),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: item['poster_url'] != null && item['poster_url'].toString().startsWith('http')
                  ? Image.network(
                      item['poster_url'],
                      width: 50,
                      height: 75,
                      fit: BoxFit.cover,
                    )
                  : Container(
                      width: 50,
                      height: 75,
                      color: Colors.grey[800],
                      child: const Icon(Icons.movie, color: Colors.white54),
                    ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    item['baslik'] ?? 'Bilinmeyen Başlık',
                    style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    item['tur'] ?? 'Genel',
                    style: TextStyle(color: Colors.amber[200], fontSize: 13),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    "Eklendi: ${item['eklenme_tarihi']?.toString().split('T')[0] ?? ''}",
                    style: const TextStyle(color: Colors.white38, fontSize: 12),
                  ),
                ],
              ),
            ),
            IconButton(
              icon: Icon(Icons.delete_outline, color: Colors.red[300]),
              onPressed: () async {
                try {
                  await Provider.of<AppProvider>(context, listen: false).removeFromWatchlist(item['watchlist_id']);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text("Listeden çıkarıldı"), duration: Duration(seconds: 1)),
                  );
                } catch (e) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text("Hata: $e")),
                  );
                }
              },
            ),
          ],
        ),
      ),
    );
  }
}