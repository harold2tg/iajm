# SRS — Especificación de Requerimientos de Software
## Sistema de Gestión Integral IAM
### Infancia, Adolescencia y Misión Parroquial

> **Versión:** 1.1.0 · **Estado:** Draft — revisión requerida

---

| Campo | Detalle |
|---|---|
| Versión | 1.1.0 |
| Cambios respecto a v1.0 | Módulo de usuarios y roles (nuevo) · Módulo de encuentros de sábado (nuevo) · Tienda misionera redefinida por día · Asistencia vinculada al encuentro |
| Backend | FastAPI + PostgreSQL |
| Frontend Web | Next.js (App Router) |
| App Móvil | Flutter |
| Infraestructura | Docker · Digital Ocean |

---

## 01. Alcance y contexto del sistema

El sistema IAM es una plataforma de gestión integral para grupos parroquiales que administra miembros, asesores, formación, tesorería, inventario y actividades. Opera como aplicación web (Next.js) y aplicación móvil (Flutter), respaldada por una API centralizada (FastAPI) desplegada en Digital Ocean mediante contenedores Docker.

La dinámica operativa del movimiento gira en torno al **encuentro semanal del sábado**: cada grupo se reúne ese día y el asesor de grupo registra la asistencia dentro del encuentro. Simultáneamente, la tienda misionera puede operar ese mismo sábado o en cualquier otra fecha según lo indique el asesor responsable.

> ⚠️ **Restricción crítica de dominio:** Los fondos recaudados en actividades parroquiales externas *no pertenecen a IAM*. El sistema debe registrarlos y segregarlos como fondos de terceros, sin afectar el balance general de la organización.

---

## 02. Arquitectura técnica

| Capa | Detalle |
|---|---|
| **API** | FastAPI (Python 3.11+) · Arquitectura por dominios (routers, services, schemas, repositories) · Pydantic v2 para validación · SQLAlchemy 2.0 ORM · Alembic para migraciones |
| **Base de datos** | PostgreSQL 16 · Índices en campos de búsqueda frecuente (fecha, grupo, estado) · Triggers para automatización de reglas de negocio críticas |
| **Web** | Next.js 14 (App Router) · TypeScript · Tailwind CSS · React Query para estado servidor · Zod para validación de formularios |
| **Móvil** | Flutter 3.x · Dart · Riverpod para gestión de estado · Dio para cliente HTTP · Soporte Android e iOS |
| **Infraestructura** | Docker Compose (dev) · Docker + Nginx reverse proxy (prod) · Digital Ocean Droplet · GitHub Actions CI/CD · Variables de entorno por stage |
| **Seguridad** | JWT con refresh tokens · RBAC basado en roles definidos en sección 03 · HTTPS obligatorio · Rate limiting en endpoints sensibles |

---

## 03. Módulo de usuarios y control de acceso (RBAC)

Este módulo es transversal a todo el sistema. Define qué puede ver y operar cada tipo de usuario. El modelo de seguridad es **Role-Based Access Control (RBAC)** con roles fijos y la posibilidad de que un usuario acumule más de un rol simultáneamente.

### 3.1 Roles del sistema

#### Rol: Administrador

Es el único rol con acceso total al sistema sin restricciones. Solo debe existir un número muy reducido de usuarios con este rol.

| Alcance | Detalle |
|---|---|
| **Acceso** | Total — todos los módulos, todos los grupos |
| **Operaciones** | Crear, leer, actualizar, eliminar en cualquier entidad |
| **Exclusivo** | Gestión de usuarios y asignación de roles · Configuración global del sistema · Reportes consolidados de todos los grupos |

#### Rol: Asesor de grupo

Es el rol operativo principal. Cada asesor de grupo tiene visibilidad y operación **únicamente sobre el grupo o grupos a los que está asignado**. No puede ver información de miembros de otros grupos.

