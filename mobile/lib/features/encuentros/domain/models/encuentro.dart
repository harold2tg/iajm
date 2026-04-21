class Encuentro {
  final String id;
  final String grupoId;
  final String fecha;
  final String? tema;
  final String? observaciones;
  final String estado;

  Encuentro({
    required this.id,
    required this.grupoId,
    required this.fecha,
    this.tema,
    this.observaciones,
    required this.estado,
  });

  factory Encuentro.fromJson(Map<String, dynamic> json) => Encuentro(
        id: json['id'] as String,
        grupoId: json['grupo_id'] as String? ?? '',
        fecha: json['fecha'] as String? ?? '',
        tema: json['tema'] as String?,
        observaciones: json['observaciones'] as String?,
        estado: json['estado'] as String? ?? 'abierto',
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'grupo_id': grupoId,
        'fecha': fecha,
        'tema': tema,
        'observaciones': observaciones,
        'estado': estado,
      };
}
