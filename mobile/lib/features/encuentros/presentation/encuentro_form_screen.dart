import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../data/encuentros_repository.dart';
import '../domain/models/encuentro.dart';

class EncuentroFormScreen extends ConsumerStatefulWidget {
  final String grupoId;
  final Encuentro? encuentro; // null = crear
  const EncuentroFormScreen(
      {super.key, required this.grupoId, this.encuentro});

  @override
  ConsumerState<EncuentroFormScreen> createState() =>
      _EncuentroFormScreenState();
}

class _EncuentroFormScreenState
    extends ConsumerState<EncuentroFormScreen> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _fechaCtrl;
  late final TextEditingController _temaCtrl;
  late final TextEditingController _obsCtrl;
  bool _loading = false;

  bool get _isEditing => widget.encuentro != null;

  @override
  void initState() {
    super.initState();
    final e = widget.encuentro;
    _fechaCtrl =
        TextEditingController(text: e?.fecha ?? _todayIso());
    _temaCtrl = TextEditingController(text: e?.tema ?? '');
    _obsCtrl = TextEditingController(text: e?.observaciones ?? '');
  }

  String _todayIso() {
    final now = DateTime.now();
    return '${now.year}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')}';
  }

  @override
  void dispose() {
    _fechaCtrl.dispose();
    _temaCtrl.dispose();
    _obsCtrl.dispose();
    super.dispose();
  }

  Future<void> _pickDate() async {
    DateTime initial = DateTime.now();
    try {
      if (_fechaCtrl.text.isNotEmpty) {
        initial = DateTime.parse(_fechaCtrl.text);
      }
    } catch (_) {}
    final picked = await showDatePicker(
      context: context,
      initialDate: initial,
      firstDate: DateTime(2000),
      lastDate: DateTime(2100),
    );
    if (picked != null) {
      _fechaCtrl.text =
          '${picked.year}-${picked.month.toString().padLeft(2, '0')}-${picked.day.toString().padLeft(2, '0')}';
    }
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _loading = true);
    try {
      final data = <String, dynamic>{
        'grupo_id': widget.grupoId,
        'fecha': _fechaCtrl.text.trim(),
        if (_temaCtrl.text.isNotEmpty) 'tema': _temaCtrl.text.trim(),
        if (_obsCtrl.text.isNotEmpty)
          'observaciones': _obsCtrl.text.trim(),
      };
      final repo = ref.read(encuentrosRepositoryProvider);
      if (_isEditing) {
        await repo.update(widget.encuentro!.id, data);
      } else {
        await repo.create(data);
      }
      if (mounted) context.pop(true);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_isEditing ? 'Editar Encuentro' : 'Nuevo Encuentro'),
        actions: [
          if (_loading)
            const Padding(
              padding: EdgeInsets.all(16),
              child: SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2)),
            )
          else
            TextButton(onPressed: _save, child: const Text('Guardar')),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            TextFormField(
              controller: _fechaCtrl,
              decoration: const InputDecoration(
                  labelText: 'Fecha *', hintText: 'YYYY-MM-DD'),
              readOnly: true,
              onTap: _pickDate,
              validator: (v) =>
                  v == null || v.trim().isEmpty ? 'Requerido' : null,
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _temaCtrl,
              decoration: const InputDecoration(labelText: 'Tema'),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _obsCtrl,
              decoration:
                  const InputDecoration(labelText: 'Observaciones'),
              maxLines: 3,
            ),
          ],
        ),
      ),
    );
  }
}
