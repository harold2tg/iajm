export type RolEnum = "administrador" | "asesor_grupo" | "asesor_tesoreria" | "asesor_tienda" | "observador";

export interface UsuarioRol {
  id: string;
  rol: RolEnum;
  grupo_id: string | null;
  asignado_en: string;
}

export interface Usuario {
  id: string;
  email: string;
  nombre_completo: string;
  activo: boolean;
  roles: UsuarioRol[];
}

export type TipoGrupo = "infancia" | "adolescencia" | "juventud";

export interface Grupo {
  id: string;
  nombre: string;
  tipo: TipoGrupo;
  edad_minima: number;
  edad_maxima: number;
}

export interface Miembro {
  id: string;
  nombre_completo: string;
  fecha_nacimiento: string;
  fecha_ingreso: string;
  grupo_id: string;
  activo: boolean;
  tipo: string;
  nombre_acudiente?: string;
  telefono?: string;
  nombre_grupo?: string | null;
}

export type TipoAsesor = "base" | "coordinador" | "de_apoyo" | "de_contingencia";

export interface GrupoSimple {
  id: string;
  nombre: string;
}

export interface Asesor {
  id: string;
  nombre_completo: string;
  telefono: string;
  tipo: TipoAsesor;
  fecha_nacimiento?: string;
  activo: boolean;
  grupos: GrupoSimple[];
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export type EstadoEncuentro = "abierto" | "cerrado";
export type EstadoAsistencia = "asistio" | "no_asistio" | "justificado";

export interface Encuentro {
  id: string;
  grupo_id: string;
  fecha: string;
  tema: string | null;
  observaciones: string | null;
  estado: EstadoEncuentro;
  creado_por: string | null;
  creado_en: string;
  cerrado_en: string | null;
  total_asistentes: number;
  porcentaje_asistencia: number;
}

export interface EncuentroCreate {
  grupo_id: string;
  fecha: string;
  tema?: string;
  observaciones?: string;
}

export interface AsistenciaEncuentro {
  id: string;
  encuentro_id: string;
  miembro_id: string;
  estado: EstadoAsistencia;
  registrado_por: string | null;
  registrado_en: string;
}

export interface MetricasEncuentro {
  total_miembros: number;
  total_asistio: number;
  total_no_asistio: number;
  total_justificado: number;
  porcentaje_asistencia: number;
}

export interface ResumenTesoreria {
  total_ingresos: number;
  total_gastos: number;
  balance: number;
}

export interface ActividadTesoreria {
  id: string;
  nombre: string;
  fecha: string;
  monto_recaudado: number;
}

export interface Donacion {
  id: string;
  donante: string;
  monto: number;
  fecha: string;
}

export interface CategoriaGasto {
  id: string;
  nombre: string;
}

export interface Gasto {
  id: string;
  descripcion: string;
  total: number;
  fecha: string;
  categoria_id: string;
}

export interface Venta {
  id: string;
  fecha: string;
  total: number;
  observaciones?: string;
}

export interface ItemInventario {
  id: string;
  nombre: string;
  tipo: string;
  estado: string;
  origen: string;
}

export interface ActividadParroquial {
  id: string;
  nombre: string;
  fecha: string;
  entregado: boolean;
}

export interface MiembroCreate {
  nombre_completo: string;
  fecha_nacimiento: string;
  fecha_ingreso: string;
  telefono_personal?: string;
  nombre_acudiente?: string;
  telefono_acudiente?: string;
  encuentro_id?: string;
}

export interface MiembroUpdate {
  nombre_completo?: string;
  telefono_personal?: string;
  nombre_acudiente?: string;
  telefono_acudiente?: string;
  activo?: boolean;
}

export interface AsesorCreate {
  nombre_completo: string;
  telefono: string;
  tipo: TipoAsesor;
}

export interface AsesorUpdate {
  nombre_completo?: string;
  telefono?: string;
  tipo?: TipoAsesor;
  activo?: boolean;
}

export interface GrupoUpdate {
  nombre?: string;
  edad_minima?: number;
  edad_maxima?: number;
  activo?: boolean;
}

// ── Reportes ──────────────────────────────────────────────────────────────────

export interface DetalleIngresoItem {
  descripcion: string;
  valor: number;
  fecha: string;
  tipo: string;
}

export interface DetalleGastoItem {
  descripcion: string;
  valor_total: number;
  fecha: string;
  categoria: string;
}

export interface BalanceResponse {
  mes: number;
  anio: number;
  total_ingresos: number;
  total_gastos: number;
  saldo: number;
  detalle_ingresos: DetalleIngresoItem[];
  detalle_gastos: DetalleGastoItem[];
}

export interface ProductoActividadItem {
  id: string;
  nombre: string;
  cantidad: number;
  costo_unitario: number | null;
  precio_venta: number;
  es_donado: boolean;
}

export interface ActividadReporteResponse {
  actividad_id: string;
  nombre: string;
  tipo: string;
  fecha: string;
  responsable: string;
  productos: ProductoActividadItem[];
  total_ingresos: number;
  total_costos: number;
  utilidad: number;
}

export interface DonacionItem {
  id: string;
  tipo: string;
  donante: string | null;
  fecha: string;
  valor: number | null;
  descripcion: string | null;
  cantidad_especie: number | null;
  valor_estimado: number | null;
}

export interface DonacionesResponse {
  total_efectivo: number;
  total_especie: number;
  donaciones: DonacionItem[];
}

export interface GrupoConteo {
  clave: string;
  cantidad: number;
}

export interface ItemInventarioItem {
  id: string;
  nombre: string;
  cantidad: number;
  tipo: string | null;
  origen: string | null;
  estado: string | null;
  ubicacion: string | null;
}

export interface InventarioResponse {
  total_items: number;
  por_tipo: GrupoConteo[];
  por_origen: GrupoConteo[];
  items: ItemInventarioItem[];
}

export interface AsistenciaMiembroItem {
  miembro_id: string;
  nombre: string;
  fecha_ingreso: string;
  total_encuentros: number;
  total_asistencias: number;
  porcentaje: number;
  apto_consagracion: boolean;
}

export interface AsistenciaResponse {
  miembros: AsistenciaMiembroItem[];
}

export interface EncuentroReporteItem {
  encuentro_id: string;
  fecha: string;
  grupo: string;
  tema: string | null;
  total_miembros: number;
  total_asistieron: number;
  porcentaje_cobertura: number;
}

export interface EncuentrosResponse {
  encuentros: EncuentroReporteItem[];
}

export interface VentaDiaItem {
  fecha: string;
  total: number;
}

export interface TiendaResponse {
  total_mes: number;
  ventas_por_dia: VentaDiaItem[];
  acumulado_historico: number;
}

export interface CuotaAsesorItem {
  asesor_id: string;
  nombre: string;
  estado: string;
  monto: number;
  fecha_pago: string | null;
}

export interface CuotasResponse {
  mes: number;
  anio: number;
  cuotas: CuotaAsesorItem[];
}

export interface UsuarioReporteItem {
  id: string;
  nombre: string;
  email: string;
  roles: string[];
  ultimo_acceso: string | null;
}

export interface UsuariosResponse {
  total_activos: number;
  usuarios: UsuarioReporteItem[];
}
