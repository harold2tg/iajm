import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../data/miembros_repository.dart';
import '../domain/models/miembro.dart';

class MiembroFormScreen extends ConsumerStatefulWidget {
  final String grupoId;
  final Miembro? miembro; // null = crear
  const MiembroFormScreen({super.key, required this.grupoId, this.miembro});

  @override
  ConsumerState<MiembroFormScreen> createState() =>
      _MiembroFormScreenState();
}

class _MiembroFormScreenState extends ConsumerState<MiembroFormScreen> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _nombreCtrl;
  late final TextEditingController _fechaNacCtrl;
  late final TextEditingController _fechaIngCtrl;
  late final TextEditingController _telefonoCtrl;
  late final TextEditingController _acudienteCtrl;
  late final TextEditingController _telAcudienteCtrl;
  late String _tipo;
  bool _loading = false;

  static const _tipos = ['infancia', 'adolescencia', 'juventud'];

  bool get _isEditing => widget.miembro != null;

  @override
  void initState() {
    super.initState();
    final m = widget.miembro;
    _nombreCtrl = TextEditingController(text: m?.nombreCompleto ?? '');
    _fechaNacCtrl = TextEditingController(text: m?.fechaNacimiento ?? '');
    _fechaIngCtrl = TextEditingController(
        text: m?.fechaIngreso ?? _todayIso());
    _telefonoCtrl = TextEditingController(text: m?.telefonoPersonal ?? '');
    _acudienteCtrl = TextEditingController(text: m?.nombreAcudiente ?? '');
    _telAcudienteCtrl =
        TextEditingController(text: m?.telefonoAcudiente ?? '');
    _tipo = (m?.tipo.isNotEmpty == true) ? m!.tipo : _tipos.first;
  }

  String _todayIso() {
    final now = DateTime.now();
    return '${now.year}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')}';
  }

  @override
  void dispose() {
    _nombreCtrl.dispose();
    _fechaNacCtrl.dispose();
    _fechaIngCtrl.dispose();
    _telefonoCtrl.dispose();
    _acudienteCtrl.dispose();
    _telAcudienteCtrl.dispose();
    super.dispose();
  }

  Future<void> _pickDate(TextEditingController ctrl) async {
    DateTime initial = DateTime.now();
    try {
      if (ctrl.text.isNotEmpty) {
        initial = DateTime.parse(ctrl.text);
      }
    } catch (_) {}
    final picked = await showDatePicker(
      context: context,
      initialDate: initial,
      firstDate: DateTime(1900),
      lastDate: DateTime(2100),
    );
    if (picked != null) {
      ctrl.text =
          '${picked.year}-${picked.month.toString().padLeft(2, '0')}-${picked.day.toString().padLeft(2, '0')}';
    }
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _loading = true);
    try {
      final data = <String, dynamic>{
        'nombre_completo': _nombreCtrl.text.trim(),
        'fecha_ingreso': _fechaIngCtrl.text.trim(),
        'tipo': _tipo,
        'grupo_id': widget.grupoId,
        if (_fechaNacCtrl.text.isNotEmpty)
          'fecha_nacimiento': _fechaNacCtrl.text.trim(),
        if (_telefonoCtrl.text.isNotEmpty)
          'telefono_personal': _telefonoCtrl.text.trim(),
        if (_acudienteCtrl.text.isNotEmpty)
          'nombre_acudiente': _acudienteCtrl.text.trim(),
        if (_telAcudienteCtrl.text.isNotEmpty)
          'telefono_acudiente': _telAcudienteCtrl.text.trim(),
      };
      final repo = ref.read(miembrosRepositoryProvider);
      if (_isEditing) {
        await repo.update(widget.miembro!.id, data);
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
        title: Text(_isEditing ? 'Editar Miembro' : 'Nuevo Miembro'),
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
              controller: _nombreCtrl,
              decoration:
                  const InputDecoration(labelText: 'Nombre completo *'),
              validator: (v) =>
                  v == null || v.trim().isEmpty ? 'Requerido' : null,
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              initialValue: _tipos.contains(_tipo) ? _tipo : _tipos.first,
              decoration: const InputDecoration(labelText: 'Tipo'),
              items: _tipos
                  // ignore: deprecated_member_use
                  .map((t) => DropdownMenuItem(value: t, child: Text(t)))
                  .toList(),
              onChanged: (v) => setState(() => _tipo = v ?? _tipo),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _fechaNacCtrl,
              decoration: const InputDecoration(
                  labelText: 'Fecha de nacimiento', hintText: 'YYYY-MM-DD'),
              readOnly: true,
              onTap: () => _pickDate(_fechaNacCtrl),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _fechaIngCtrl,
              decoration: const InputDecoration(
                  labelText: 'Fecha de ingreso *',
                  hintText: 'YYYY-MM-DD'),
              readOnly: true,
              onTap: () => _pickDate(_fechaIngCtrl),
              validator: (v) =>
                  v == null || v.trim().isEmpty ? 'Requerido' : null,
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _telefonoCtrl,
              decoration:
                  const InputDecoration(labelText: 'Teléfono personal'),
              keyboardType: TextInputType.phone,
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _acudienteCtrl,
              decoration:
                  const InputDecoration(labelText: 'Nombre acudiente'),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _telAcudienteCtrl,
              decoration:
                  const InputDecoration(labelText: 'Teléfono acudiente'),
              keyboardType: TextInputType.phone,
            ),
          ],
        ),
      ),
    );
  }
}
