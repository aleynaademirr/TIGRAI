class Kullanici {
  final int id;
  final String kullaniciAdi;
  final String? email;
  final bool isAdmin;
  final DateTime olusturmaTarihi;
  Kullanici({
    required this.id,
    required this.kullaniciAdi,
    this.email,
    this.isAdmin = false,
    required this.olusturmaTarihi,
  });
  factory Kullanici.fromJson(Map<String, dynamic> json) {
    return Kullanici(
      id: json['id'] as int,
      kullaniciAdi: json['kullanici_adi'] as String,
      email: json['email'] as String?,
      isAdmin: json['is_admin'] == true || json['is_admin'] == 1,
      olusturmaTarihi: DateTime.parse(json['olusturma_tarihi'] as String),
    );
  }
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'kullanici_adi': kullaniciAdi,
      'email': email,
      'is_admin': isAdmin,
      'olusturma_tarihi': olusturmaTarihi.toIso8601String(),
    };
  }
}