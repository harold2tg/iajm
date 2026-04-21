class Miembro {
  final String id;
  final String nombreCompleto;
  final String? fechaNacimiento;
  final String fechaIngreso;
  final String grupoId;
  final String tipo;
  final int edad;
  final String? telefonoPersonal;
  final String? nombreAcudiente;
  final String? telefonoAcudiente;

  Miembro({
    required this.id,
    required this.nombreCompleto,
    this.fechaNacimiento,
    required this.fechaIngreso,
    required this.grupoId,
    required this.tipo,
    required this.edad,
    this.telefonoPersonal,
    this.nombreAcudiente,
    this.telefonoAcudiente,
  });

  factory Miembro.fromJson(Map<String, dynamic> json) => Miembro(
        id: json['id'] as String,
        nombreCompleto: json['nombre_completo'] as String,
        fechaNacimiento: json['fecha_nacimiento'] as String?,
        fechaIngreso: json['fecha_ingreso'] as String? ?? '',
        grupoId: json['grupo_id'] as String? ?? '',
        tipo: json['tipo'] as String? ?? '',
        edad: (json['edad'] as num?)?.toInt() ?? 0,
        telefonoPersonal: json['telefono_personal'] as String?,
        nombreAcudiente: json['nombre_acudiente'] as String?,
        telefonoAcudiente: json['telefono_acudiente'] as String?,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'nombre_completo': nombreCompleto,
        'fecha_nacimiento': fechaNacimiento,
        'fecha_ingreso': fechaIngreso,
        'grupo_id': grupoId,
        'tipo': tipo,
        'edad': edad,
        'telefono_personal': telefonoPersonal,
        'nombre_acudiente': nombreAcudiente,
        'telefono_acudiente': telefonoAcudiente,
      };
}