| Alcance | Detalle |
|---|---|
| **Acceso** | Restringido a su(s) grupo(s) asignado(s) |
| **Puede** | Ver el listado de miembros de su grupo · Crear y gestionar encuentros del sábado de su grupo · Registrar asistencia en sus encuentros · Ingresar nuevos miembros durante un encuentro · Consultar historial de asistencia de su grupo |
| **No puede** | Ver miembros de otros grupos · Acceder a tesorería · Acceder a inventario · Gestionar usuarios |

> ℹ️ Un asesor puede pertenecer a más de un grupo. En ese caso, su acceso se amplía a todos sus grupos asignados, pero sigue sin poder ver otros grupos.

#### Rol: Asesor de tesorería

Gestiona toda la parte financiera del sistema. **Puede coexistir con el rol de asesor de grupo** en el mismo usuario: en ese caso el usuario opera tanto en finanzas como en su grupo.

| Alcance | Detalle |
|---|---|
| **Acceso** | Módulo de tesorería completo · Módulo de gastos · Actividades pro-fondos · Donaciones · Cuotas de asesores · Actividades parroquiales externas · Reportes financieros |
| **Puede** | Registrar ingresos, gastos y donaciones · Gestionar actividades pro-fondos · Consultar y registrar cuotas de asesores · Exportar reportes financieros |
| **No puede** | Gestionar usuarios · Acceder a información de miembros de grupos que no sean los suyos (salvo que también tenga rol de asesor de grupo en ese grupo) |

#### Rol: Asesor de tienda misionera

Gestiona las ventas de la tienda misionera. **Puede coexistir con el rol de asesor de grupo** en el mismo usuario.

| Alcance | Detalle |
|---|---|
| **Acceso** | Módulo de tienda misionera · Consulta de inventario relacionado |
| **Puede** | Registrar ventas del día (en cualquier fecha, no restringida a sábados) · Consultar histórico de ventas · Ver reportes de tienda |
| **No puede** | Acceder a tesorería general · Gestionar usuarios · Ver miembros de grupos (salvo que también tenga rol de asesor de grupo) |

#### Rol: Observador

Usuario de solo lectura. Puede navegar y consultar todo el sistema pero no puede crear, modificar ni eliminar ningún registro.

| Alcance | Detalle |
|---|---|
| **Acceso** | Todo el sistema — todos los módulos y todos los grupos |
| **Puede** | Consultar y exportar cualquier reporte · Ver listados de miembros, grupos, asesores, tesorería, inventario y actividades |
| **No puede** | Crear, editar o eliminar ningún registro · Gestionar usuarios · Realizar ninguna operación que modifique el estado del sistema |

> ℹ️ Este rol es útil para líderes parroquiales, revisores externos o autoridades que necesitan visibilidad sin intervenir en la operación.

### 3.2 Acumulación de roles

Un mismo usuario puede tener más de un rol. Las combinaciones válidas y su resultado son:

| Combinación | Resultado |
|---|---|
| Asesor de grupo + Asesor de tesorería | Opera su grupo Y gestiona finanzas |
| Asesor de grupo + Asesor de tienda misionera | Opera su grupo Y registra ventas de tienda |
| Asesor de grupo + Asesor de tesorería + Asesor de tienda misionera | Opera su grupo, finanzas y tienda simultáneamente |
| Observador + cualquier otro rol | Inválido — el rol observador es exclusivo, no se combina |
| Administrador + cualquier otro rol | Innecesario — el administrador ya tiene acceso total |

### 3.3 Modelo de datos — entidad Usuario

| Campo | Tipo | Observación |
|---|---|---|
| `id` | uuid | PK generado automáticamente |
| `nombre_completo` | varchar(200) | **Requerido** |
| `email` | varchar(200) | **Requerido** · Único · Usado para login |
| `password_hash` | varchar | **Requerido** · bcrypt |
| `activo` | boolean | Default: true |
| `creado_en` | timestamp | Automático |
| `ultimo_acceso` | timestamp | Actualizado en cada login |

