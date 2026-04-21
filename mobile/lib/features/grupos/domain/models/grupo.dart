class Grupo {
  final String id;
  final String nombre;
  final String tipo;
  final int? edadMinima;
  final int? edadMaxima;

  Grupo({
    required this.id,
    required this.nombre,
    required this.tipo,
    this.edadMinima,
    this.edadMaxima,
  });

  factory Grupo.fromJson(Map<String, dynamic> json) => Grupo(
        id: json['id'] as String,
        nombre: json['nombre'] as String,
        tipo: json['tipo'] as String? ?? '',
        edadMinima: json['edad_minima'] as int?,
        edadMaxima: json['edad_maxima'] as int?,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'nombre': nombre,
        'tipo': tipo,
        'edad_minima': edadMinima,
        'edad_maxima': edadMaxima,
      };
}
