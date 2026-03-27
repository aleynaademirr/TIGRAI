class Icerik {
  final int id;
  final String baslik;
  final String tur; 
  final String? kategoriler;
  final String? ozet;
  final String? posterUrl;
  final int? yil;
  final double? imdbPuani;
  final DateTime? olusturmaTarihi;
  Icerik({
    required this.id,
    required this.baslik,
    required this.tur,
    this.kategoriler,
    this.ozet,
    this.posterUrl,
    this.yil,
    this.imdbPuani,
    this.olusturmaTarihi,
  });
  factory Icerik.fromJson(Map<String, dynamic> json) {
    return Icerik(
      id: json['id'] as int,
      baslik: json['baslik'] as String,
      tur: json['tur'] as String,
      kategoriler: json['kategoriler'] as String?,
      ozet: json['ozet'] as String?,
      posterUrl: json['poster_url'] as String?,
      yil: json['yil'] as int?,
      imdbPuani: json['imdb_puani'] != null ? (json['imdb_puani'] as num).toDouble() : null,
      olusturmaTarihi: json['olusturma_tarihi'] != null ? DateTime.parse(json['olusturma_tarihi'] as String) : null,
    );
  }
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'baslik': baslik,
      'tur': tur,
      'kategoriler': kategoriler,
      'ozet': ozet,
      'poster_url': posterUrl,
      'yil': yil,
      'imdb_puani': imdbPuani,
      'olusturma_tarihi': olusturmaTarihi?.toIso8601String(),
    };
  }
}