### 3.4 Modelo de datos — entidad UsuarioRol (N:M)

| Campo | Tipo | Observación |
|---|---|---|
| `usuario_id` | FK → Usuario | **Requerido** |
| `rol` | enum(administrador, asesor_grupo, asesor_tesoreria, asesor_tienda, observador) | **Requerido** |
| `grupo_id` | FK → Grupo · nullable | Solo aplica cuando rol = asesor_grupo |
| `asignado_en` | timestamp | Automático |
| `asignado_por` | FK → Usuario | Usuario administrador que hizo la asignación |

### 3.5 Reglas de negocio — usuarios

**RN-USR-001 · Solo administradores gestionan usuarios**
La creación, edición, activación/desactivación y asignación de roles de usuarios es una operación exclusiva del rol administrador. Ningún otro rol puede acceder a estos endpoints.

**RN-USR-002 · Observador es rol exclusivo**
Un usuario con rol observador no puede tener ningún otro rol asignado simultáneamente. El sistema debe rechazar esta combinación con error descriptivo.

**RN-USR-003 · Asesor de grupo requiere grupo asignado**
Al asignar el rol `asesor_grupo`, el campo `grupo_id` es obligatorio. No puede existir un asesor de grupo sin grupo asignado.

**RN-USR-004 · Restricción de visibilidad por grupo**
Todos los endpoints que devuelven información de miembros deben filtrar por los grupos asignados al usuario autenticado cuando su rol es `asesor_grupo`. Esta restricción debe aplicarse en la capa de servicio de la API, no en el frontend.

**RN-USR-005 · Auditoría de acceso**
Cada login exitoso debe registrar timestamp y dirección IP en tabla `log_acceso`. Los intentos fallidos (más de 5 consecutivos) deben bloquear temporalmente la cuenta por 15 minutos.

---

## 04. Módulo de miembros

### Modelo de datos — entidad Miembro

| Campo | Tipo | Observación |
|---|---|---|
| `nombre_completo` | varchar(200) | **Requerido** |
| `fecha_nacimiento` | date | **Requerido** |
| `edad` | integer | Calculado automáticamente |
| `tipo` | enum(infancia, adolescencia, juventud) | Calculado automáticamente |
| `grupo_id` | FK → Grupo | Asignado automáticamente |
| `fecha_ingreso` | date | **Requerido** |
| `telefono_personal` | varchar(20) | Condicional según tipo |
| `nombre_acudiente` | varchar(200) | Condicional según tipo |
| `telefono_acudiente` | varchar(20) | Condicional según tipo |
| `activo` | boolean | Default: true |
| `ingresado_en_encuentro_id` | FK → Encuentro · nullable | Si el miembro fue ingresado durante un encuentro |

### Reglas de negocio — validaciones condicionales

**RN-MEM-001 · Infancia (4–12 años)**
Los campos `nombre_acudiente` y `telefono_acudiente` son obligatorios. El campo `telefono_personal` no aplica y debe ignorarse si se envía.

**RN-MEM-002 · Adolescencia (13–15 años)**
Igual que infancia: acudiente obligatorio. El campo `telefono_personal` es opcional pero permitido.

**RN-MEM-003 · Juventud (16–24 años)**
No requiere acudiente. `telefono_personal` es obligatorio. El sistema no debe solicitar ni almacenar datos de acudiente.

**RN-MEM-004 · Rango de edad**
Solo se permiten registros con edad entre 4 y 24 años inclusive. El sistema debe calcularlo desde `fecha_nacimiento` al momento del registro; no se permite entrada manual de edad.

**RN-MEM-005 · Ingreso durante encuentro**
Cuando un asesor de grupo registra un nuevo miembro desde la pantalla de un encuentro activo, el sistema debe vincular automáticamente el nuevo miembro al encuentro mediante `ingresado_en_encuentro_id` y registrar su primer registro de asistencia con estado `asistio` para ese encuentro.

