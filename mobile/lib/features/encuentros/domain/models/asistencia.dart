class Asistencia {
  final String id;
  final String miembroId;
  final String nombreMiembro;
  final String estado;

  Asistencia({
    required this.id,
    required this.miembroId,
    required this.nombreMiembro,
    required this.estado,
  });

  factory Asistencia.fromJson(Map<String, dynamic> json) => Asistencia(
        id: json['id'] as String,
        miembroId: json['miembro_id'] as String,
        nombreMiembro: json['nombre_miembro'] as String? ?? '',
        estado: json['estado'] as String? ?? 'no_asistio',
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'miembro_id': miembroId,
        'nombre_miembro': nombreMiembro,
        'estado': estado,
      };
}
