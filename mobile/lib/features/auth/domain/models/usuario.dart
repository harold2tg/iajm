class Usuario {
  final String id;
  final String email;
  final String nombreCompleto;
  final List<String> roles;

  Usuario({
    required this.id,
    required this.email,
    required this.nombreCompleto,
    required this.roles,
  });

  factory Usuario.fromJson(Map<String, dynamic> json) => Usuario(
        id: json['id'] as String,
        email: json['email'] as String,
        nombreCompleto:
            json['nombre_completo'] as String? ?? json['email'] as String,
        roles: (json['roles'] as List<dynamic>?)
                ?.map((e) => e.toString())
                .toList() ??
            [],
      );
}
