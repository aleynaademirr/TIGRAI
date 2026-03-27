class Puan {
  final int id;
  final int kullaniciId;
  final int icerikId;
  final int puan; 
  final DateTime puanlamaTarihi;
  Puan({
    required this.id,
    required this.kullaniciId,
    required this.icerikId,
    required this.puan,
    required this.puanlamaTarihi,
  });
  factory Puan.fromJson(Map<String, dynamic> json) {
    return Puan(
      id: json['id'] as int,
      kullaniciId: json['kullanici_id'] as int,
      icerikId: json['icerik_id'] as int,
      puan: json['puan'] as int,
      puanlamaTarihi: DateTime.parse(json['puanlama_tarihi'] as String),
    );
  }
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'kullanici_id': kullaniciId,
      'icerik_id': icerikId,
      'puan': puan,
      'puanlama_tarihi': puanlamaTarihi.toIso8601String(),
    };
  }
}