---

## 05. Gestión automática de grupos

### Definición de grupos por edad

| Grupo | Rango de edad | Tipo |
|---|---|---|
| Trigo Verde | 4 – 6 años | Infancia |
| Trigo Maduro Iniciado | 7 – 9 años | Infancia |
| Trigo Maduro Avanzado | 10 – 12 años | Infancia |
| Adolescencia | 13 – 15 años | Adolescencia |
| Juventud | 16 – 24 años | Juventud |

### Proceso automático diario — RN-GRP-001

> 🔴 **Crítico:** Este proceso debe ejecutarse diariamente vía cron job (recomendado: 00:05 UTC). Recalcula la edad de cada miembro activo, detecta si su grupo actual ya no corresponde a su edad y actualiza el campo `grupo_id` automáticamente. Debe registrar un log de cada cambio con fecha, miembro y grupos anterior/nuevo.

- La asignación manual de grupo que contradiga el rango de edad debe ser rechazada con error 422 desde la API.
- Al cambiar de grupo, debe evaluarse si el miembro pasa a Juventud y en ese caso verificar/solicitar teléfono personal.
- Los logs de cambio de grupo deben quedar trazables en tabla `historial_grupo` con timestamp.

---

## 06. Módulo de asesores

### Modelo de datos — entidad Asesor

| Campo | Tipo | Observación |
|---|---|---|
| `nombre_completo` | varchar(200) | **Requerido** |
| `telefono` | varchar(20) | **Requerido** |
| `tipo` | enum(base, auxiliar) | **Requerido** |
| `usuario_id` | FK → Usuario · nullable | Cuenta de acceso al sistema si aplica |
| `activo` | boolean | Default: true |

### Reglas de negocio

**RN-ASE-001 · Cobertura obligatoria**
Cada grupo debe tener asignado exactamente 1 asesor base. La API debe impedir eliminar o desactivar un asesor base si es el único en su grupo.

**RN-ASE-002 · Multi-grupo**
Un asesor puede pertenecer a múltiples grupos. La relación es N:M mediante tabla `asesor_grupo`.

**RN-ASE-003 · Cuotas mensuales**
El sistema debe registrar el pago de cuota mensual por asesor: fecha, monto, mes correspondiente y estado (pagado / pendiente). Debe generarse automáticamente el registro de cuota al inicio de cada mes para asesores activos.

---

## 07. Módulo de encuentros del sábado

Este es el módulo operativo central del movimiento. Toda la dinámica formativa ocurre en el **encuentro semanal**, que se realiza los sábados. El sistema debe modelarlo como una entidad propia que agrupa la asistencia y los eventos ocurridos en esa sesión.

### 7.1 Contexto operativo

Los encuentros se realizan **todos los sábados**. Cada grupo tiene su propio encuentro ese día. El asesor de grupo responsable debe crear el encuentro en el sistema antes o durante la sesión, registrar quiénes asistieron y, si llega alguien nuevo, ingresarlo directamente desde esa pantalla.

> ℹ️ Aunque el patrón es semanal los sábados, el sistema **no debe restringir técnicamente la fecha a sábados**, para permitir flexibilidad ante días festivos, cambios de calendario o reuniones extraordinarias. La fecha es libre; el asesor es quien decide cuándo crear el encuentro.

### 7.2 Modelo de datos — entidad Encuentro

| Campo | Tipo | Observación |
|---|---|---|
| `id` | uuid | PK |
| `grupo_id` | FK → Grupo | **Requerido** |
| `fecha` | date | **Requerido** · Generalmente un sábado |
| `creado_por` | FK → Usuario | Asesor que creó el encuentro |
| `tema` | varchar(300) | Opcional — tema o actividad del encuentro |
| `observaciones` | text | Opcional — notas generales del encuentro |
| `estado` | enum(abierto, cerrado) | Default: abierto. Cerrado impide modificaciones |
| `creado_en` | timestamp | Automático |
| `cerrado_en` | timestamp | Nullable — se llena al cerrar |

