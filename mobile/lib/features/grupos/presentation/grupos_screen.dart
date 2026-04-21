import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'grupos_provider.dart';

class GruposScreen extends ConsumerWidget {
  const GruposScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final gruposAsync = ref.watch(gruposProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Grupos')),
      body: gruposAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 48, color: Colors.red),
              const SizedBox(height: 8),
              Text('Error: $e'),
              TextButton(
                onPressed: () => ref.refresh(gruposProvider),
                child: const Text('Reintentar'),
              ),
            ],
          ),
        ),
        data: (grupos) => RefreshIndicator(
          onRefresh: () => ref.refresh(gruposProvider.future),
          child: grupos.isEmpty
              ? const Center(child: Text('No hay grupos disponibles'))
              : ListView.builder(
                  itemCount: grupos.length,
                  itemBuilder: (context, i) {
                    final g = grupos[i];
                    return ListTile(
                      leading: const CircleAvatar(
                          child: Icon(Icons.group)),
                      title: Text(g.nombre),
                      subtitle: Text(g.tipo),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () => context.go('/grupos/${g.id}'),
                    );
                  },
                ),
        ),
      ),
    );
  }
}
