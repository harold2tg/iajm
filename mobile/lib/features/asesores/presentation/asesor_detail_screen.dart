import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'asesores_provider.dart';

class AsesorDetailScreen extends ConsumerWidget {
  final String asesorId;
  const AsesorDetailScreen({super.key, required this.asesorId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asesorAsync = ref.watch(asesorDetailProvider(asesorId));

    return asesorAsync.when(
      loading: () =>
          const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (e, _) => Scaffold(body: Center(child: Text('Error: $e'))),
      data: (asesor) => Scaffold(
        appBar: AppBar(
          title: Text(asesor.nombreCompleto),
          actions: [
            IconButton(
              icon: const Icon(Icons.edit),
              tooltip: 'Editar',
              onPressed: () async {
                final result = await context.push(
                  '/asesores/${asesor.id}/edit',
                  extra: asesor,
                );
                if (result == true) {
                  ref.invalidate(asesorDetailProvider(asesorId));
                }
              },
            ),
          ],
        ),
        body: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _InfoRow(
                          label: 'Teléfono', value: asesor.telefono ?? '-'),
                      _InfoRow(
                        label: 'Estado',
                        value: asesor.activo ? 'Activo' : 'Inactivo',
                      ),
                    ],
                  ),
                ),
              ),
              if (asesor.grupos.isNotEmpty) ...[
                const SizedBox(height: 16),
                Text('Grupos asignados',
                    style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                ...asesor.grupos.map((g) => Card(
                      child: ListTile(
                        leading: const Icon(Icons.group),
                        title: Text(g.nombre),
                      ),
                    )),
              ],
            ],
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
        children: [
          SizedBox(
            width: 100,
            child: Text(label,
                style: const TextStyle(fontWeight: FontWeight.bold)),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}