### 7.3 Modelo de datos — entidad AsistenciaEncuentro

| Campo | Tipo | Observación |
|---|---|---|
| `id` | uuid | PK |
| `encuentro_id` | FK → Encuentro | **Requerido** |
| `miembro_id` | FK → Miembro | **Requerido** |
| `estado` | enum(asistio, no_asistio, justificado) | **Requerido** |
| `registrado_por` | FK → Usuario | Asesor que marcó la asistencia |
| `registrado_en` | timestamp | Automático |

### 7.4 Flujo operativo del encuentro

El asesor de grupo sigue este flujo desde la aplicación (web o móvil):

1. **Crear el encuentro:** selecciona su grupo, confirma o ajusta la fecha y opcionalmente escribe el tema del día. El sistema crea el encuentro en estado `abierto`.
2. **Pasar lista:** el sistema muestra todos los miembros activos del grupo. El asesor marca cada uno como `asistio`, `no_asistio` o `justificado`.
3. **Ingresar nuevo miembro (si aplica):** si llega un participante nuevo, el asesor lo registra directamente desde la pantalla del encuentro. El sistema lo vincula al grupo, crea su perfil completo y lo registra automáticamente con estado `asistio` en ese encuentro.
4. **Cerrar el encuentro:** al finalizar, el asesor cierra el encuentro. Una vez cerrado, no se pueden modificar los registros de asistencia salvo que el administrador lo reabra explícitamente.

### 7.5 Reglas de negocio — encuentros

**RN-ENC-001 · Un encuentro por grupo por fecha**
No puede existir más de un encuentro para el mismo grupo en la misma fecha. El sistema debe rechazar duplicados con error descriptivo.

**RN-ENC-002 · Solo el asesor del grupo puede crear encuentros**
Un asesor solo puede crear encuentros para los grupos a los que está asignado. El administrador puede crear encuentros para cualquier grupo.

**RN-ENC-003 · Encuentro abierto requerido para registrar asistencia**
Solo se puede registrar o modificar asistencia en encuentros con estado `abierto`. Los encuentros `cerrados` son de solo lectura.

**RN-ENC-004 · Registro completo antes de cerrar**
El sistema debe advertir (no bloquear) si se intenta cerrar un encuentro sin haber registrado el estado de todos los miembros activos del grupo.

**RN-ENC-005 · Nuevo miembro desde encuentro**
Al ingresar un nuevo miembro desde un encuentro activo, se aplica el flujo descrito en RN-MEM-005: el miembro queda vinculado al encuentro y su primer registro de asistencia es `asistio`.

**RN-ENC-006 · Reapertura de encuentros**
Solo el administrador puede reabrir un encuentro cerrado. Toda reapertura debe quedar registrada en log de auditoría con usuario, fecha y motivo.

### 7.6 Métricas derivadas de los encuentros

Las siguientes métricas se calculan en tiempo de consulta a partir de los registros de asistencia:

- **Porcentaje de asistencia por miembro:** total de `asistio` / total de encuentros del grupo en el período × 100.
- **Porcentaje de asistencia por encuentro:** total de `asistio` en ese encuentro / total de miembros activos del grupo × 100.
- **Racha de asistencia:** número de encuentros consecutivos a los que asistió un miembro.
- **Aptitud para consagración:** se evalúa con parámetros configurables (tiempo mínimo desde ingreso en meses + porcentaje mínimo de asistencia). El sistema identifica automáticamente los miembros que cumplen ambos criterios.

---

## 08. Seguimiento formativo

El seguimiento formativo se construye **sobre los registros de asistencia vinculados a encuentros** (sección 07). No existe un módulo de asistencia separado; toda asistencia ocurre en el contexto de un encuentro.

### Consultas disponibles

