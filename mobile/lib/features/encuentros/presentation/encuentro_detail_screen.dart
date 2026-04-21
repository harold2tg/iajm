import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../data/encuentros_repository.dart';
import 'encuentros_provider.dart';

class EncuentroDetailScreen extends ConsumerStatefulWidget {
  final String encuentroId;
  const EncuentroDetailScreen({super.key, required this.encuentroId});

  @override
  ConsumerState<EncuentroDetailScreen> createState() =>
      _EncuentroDetailScreenState();
}

class _EncuentroDetailScreenState
    extends ConsumerState<EncuentroDetailScreen> {
  bool _initialized = false;

  @override
  Widget build(BuildContext context) {
    final encuentroAsync =
        ref.watch(encuentroDetailProvider(widget.encuentroId));
    final asistenciaAsync =
        ref.watch(asistenciaProvider(widget.encuentroId));
    final paseListaState =
        ref.watch(paseListaProvider(widget.encuentroId));
    final notifier =
        ref.read(paseListaProvider(widget.encuentroId).notifier);

    return encuentroAsync.when(
      loading: () =>
          const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (e, _) => Scaffold(body: Center(child: Text('Error: $e'))),
      data: (encuentro) {
        final isAbierto = encuentro.estado != 'cerrado';
        return asistenciaAsync.when(
          loading: () => const Scaffold(
              body: Center(child: CircularProgressIndicator())),
          error: (e, _) => Scaffold(body: Center(child: Text('Error: $e'))),
          data: (asistencias) {
            if (!_initialized) {
              WidgetsBinding.instance.addPostFrameCallback((_) {
                notifier.initFromAsistencia(asistencias);
                if (mounted) setState(() => _initialized = true);
              });
            }

            final presentes = paseListaState.estados.values
                .where((e) => e == 'presente' || e == 'asistio')
                .length;
            final ausentes = paseListaState.estados.values
                .where((e) => e == 'ausente' || e == 'no_asistio')
                .length;
            final total = paseListaState.estados.length;

            return Scaffold(
              appBar: AppBar(
                title: Text(encuentro.tema ?? 'Encuentro'),
                actions: [
                  IconButton(
                    icon: const Icon(Icons.edit),
                    tooltip: 'Editar',
                    onPressed: () async {
                      final result = await context.push(
                        '/grupos/${encuentro.grupoId}/encuentros/${widget.encuentroId}/edit',
                        extra: encuentro,
                      );
                      if (result == true) {
                        ref.invalidate(
                            encuentroDetailProvider(widget.encuentroId));
                      }
                    },
                  ),
                  if (isAbierto)
                    IconButton(
                      icon: const Icon(Icons.lock),
                      tooltip: 'Cerrar encuentro',
                      onPressed: () async {
                        await ref
                            .read(encuentrosRepositoryProvider)
                            .cerrar(widget.encuentroId);
                        ref.invalidate(
                            encuentroDetailProvider(widget.encuentroId));
                      },
                    )
                  else
                    IconButton(
                      icon: const Icon(Icons.lock_open),
                      tooltip: 'Reabrir encuentro',
                      onPressed: () async {
                        await ref
                            .read(encuentrosRepositoryProvider)
                            .reabrir(widget.encuentroId);
                        ref.invalidate(
                            encuentroDetailProvider(widget.encuentroId));
                      },
                    ),
                ],
              ),
              body: Column(
                children: [
                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _StatChip(
                            label: 'Presentes',
                            count: presentes,
                            color: const Color(0xFF27AE60)),
                        _StatChip(
                            label: 'Ausentes',
                            count: ausentes,
                            color: const Color(0xFFC0392B)),
                        _StatChip(
                            label: 'Total',
                            count: total,
                            color: const Color(0xFF1A4B8C)),
                      ],
                    ),
                  ),
                  Expanded(
                    child: ListView.builder(
                      itemCount: asistencias.length,
                      itemBuilder: (context, index) {
                        final asistencia = asistencias[index];
                        final estadoActual =
                            paseListaState.estados[asistencia.miembroId] ??
                                asistencia.estado;

                        return ListTile(
                          title: Text(asistencia.nombreMiembro),
                          trailing: isAbierto
                              ? SegmentedButton<String>(
                                  segments: const [
                                    ButtonSegment(
                                        value: 'asistio',
                                        icon: Icon(Icons.check, size: 16),
                                        label: Text('Sí')),
                                    ButtonSegment(
                                        value: 'no_asistio',
                                        icon: Icon(Icons.close, size: 16),
                                        label: Text('No')),
                                  ],
                                  selected: {estadoActual},
                                  onSelectionChanged: (val) {
                                    notifier.toggleEstado(
                                        asistencia.miembroId, val.first);
                                  },
                                )
                              : Chip(
                                  label: Text(estadoActual),
                                  backgroundColor: estadoActual == 'asistio'
                                      ? const Color(0xFF27AE60)
                                          .withValues(alpha: 0.2)
                                      : const Color(0xFFC0392B)
                                          .withValues(alpha: 0.2),
                                ),
                        );
                      },
                    ),
                  ),
                  if (isAbierto)
                    Padding(
                      padding: const EdgeInsets.all(16),
                      child: SizedBox(
                        width: double.infinity,
                        child: ElevatedButton(
                          onPressed: paseListaState.saving
                              ? null
                              : () => notifier.guardar(),
                          child: paseListaState.saving
                              ? const CircularProgressIndicator(
                                  color: Colors.white)
                              : const Text('Guardar Asistencia'),
                        ),
                      ),
                    ),
                ],
              ),
            );
          },
        );
      },
    );
  }
}

class _StatChip extends StatelessWidget {
  final String label;
  final int count;
  final Color color;

  const _StatChip(
      {required this.label, required this.count, required this.color});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('$count',
            style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color)),
        Text(label, style: const TextStyle(fontSize: 12)),
      ],
    );
  }
}
