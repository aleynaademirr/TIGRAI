import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../constants/app_theme.dart';
import '../constants/app_constants.dart';
import '../widgets/bottom_nav_bar.dart';

class AdminScreen extends StatefulWidget {
  const AdminScreen({super.key});

  @override
  State<AdminScreen> createState() => _AdminScreenState();
}

class _AdminScreenState extends State<AdminScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  Map<String, dynamic>? _stats;
  List<dynamic> _users = [];
  List<dynamic> _activities = [];
  bool _isLoading = true;
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      await Future.wait([
        _loadStats(),
        _loadUsers(),
        _loadActivities(),
      ]);
    } catch (e) {
      print('Veri yükleme hatası: $e');
    }
    setState(() => _isLoading = false);
  }

  Future<void> _loadStats() async {
    try {
      final response = await http.get(Uri.parse('${AppConstants.baseUrl}/admin/api/stats'));
      if (response.statusCode == 200) {
        setState(() => _stats = json.decode(response.body));
      }
    } catch (e) {
      print('İstatistik yükleme hatası: $e');
    }
  }

  Future<void> _loadUsers() async {
    try {
      final response = await http.get(Uri.parse('${AppConstants.baseUrl}/admin/api/users'));
      if (response.statusCode == 200) {
        setState(() => _users = json.decode(response.body));
      }
    } catch (e) {
      print('Kullanıcı yükleme hatası: $e');
    }
  }

  Future<void> _loadActivities() async {
    try {
      final response = await http.get(Uri.parse('${AppConstants.baseUrl}/admin/api/recent-activity'));
      if (response.statusCode == 200) {
        setState(() => _activities = json.decode(response.body));
      }
    } catch (e) {
      print('Aktivite yükleme hatası: $e');
    }
  }

  Future<void> _deleteUser(int userId) async {
    try {
      final response = await http.delete(Uri.parse('${AppConstants.baseUrl}/admin/api/users/$userId'));
      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Kullanıcı silindi ✅'), backgroundColor: Colors.green),
        );
        _loadUsers();
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Hata: $e'), backgroundColor: Colors.red),
      );
    }
  }

  Future<void> _toggleAdmin(int userId) async {
    try {
      final response = await http.post(Uri.parse('${AppConstants.baseUrl}/admin/api/users/$userId/toggle-admin'));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(data['message']), backgroundColor: Colors.green),
        );
        _loadUsers();
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Hata: $e'), backgroundColor: Colors.red),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundDark,
      appBar: AppBar(
        automaticallyImplyLeading: false,
        backgroundColor: AppTheme.cardDark,
        elevation: 0,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [AppTheme.primaryOrange, AppTheme.primaryOrange.withOpacity(0.6)],
                ),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.admin_panel_settings, color: Colors.white, size: 20),
            ),
            const SizedBox(width: 12),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Admin Paneli', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
                Text('Yönetim Konsolu', style: TextStyle(color: Colors.white54, fontSize: 11)),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: AppTheme.primaryGreen),
            tooltip: 'Yenile',
            onPressed: _loadData,
          ),
          const SizedBox(width: 8),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: AppTheme.primaryOrange,
          labelColor: AppTheme.primaryOrange,
          unselectedLabelColor: Colors.white54,
          tabs: const [
            Tab(icon: Icon(Icons.dashboard), text: 'Dashboard'),
            Tab(icon: Icon(Icons.people), text: 'Kullanıcılar'),
            Tab(icon: Icon(Icons.history), text: 'Aktivite'),
          ],
        ),
      ),
      body: _isLoading
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const CircularProgressIndicator(color: AppTheme.primaryOrange),
                  const SizedBox(height: 16),
                  Text('Yükleniyor...', style: TextStyle(color: Colors.white.withOpacity(0.7))),
                ],
              ),
            )
          : TabBarView(
              controller: _tabController,
              children: [
                _buildDashboard(),
                _buildUsersTab(),
                _buildActivityTab(),
              ],
            ),
      bottomNavigationBar: const BottomNavBar(currentIndex: 3),
    );
  }

  Widget _buildDashboard() {
    if (_stats == null) {
      return const Center(child: Text('İstatistikler yüklenemedi', style: TextStyle(color: Colors.white54)));
    }

    return RefreshIndicator(
      onRefresh: _loadStats,
      color: AppTheme.primaryOrange,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Genel Bakış',
              style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            GridView.count(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisCount: 2,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
              childAspectRatio: 1.5,
              children: [
                _buildStatCard('Toplam İçerik', _stats!['total_content'].toString(), Icons.movie_filter, AppTheme.primaryGreen),
                _buildStatCard('Kullanıcılar', _stats!['total_users'].toString(), Icons.people, AppTheme.primaryBlue),
                _buildStatCard('Puanlar', _stats!['total_ratings'].toString(), Icons.star, Colors.amber),
                _buildStatCard('Yorumlar', _stats!['total_comments'].toString(), Icons.comment, AppTheme.primaryOrange),
              ],
            ),
            const SizedBox(height: 24),
            const Text(
              'İçerik Dağılımı',
              style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            _buildContentDistribution(),
          ],
        ),
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [color.withOpacity(0.2), color.withOpacity(0.05)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: color, size: 32),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(color: color, fontSize: 28, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: const TextStyle(color: Colors.white70, fontSize: 12),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildContentDistribution() {
    final contentByType = _stats!['content_by_type'];
    final total = contentByType['movies'] + contentByType['series'] + contentByType['books'];
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        children: [
          _buildDistributionRow('Filmler', contentByType['movies'], total, AppTheme.primaryGreen),
          const Divider(color: Colors.white10, height: 24),
          _buildDistributionRow('Diziler', contentByType['series'], total, AppTheme.primaryBlue),
          const Divider(color: Colors.white10, height: 24),
          _buildDistributionRow('Kitaplar', contentByType['books'], total, AppTheme.primaryOrange),
        ],
      ),
    );
  }

  Widget _buildDistributionRow(String label, int count, int total, Color color) {
    final percentage = total > 0 ? (count / total * 100).toStringAsFixed(1) : '0.0';
    
    return Row(
      children: [
        Expanded(
          flex: 2,
          child: Text(label, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w500)),
        ),
        Expanded(
          flex: 3,
          child: ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              value: total > 0 ? count / total : 0,
              backgroundColor: Colors.white10,
              valueColor: AlwaysStoppedAnimation(color),
              minHeight: 8,
            ),
          ),
        ),
        const SizedBox(width: 12),
        Text('$count', style: TextStyle(color: color, fontWeight: FontWeight.bold)),
        const SizedBox(width: 4),
        Text('($percentage%)', style: const TextStyle(color: Colors.white54, fontSize: 12)),
      ],
    );
  }

  Widget _buildUsersTab() {
    final filteredUsers = _searchQuery.isEmpty
        ? _users
        : _users.where((user) {
            final name = user['kullanici_adi'].toString().toLowerCase();
            final email = user['email'].toString().toLowerCase();
            final query = _searchQuery.toLowerCase();
            return name.contains(query) || email.contains(query);
          }).toList();

    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: TextField(
            onChanged: (value) => setState(() => _searchQuery = value),
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              hintText: 'Kullanıcı ara...',
              hintStyle: const TextStyle(color: Colors.white54),
              prefixIcon: const Icon(Icons.search, color: Colors.white54),
              filled: true,
              fillColor: AppTheme.cardDark,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide.none,
              ),
            ),
          ),
        ),
        Expanded(
          child: RefreshIndicator(
            onRefresh: _loadUsers,
            color: AppTheme.primaryOrange,
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: filteredUsers.length,
              itemBuilder: (context, index) {
                final user = filteredUsers[index];
                return _buildUserCard(user);
              },
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildUserCard(Map<String, dynamic> user) {
    final isAdmin = user['is_admin'] == true;
    
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isAdmin ? AppTheme.primaryOrange.withOpacity(0.3) : Colors.white10,
        ),
      ),
      child: Column(
        children: [
          ListTile(
            contentPadding: const EdgeInsets.all(16),
            leading: CircleAvatar(
              radius: 24,
              backgroundColor: isAdmin ? AppTheme.primaryOrange : AppTheme.primaryBlue,
              child: Text(
                user['kullanici_adi'][0].toUpperCase(),
                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 20),
              ),
            ),
            title: Row(
              children: [
                Expanded(
                  child: Text(
                    user['kullanici_adi'],
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                  ),
                ),
                if (isAdmin)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppTheme.primaryOrange.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: AppTheme.primaryOrange),
                    ),
                    child: const Text(
                      'ADMIN',
                      style: TextStyle(color: AppTheme.primaryOrange, fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ),
              ],
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 4),
                Text(user['email'], style: const TextStyle(color: Colors.white70, fontSize: 13)),
                const SizedBox(height: 8),
                Row(
                  children: [
                    _buildUserStat(Icons.star, user['rating_count'].toString(), Colors.amber),
                    const SizedBox(width: 16),
                    _buildUserStat(Icons.comment, user['comment_count'].toString(), AppTheme.primaryBlue),
                  ],
                ),
              ],
            ),
          ),
          const Divider(color: Colors.white10, height: 1),
          Padding(
            padding: const EdgeInsets.all(8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton.icon(
                  onPressed: () => _toggleAdmin(user['id']),
                  icon: Icon(
                    isAdmin ? Icons.remove_moderator : Icons.admin_panel_settings,
                    size: 18,
                    color: AppTheme.primaryOrange,
                  ),
                  label: Text(
                    isAdmin ? 'Admin Kaldır' : 'Admin Yap',
                    style: const TextStyle(color: AppTheme.primaryOrange),
                  ),
                ),
                const SizedBox(width: 8),
                TextButton.icon(
                  onPressed: isAdmin ? null : () => _showDeleteDialog(user),
                  icon: const Icon(Icons.delete_outline, size: 18),
                  label: const Text('Sil'),
                  style: TextButton.styleFrom(
                    foregroundColor: isAdmin ? Colors.grey : Colors.red,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildUserStat(IconData icon, String value, Color color) {
    return Row(
      children: [
        Icon(icon, size: 16, color: color),
        const SizedBox(width: 4),
        Text(value, style: TextStyle(color: color, fontWeight: FontWeight.w600, fontSize: 12)),
      ],
    );
  }

  void _showDeleteDialog(Map<String, dynamic> user) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppTheme.cardDark,
        title: const Text('Kullanıcıyı Sil', style: TextStyle(color: Colors.white)),
        content: Text(
          '${user['kullanici_adi']} kullanıcısını silmek istediğinize emin misiniz? Bu işlem geri alınamaz.',
          style: const TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('İptal', style: TextStyle(color: Colors.white54)),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _deleteUser(user['id']);
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Sil'),
          ),
        ],
      ),
    );
  }

  Widget _buildActivityTab() {
    return RefreshIndicator(
      onRefresh: _loadActivities,
      color: AppTheme.primaryOrange,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _activities.length,
        itemBuilder: (context, index) {
          final activity = _activities[index];
          return _buildActivityCard(activity);
        },
      ),
    );
  }

  Widget _buildActivityCard(Map<String, dynamic> activity) {
    final isComment = activity['type'] == 'comment';
    final icon = isComment ? Icons.comment : Icons.star;
    final color = isComment ? AppTheme.primaryBlue : Colors.amber;
    
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white10),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withOpacity(0.2),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      activity['user'],
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      isComment ? 'yorum yaptı' : 'puan verdi',
                      style: const TextStyle(color: Colors.white54, fontSize: 12),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  activity['content'],
                  style: TextStyle(color: color, fontSize: 13),
                ),
                if (isComment) ...[
                  const SizedBox(height: 4),
                  Text(
                    activity['text'],
                    style: const TextStyle(color: Colors.white70, fontSize: 12),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ] else ...[
                  const SizedBox(height: 4),
                  Row(
                    children: List.generate(
                      10,
                      (i) => Icon(
                        i < activity['rating'] ? Icons.star : Icons.star_border,
                        color: Colors.amber,
                        size: 14,
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}