- Historial de asistencia de un miembro: todos sus registros de `AsistenciaEncuentro` ordenados cronológicamente.
- Listado de encuentros de un grupo: con fecha, tema, total asistentes y porcentaje de asistencia.
- Miembros con baja asistencia: filtro por umbral configurable (ej. menos del 50% en los últimos 2 meses).
- Miembros aptos para consagración: según parámetros configurables por el administrador.

---

## 09. Módulo de tesorería

### Fuentes de ingreso permitidas

- Cuotas de asesores (vinculadas a tabla `cuotas_asesor`)
- Actividades pro-fondos (utilidad neta de la actividad)
- Tienda misionera (ventas registradas por el asesor de tienda)
- Donaciones en efectivo
- Otros ingresos (con descripción obligatoria)

### Actividades pro-fondos — modelo de datos

| Campo | Tipo | Observación |
|---|---|---|
| `nombre`, `tipo`, `fecha`, `responsable` | varchar / date | Campos cabecera de la actividad |
| `ProductoActividad.nombre` | varchar | Nombre del producto |
| `ProductoActividad.cantidad` | integer | Unidades |
| `ProductoActividad.costo_unitario` | numeric(12,2) | Nullable si el producto es donado |
| `ProductoActividad.precio_venta` | numeric(12,2) | Precio al público |
| `ProductoActividad.es_donado` | boolean | Indica si el producto fue donado |

**RN-TES-001 · Cálculos automáticos**
- Total ingresos = Σ(cantidad × precio_venta)
- Total costos = Σ(cantidad × costo_unitario) solo para productos no donados
- Utilidad = ingresos − costos

Todos los valores se calculan en tiempo de consulta; no se almacenan.

### Donaciones — reglas de integridad

> 🔴 **RN-TES-002:** Una donación debe ser de tipo **efectivo** O **especie**, nunca ambos. Debe estar asociada a una actividad O ser general, nunca ambas. El sistema debe rechazar cualquier combinación ambigua con error de validación descriptivo.

**RN-TES-003 · Donaciones en especie**
Requieren: descripción, cantidad y `valor_estimado` (obligatorio). Se registran automáticamente en el módulo de inventario. No se suman al flujo de efectivo; afectan el inventario y pueden reducir costos de actividades.

**RN-TES-004 · Donaciones en efectivo**
Requieren: valor, fecha, donante (opcional). Se suman directamente al balance de ingresos del período correspondiente.

---

## 10. Módulo de gastos

### Modelo de datos — entidad Gasto

| Campo | Tipo | Observación |
|---|---|---|
| `fecha` | date | **Requerido** |
| `mes` | integer | Derivado de fecha (automático) |
| `descripcion` | text | **Requerido** |
| `cantidad` | integer | **Requerido** |
| `valor_unitario` | numeric(12,2) | **Requerido** |
| `valor_total` | numeric(12,2) | Calculado (cantidad × valor_unitario) |
| `categoria` | FK → CategoriaGasto | **Requerido** |

### Reglas

- El campo `mes` debe derivarse de la `fecha`, no ingresarse manualmente, para garantizar consistencia.
- El sistema debe exponer agrupación mensual y reporte anual con totalización por categoría.

---

## 11. Tienda misionera e inventario

### 11.1 Tienda misionera

La tienda misionera opera principalmente los sábados junto al encuentro, pero el sistema **no restringe la fecha a sábados**. El asesor de tienda misionera puede registrar ventas en cualquier fecha que él indique. Esto permite cubrir ventas en eventos especiales, ferias o cualquier otra ocasión fuera del sábado habitual.

#### Modelo de datos — entidad VentaDia

El modelo anterior de venta mensual se reemplaza por un modelo de **venta por día**, más granular y alineado con la operación real.

