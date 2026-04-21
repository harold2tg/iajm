import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'miembros_provider.dart';

class MiembroDetailScreen extends ConsumerWidget {
  final String miembroId;
  const MiembroDetailScreen({super.key, required this.miembroId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final miembroAsync = ref.watch(miembroDetailProvider(miembroId));

    return miembroAsync.when(
      loading: () =>
          const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (e, _) => Scaffold(body: Center(child: Text('Error: $e'))),
      data: (miembro) => Scaffold(
        appBar: AppBar(
          title: Text(miembro.nombreCompleto),
          actions: [
            IconButton(
              icon: const Icon(Icons.edit),
              tooltip: 'Editar',
              onPressed: () async {
                final result = await context.push(
                  '/grupos/${miembro.grupoId}/miembros/$miembroId/edit',
                  extra: miembro,
                );
                if (result == true) {
                  ref.invalidate(miembroDetailProvider(miembroId));
                }
              },
            ),
          ],
        ),
        body: Padding(
          padding: const EdgeInsets.all(16),
          child: Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _InfoRow(label: 'Tipo', value: miembro.tipo),
                  _InfoRow(label: 'Edad', value: '${miembro.edad} años'),
                  _InfoRow(
                      label: 'Teléfono',
                      value: miembro.telefonoPersonal ?? '-'),
                  _InfoRow(
                      label: 'Acudiente',
                      value: miembro.nombreAcudiente ?? '-'),
                  _InfoRow(
                      label: 'Tel. Acudiente',
                      value: miembro.telefonoAcudiente ?? '-'),
                  _InfoRow(
                      label: 'F. Ingreso', value: miembro.fechaIngreso),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;
  const _InfoRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(label,
                style: const TextStyle(fontWeight: FontWeight.bold)),
          ),
          Expanded(
            child: Text(value),
          ),
        ],
      ),
    );
  }
}
