import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:ui';
import '../providers/app_provider.dart';
import '../models/icerik.dart';
import '../constants/app_theme.dart';
import 'login_screen.dart';
import '../widgets/content_card.dart';
import '../widgets/hero_carousel.dart';
import '../widgets/bottom_nav_bar.dart';
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}
class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';
  String? _selectedCategory;
  @override
  void initState() {
    super.initState();
    final provider = Provider.of<AppProvider>(context, listen: false);
    if (provider.currentUser == null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => const LoginScreen()),
        );
      });
    } else {
      provider.loadIcerikler();
    }
  }
  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: _buildAppBar(),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              AppTheme.backgroundDark,
              Color(0xFF0D1012),
            ],
          ),
        ),
        child: SafeArea(
          bottom: false,
          child: Consumer<AppProvider>(
            builder: (context, provider, child) {
              if (provider.isLoading && provider.icerikler.isEmpty) {
                return const Center(child: CircularProgressIndicator());
              }
              if (provider.error != null) {
                return Center(child: Text(provider.error!, style: const TextStyle(color: Colors.white)));
              }
              final allContent = provider.icerikler;
              if (_searchQuery.isNotEmpty) {
                final searchResults = provider.searchIcerikler(_searchQuery);
                return _buildSearchResults(searchResults);
              }
              final movies = allContent.where((i) => i.tur == 'Film').toList();
              final series = allContent.where((i) => i.tur == 'Dizi').toList();
              final books = allContent.where((i) => i.tur == 'Kitap').toList();
              movies.sort((a, b) => (b.imdbPuani ?? 0).compareTo(a.imdbPuani ?? 0));
              series.sort((a, b) => (b.imdbPuani ?? 0).compareTo(a.imdbPuani ?? 0));
              books.sort((a, b) => (b.imdbPuani ?? 0).compareTo(a.imdbPuani ?? 0));
              if (_selectedCategory != null) {
                  List<Icerik> filteredContent;
                  if (_selectedCategory == 'Film') {
                    filteredContent = movies;
                  } else if (_selectedCategory == 'Dizi') filteredContent = series;
                  else filteredContent = books;
                  return Column(
                    children: [
                      _buildStatsAndFilters(movies.length, series.length, books.length),
                      Expanded(
                        child: GridView.builder(
                          padding: const EdgeInsets.all(16),
                          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount: 3,
                            childAspectRatio: 0.65,
                            crossAxisSpacing: 12,
                            mainAxisSpacing: 12,
                          ),
                          itemCount: filteredContent.length,
                          itemBuilder: (context, index) => ContentCard(icerik: filteredContent[index], showTitle: false),
                        ),
                      ),
                    ],
                  );
              }
              return ListView(
                padding: const EdgeInsets.only(bottom: 80),
                children: [
                   HeroCarousel(icerikler: allContent),
                  _buildStatsAndFilters(movies.length, series.length, books.length),
                  _buildSectionHeader('Popüler Filmler', Icons.movie, AppTheme.primaryGreen),
                  _buildHorizontalContentList(movies),
                  _buildSectionHeader('En İyi Diziler', Icons.tv, AppTheme.primaryBlue),
                  _buildHorizontalContentList(series),
                  _buildSectionHeader('Önerilen Kitaplar', Icons.book, AppTheme.primaryOrange),
                  _buildHorizontalContentList(books, isBook: true),
                   const SizedBox(height: 20),
                ],
              );
            },
          ),
        ),
      ),
      bottomNavigationBar: const BottomNavBar(currentIndex: 0),
    );
  }
  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      backgroundColor: AppTheme.backgroundDark.withOpacity(0.9),
      flexibleSpace: ClipRRect(
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: Container(color: Colors.transparent),
        ),
      ),
      title: Container(
        height: 40,
        decoration: BoxDecoration(
          color: AppTheme.cardDark,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: Colors.white10),
        ),
        child: TextField(
          controller: _searchController,
          onChanged: (val) => setState(() => _searchQuery = val),
          style: const TextStyle(color: Colors.white),
          decoration: InputDecoration(
            hintText: 'Film, dizi, kitap ara...',
            hintStyle: TextStyle(color: Colors.grey[500], fontSize: 14),
            prefixIcon: Icon(Icons.search, color: Colors.grey[400], size: 20),
            suffixIcon: _searchQuery.isNotEmpty 
              ? IconButton(
                  icon: const Icon(Icons.clear, size: 18, color: Colors.white54),
                  onPressed: () {
                    _searchController.clear();
                    setState(() => _searchQuery = '');
                  },
                )
              : null,
            border: InputBorder.none,
            enabledBorder: InputBorder.none,
            focusedBorder: InputBorder.none,
            contentPadding: const EdgeInsets.symmetric(vertical: 0, horizontal: 16),
          ),
          textAlignVertical: TextAlignVertical.center,
        ),
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.logout),
          onPressed: () {
            Provider.of<AppProvider>(context, listen: false).logout();
            Navigator.pushReplacement(
              context, 
              MaterialPageRoute(builder: (_) => const LoginScreen())
            );
          },
        ),
      ],
    );
  }
  Widget _buildSearchResults(List<Icerik> results) {
     if (results.isEmpty) {
        return const Center(child: Text("Sonuç bulunamadı", style: TextStyle(color: Colors.white54)));
     }
     return GridView.builder(
        padding: const EdgeInsets.all(16),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 3,
          childAspectRatio: 0.65,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
        ),
        itemCount: results.length,
        itemBuilder: (context, index) {
          return ContentCard(icerik: results[index], showTitle: false);
        },
     );
  }
  Widget _buildStatsAndFilters(int films, int series, int books) {
    return Container(
      height: 50,
      margin: const EdgeInsets.symmetric(vertical: 12),
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        children: [
          _buildFilterChip('Tümü', null, selected: _selectedCategory == null),
          _buildFilterChip('Filmler', 'Film', count: films, color: AppTheme.primaryGreen, selected: _selectedCategory == 'Film'),
          _buildFilterChip('Diziler', 'Dizi', count: series, color: AppTheme.primaryBlue, selected: _selectedCategory == 'Dizi'),
          _buildFilterChip('Kitaplar', 'Kitap', count: books, color: AppTheme.primaryOrange, selected: _selectedCategory == 'Kitap'),
        ],
      ),
    );
  }
  Widget _buildFilterChip(String label, String? type, {int? count, Color? color, bool selected = false}) {
    final activeColor = color ?? Colors.white;
    return GestureDetector(
      onTap: () => setState(() => _selectedCategory = type),
      child: Container(
        margin: const EdgeInsets.only(right: 12),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: selected ? activeColor.withOpacity(0.2) : AppTheme.cardDark,
          border: Border.all(
            color: selected ? activeColor : Colors.transparent,
            width: 1.5,
          ),
          borderRadius: BorderRadius.circular(25),
        ),
        child: Row(
          children: [
            Text(
              label,
              style: TextStyle(
                color: selected ? activeColor : Colors.white70,
                fontWeight: selected ? FontWeight.bold : FontWeight.w500,
                fontSize: 13,
              ),
            ),
            if (count != null) ...[
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.black26,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  '$count',
                  style: TextStyle(
                    fontSize: 10,
                    color: selected ? activeColor : Colors.grey[400],
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ]
          ],
        ),
      ),
    );
  }
  Widget _buildSectionHeader(String title, IconData icon, Color color) {
    String? categoryToSelect;
    if (title.contains('Film')) {
      categoryToSelect = 'Film';
    } else if (title.contains('Dizi')) categoryToSelect = 'Dizi';
    else if (title.contains('Kitap')) categoryToSelect = 'Kitap';
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 24, 16, 12),
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 8),
          Text(
            title,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
              letterSpacing: 0.5,
            ),
          ),
          const Spacer(),
          GestureDetector(
            onTap: () {
               if (categoryToSelect != null) {
                 setState(() {
                   _selectedCategory = categoryToSelect;
                 });
               }
            },
            child: Text(
              'Tümünü Gör',
              style: TextStyle(
                color: color.withOpacity(0.8),
                fontSize: 12,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }
  Widget _buildHorizontalContentList(List<Icerik> contents, {bool isBook = false}) {
    if (contents.isEmpty) {
        return const Padding(
            padding: EdgeInsets.symmetric(horizontal: 16),
            child: Text("Bu kategoride içerik bulunamadı.", style: TextStyle(color: Colors.white38)),
        );
    }
    return SizedBox(
      height: isBook ? 200 : 240, 
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: contents.length,
        itemBuilder: (context, index) {
          return ContentCard(
            icerik: contents[index], 
            width: 130, 
            height: 190,
          );
        },
      ),
    );
  }
}