| Campo | Tipo | Observación |
|---|---|---|
| `id` | uuid | PK |
| `fecha` | date | **Requerido** · Fecha real de la venta (libre) |
| `registrado_por` | FK → Usuario | Asesor de tienda que registra |
| `observaciones` | varchar(500) | Opcional — contexto de la venta (ej. "sábado encuentro", "feria parroquial") |
| `total_calculado` | numeric(12,2) | Calculado a partir del detalle de productos |
| `creado_en` | timestamp | Automático |

#### Modelo de datos — entidad DetalleVentaDia

| Campo | Tipo | Observación |
|---|---|---|
| `venta_dia_id` | FK → VentaDia | **Requerido** |
| `producto` | varchar(200) | **Requerido** |
| `cantidad` | integer | **Requerido** |
| `precio_unitario` | numeric(12,2) | **Requerido** |
| `subtotal` | numeric(12,2) | Calculado (cantidad × precio_unitario) |

#### Reglas de negocio — tienda misionera

**RN-TIE-001 · Fecha libre**
El asesor de tienda puede registrar ventas en cualquier fecha. El sistema no valida que sea sábado. Si en un mismo día hay múltiples sesiones de venta, se pueden crear múltiples registros de `VentaDia` para la misma fecha.

**RN-TIE-002 · Solo el asesor de tienda puede registrar ventas**
El rol `asesor_tienda` es el único que puede crear y editar registros de venta. El administrador puede hacerlo también. El asesor de tesorería puede consultarlos pero no crearlos.

**RN-TIE-003 · Integración con tesorería**
Cada registro de `VentaDia` cerrado debe generar automáticamente un ingreso en tesorería del tipo "tienda misionera" con el `total_calculado` correspondiente y la `fecha` de la venta.

### 11.2 Inventario

#### Modelo de datos — entidad ItemInventario

| Campo | Tipo | Observación |
|---|---|---|
| `nombre` | varchar(200) | **Requerido** |
| `cantidad` | integer | **Requerido** |
| `estado` | enum(bueno, regular, dañado) | |
| `ubicacion` | varchar | |
| `responsable` | varchar | |
| `tipo` | enum(formativo, liturgico, insumo) | |
| `origen` | enum(compra, donacion) | |

> ℹ️ Las donaciones en especie deben crear automáticamente un registro en inventario con `origen = 'donacion'`. El sistema debe mantener el vínculo entre la donación original y el ítem de inventario para trazabilidad.

---

## 12. Actividades parroquiales externas

> 🔴 **Restricción de dominio — RN-ACT-001:** Los fondos de actividades parroquiales externas **NO pertenecen a IAM**. Deben registrarse en una tabla separada (`fondos_parroquiales`) y estar explícitamente excluidos de todos los reportes de balance, ingresos y saldo de IAM. El sistema debe impedirlo a nivel de base de datos, no solo de UI.

### Modelo de datos — entidad ActividadParroquial

| Campo | Tipo | Observación |
|---|---|---|
| `nombre` | varchar(200) | **Requerido** |
| `fecha` | date | **Requerido** |
| `descripcion` | text | |
| `responsable` | varchar | |
| `dinero_recolectado` | numeric(12,2) | |
| `fecha_entrega` | date | Nullable hasta que se realice la entrega |
| `entregado` | boolean | Default: false |

---

## 13. Reportes y analítica

- **Balance general:** ingresos totales − gastos totales = saldo. Filtrable por mes y año. Excluye fondos parroquiales.
- **Reporte por actividad:** detalle de ingresos, costos, utilidad y participantes por actividad pro-fondos.
- **Reporte de donaciones:** efectivo vs. especie, asociadas vs. generales, por período.
- **Reporte de inventario:** estado actual por tipo, ítems donados vs. comprados.
- **Reporte de asistencia:** por grupo, por miembro, por período. Basado en encuentros. Incluye % de asistencia e indicador de aptitud para consagración.
- **Reporte de encuentros:** listado de encuentros por grupo con fecha, asistentes y porcentaje de cobertura.
- **Reporte de tienda misionera:** ventas por día, por mes y acumulado histórico.
- **Reporte de cuotas:** estado de pago de asesores por mes, histórico de cumplimiento.
- **Reporte de usuarios:** listado de usuarios activos, roles asignados y último acceso (solo administrador).

