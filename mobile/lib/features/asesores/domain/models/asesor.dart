class AsesorGrupo {
  final String id;
  final String nombre;

  AsesorGrupo({required this.id, required this.nombre});

  factory AsesorGrupo.fromJson(Map<String, dynamic> json) => AsesorGrupo(
        id: json['id'] as String,
        nombre: json['nombre'] as String,
      );
}

class Asesor {
  final String id;
  final String nombreCompleto;
  final String? telefono;
  final bool activo;
  final List<AsesorGrupo> grupos;

  Asesor({
    required this.id,
    required this.nombreCompleto,
    this.telefono,
    required this.activo,
    required this.grupos,
  });

  factory Asesor.fromJson(Map<String, dynamic> json) => Asesor(
        id: json['id'] as String,
        nombreCompleto: json['nombre_completo'] as String,
        telefono: json['telefono'] as String?,
        activo: json['activo'] as bool? ?? true,
        grupos: (json['grupos'] as List<dynamic>?)
                ?.map((e) => AsesorGrupo.fromJson(e as Map<String, dynamic>))
                .toList() ??
            [],
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'nombre_completo': nombreCompleto,
        'telefono': telefono,
        'activo': activo,
        'grupos': grupos.map((g) => {'id': g.id, 'nombre': g.nombre}).toList(),
      };
}
