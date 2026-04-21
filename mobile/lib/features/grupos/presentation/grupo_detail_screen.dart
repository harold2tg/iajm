import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'grupos_provider.dart';

class GrupoDetailScreen extends ConsumerWidget {
  final String grupoId;
  const GrupoDetailScreen({super.key, required this.grupoId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final grupoAsync = ref.watch(grupoDetailProvider(grupoId));

    return grupoAsync.when(
      loading: () => const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (e, _) => Scaffold(body: Center(child: Text('Error: $e'))),
      data: (grupo) => Scaffold(
        appBar: AppBar(
          title: Text(grupo.nombre),
          actions: [
            IconButton(
              icon: const Icon(Icons.edit),
              tooltip: 'Editar grupo',
              onPressed: () async {
                final result = await context.push(
                  '/grupos/$grupoId/edit',
                  extra: grupo,
                );
                if (result == true) {
                  ref.invalidate(grupoDetailProvider(grupoId));
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
                      Row(
                        children: [
                          const Icon(Icons.category, size: 16),
                          const SizedBox(width: 4),
                          Text('Tipo: ${grupo.tipo}'),
                        ],
                      ),
                      if (grupo.edadMinima != null || grupo.edadMaxima != null) ...[
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            const Icon(Icons.cake, size: 16),
                            const SizedBox(width: 4),
                            Text(
                              'Edad: ${grupo.edadMinima ?? '?'} - ${grupo.edadMaxima ?? '?'} años',
                            ),
                          ],
                        ),
                      ],
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () =>
                          context.go('/grupos/$grupoId/miembros'),
                      icon: const Icon(Icons.people),
                      label: const Text('Miembros'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () =>
                          context.go('/grupos/$grupoId/encuentros'),
                      icon: const Icon(Icons.event),
                      label: const Text('Encuentros'),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