> ℹ️ Todos los reportes deben ser exportables a **PDF** y **CSV** desde la aplicación web. La app móvil puede mostrar versiones resumidas con opción de compartir.

---

## 14. Entregables esperados del desarrollo

| Entregable | Descripción |
|---|---|
| **Esquema de base de datos** | DDL completo con relaciones, índices, constraints y triggers. Scripts Alembic de migración. Incluye tablas de usuarios, roles, encuentros y asistencia. |
| **API REST documentada** | FastAPI con documentación OpenAPI automática. Endpoints cubiertos con pruebas unitarias mínimas (pytest). Middleware de autorización RBAC por rol. |
| **Frontend web** | Next.js con formularios, listados, reportes y dashboard. Vistas diferenciadas por rol. Pantalla de gestión de encuentros y pase de lista. Responsive. Autenticación JWT. |
| **App móvil Flutter** | Módulos de encuentros, pase de lista, ingreso de nuevo miembro y consulta de reportes. Autenticación y sincronización con API. Diseñada para uso en campo (sábado). |
| **Docker Compose** | Configuración para desarrollo local y producción. Archivos separados dev/prod con variables de entorno. |
| **Datos de ejemplo** | Script seed con datos iniciales coherentes: usuarios por rol, grupos, asesores, miembros de prueba, encuentros históricos, movimientos de tesorería y ventas de tienda. |
| **Cron job automatización** | Proceso de reasignación diaria de grupos y generación mensual de cuotas de asesores. Registro de logs. Celery Beat o cron nativo en Docker. |
| **README de despliegue** | Instrucciones paso a paso para despliegue en Digital Ocean. Variables de entorno requeridas documentadas. |

---

## 15. Matriz de permisos consolidada

| Módulo / Acción | Administrador | Asesor de grupo | Asesor de tesorería | Asesor de tienda | Observador |
|---|:---:|:---:|:---:|:---:|:---:|
| Gestión de usuarios y roles | ✅ | ❌ | ❌ | ❌ | ❌ |
| Ver miembros (propio grupo) | ✅ | ✅ | ❌ | ❌ | ✅ |
| Ver miembros (todos los grupos) | ✅ | ❌ | ❌ | ❌ | ✅ |
| Crear / editar miembros | ✅ | ✅ (su grupo) | ❌ | ❌ | ❌ |
| Crear encuentros | ✅ | ✅ (su grupo) | ❌ | ❌ | ❌ |
| Registrar asistencia en encuentro | ✅ | ✅ (su grupo) | ❌ | ❌ | ❌ |
| Cerrar / reabrir encuentro | ✅ | Cerrar ✅ / Reabrir ❌ | ❌ | ❌ | ❌ |
| Ver encuentros y asistencia | ✅ | ✅ (su grupo) | ❌ | ❌ | ✅ |
| Tesorería (ingresos, gastos, donaciones) | ✅ | ❌ | ✅ | ❌ | ✅ |
| Registrar ventas de tienda | ✅ | ❌ | ❌ | ✅ | ❌ |
| Consultar ventas de tienda | ✅ | ❌ | ✅ | ✅ | ✅ |
| Gestión de inventario | ✅ | ❌ | ✅ | ✅ (consulta) | ✅ |
| Actividades parroquiales externas | ✅ | ❌ | ✅ | ❌ | ✅ |
| Exportar reportes | ✅ | ✅ (su grupo) | ✅ | ✅ (tienda) | ✅ |
| Configuración del sistema | ✅ | ❌ | ❌ | ❌ | ❌ |

---

*SRS IAM v1.1 · Documento de requerimientos · Sujeto a revisión y aprobación de stakeholders*
