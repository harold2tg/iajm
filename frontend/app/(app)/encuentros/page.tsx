"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { api } from "@/lib/api";
import { authStorage } from "@/lib/auth";
import type {
  Encuentro,
  EncuentroCreate,
  Grupo,
  Miembro,
  MiembroCreate,
  AsistenciaEncuentro,
  MetricasEncuentro,
  EstadoAsistencia,
  Usuario,
  AsistenciaMiembroItem,
  AsistenciaResponse,
} from "@/types/api";

// ── Schemas ────────────────────────────────────────────────────────────────────

const crearEncuentroSchema = z.object({
  grupo_id: z.string().min(1, "Seleccioná un grupo"),
  fecha: z.string().min(1, "Requerido"),
  tema: z.string().optional(),
  observaciones: z.string().optional(),
});

const reabrirSchema = z.object({
  motivo: z.string().min(1, "El motivo es requerido"),
});

const crearMiembroSchema = z.object({
  nombre_completo: z.string().min(1, "Requerido"),
  fecha_nacimiento: z.string().min(1, "Requerido"),
  fecha_ingreso: z.string().min(1, "Requerido"),
  telefono_personal: z.string().optional(),
  nombre_acudiente: z.string().optional(),
  telefono_acudiente: z.string().optional(),
});

type CrearEncuentroForm = z.infer<typeof crearEncuentroSchema>;
type ReopenForm = z.infer<typeof reabrirSchema>;
type CrearMiembroForm = z.infer<typeof crearMiembroSchema>;

// ── Helpers ────────────────────────────────────────────────────────────────────

function today() {
  return new Date().toISOString().split("T")[0];
}

function badgeEstado(estado: string) {
  if (estado === "abierto")
    return <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-[#27AE60]/10 text-[#27AE60]">Abierto</span>;
  return <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-500">Cerrado</span>;
}

function badgeAsistencia(estado: EstadoAsistencia) {
  const map: Record<EstadoAsistencia, string> = {
    asistio: "bg-[#27AE60]/10 text-[#27AE60]",
    no_asistio: "bg-[#C0392B]/10 text-[#C0392B]",
    justificado: "bg-[#F5C518]/20 text-[#B7860A]",
  };
  const label: Record<EstadoAsistencia, string> = {
    asistio: "Asistió",
    no_asistio: "No asistió",
    justificado: "Justificado",
  };
  return (
    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${map[estado]}`}>
      {label[estado]}
    </span>
  );
}

// ── Vista listado ──────────────────────────────────────────────────────────────

export default function EncuentrosPage() {
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<"encuentros" | "asistencia">("encuentros");
  const [vista, setVista] = useState<"listado" | "detalle">("listado");
  const [encuentroActivo, setEncuentroActivo] = useState<Encuentro | null>(null);
  const [modalCrear, setModalCrear] = useState(false);
  const [filtroGrupo, setFiltroGrupo] = useState("");
  const [filtroEstado, setFiltroEstado] = useState<"todos" | "abierto" | "cerrado">("todos");

  const { data: me } = useQuery({
    queryKey: ["me"],
    queryFn: () => api.get<Usuario>("/usuarios/me").then((r) => r.data),
  });

  const { data: grupos } = useQuery({
    queryKey: ["grupos"],
    queryFn: () => api.get<Grupo[]>("/grupos/").then((r) => r.data),
  });

  const { data: encuentros, isLoading } = useQuery({
    queryKey: ["encuentros", filtroGrupo],
    queryFn: () => {
      const params = filtroGrupo ? `?grupo_id=${filtroGrupo}` : "";
      return api.get<Encuentro[]>(`/encuentros/${params}`).then((r) => r.data);
    },
  });

  const crearForm = useForm<CrearEncuentroForm>({
    resolver: zodResolver(crearEncuentroSchema),
    defaultValues: { fecha: today() },
  });

  const crear = useMutation({
    mutationFn: (data: EncuentroCreate) =>
      api.post<Encuentro>("/encuentros/", data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["encuentros"] });
      setModalCrear(false);
      crearForm.reset({ fecha: today() });
    },
  });

  const encuentrosFiltrados = encuentros?.filter((e) => {
    if (filtroEstado === "todos") return true;
    return e.estado === filtroEstado;
  }) ?? [];

  function abrirDetalle(enc: Encuentro) {
    setEncuentroActivo(enc);
    setVista("detalle");
  }

  function volverListado() {
    setVista("listado");
    setEncuentroActivo(null);
    queryClient.invalidateQueries({ queryKey: ["encuentros"] });
  }

  if (vista === "detalle" && encuentroActivo) {
    return (
      <DetalleEncuentro
        encuentro={encuentroActivo}
        grupos={grupos ?? []}
        me={me ?? null}
        onVolver={volverListado}
        onActualizar={(enc) => setEncuentroActivo(enc)}
      />
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-[#1A4B8C]">Encuentros</h1>
        {tab === "encuentros" && (
          <button
            onClick={() => { crearForm.reset({ fecha: today() }); setModalCrear(true); }}
            className="bg-[#F5C518] text-[#1A1A1A] font-semibold px-4 py-2 rounded-lg hover:bg-[#E67E22] hover:text-white transition-colors"
          >
            + Nuevo Encuentro
          </button>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 border-b border-slate-200">
        <button
          onClick={() => setTab("encuentros")}
          className={`px-4 py-2 text-sm font-semibold rounded-t-lg transition-colors ${
            tab === "encuentros"
              ? "bg-[#1A4B8C] text-white"
              : "bg-white text-slate-500 hover:text-slate-700"
          }`}
        >
          Encuentros
        </button>
        <button
          onClick={() => setTab("asistencia")}
          className={`px-4 py-2 text-sm font-semibold rounded-t-lg transition-colors ${
            tab === "asistencia"
              ? "bg-[#1A4B8C] text-white"
              : "bg-white text-slate-500 hover:text-slate-700"
          }`}
        >
          Asistencia por grupo
        </button>
      </div>

      {/* Tab: Encuentros */}
      {tab === "encuentros" && (
        <>
          {/* Filtros */}
          <div className="flex flex-wrap gap-3 mb-4">
            <select
              value={filtroGrupo}
              onChange={(e) => setFiltroGrupo(e.target.value)}
              className="border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C] bg-white"
            >
              <option value="">Todos los grupos</option>
              {grupos?.map((g) => (
                <option key={g.id} value={g.id}>{g.nombre}</option>
              ))}
            </select>
            <select
              value={filtroEstado}
              onChange={(e) => setFiltroEstado(e.target.value as typeof filtroEstado)}
              className="border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C] bg-white"
            >
              <option value="todos">Todos los estados</option>
              <option value="abierto">Abierto</option>
              <option value="cerrado">Cerrado</option>
            </select>
          </div>

          {/* Loading */}
          {isLoading && <p className="text-slate-500 text-sm">Cargando...</p>}

          {/* Tabla */}
          {!isLoading && (
            <div className="rounded-xl border border-slate-200 overflow-hidden bg-white">
              <table className="w-full text-sm">
                <thead className="bg-slate-50 text-slate-600">
                  <tr>
                    <th className="px-4 py-3 text-left font-medium">Fecha</th>
                    <th className="px-4 py-3 text-left font-medium">Grupo</th>
                    <th className="px-4 py-3 text-left font-medium">Tema</th>
                    <th className="px-4 py-3 text-left font-medium">Estado</th>
                    <th className="px-4 py-3 text-left font-medium">Asistentes</th>
                    <th className="px-4 py-3 text-left font-medium">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {encuentrosFiltrados.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="px-4 py-8 text-center text-slate-400">
                        No hay encuentros
                      </td>
                    </tr>
                  ) : (
                    encuentrosFiltrados.map((enc) => {
                      const grupo = grupos?.find((g) => g.id === enc.grupo_id);
                      return (
                        <tr
                          key={enc.id}
                          className="hover:bg-slate-50 cursor-pointer"
                          onClick={() => abrirDetalle(enc)}
                        >
                          <td className="px-4 py-3 text-slate-700">{enc.fecha}</td>
                          <td className="px-4 py-3 text-slate-700">{grupo?.nombre ?? enc.grupo_id}</td>
                          <td className="px-4 py-3 text-slate-500">{enc.tema ?? "—"}</td>
                          <td className="px-4 py-3">{badgeEstado(enc.estado)}</td>
                          <td className="px-4 py-3 text-slate-700">{enc.total_asistentes}</td>
                          <td className="px-4 py-3">
                            <button
                              onClick={(e) => { e.stopPropagation(); abrirDetalle(enc); }}
                              className="text-xs bg-[#1A4B8C] text-white px-3 py-1.5 rounded-lg hover:bg-[#E67E22] transition-colors"
                            >
                              Ver detalle
                            </button>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {/* Tab: Asistencia por grupo */}
      {tab === "asistencia" && (
        <AsistenciaPorGrupo grupos={grupos ?? []} />
      )}

      {/* Modal Crear Encuentro */}
      {modalCrear && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-md p-6 shadow-xl">
            <h2 className="text-lg font-bold text-[#1A4B8C] mb-4">Nuevo Encuentro</h2>
            <form
              onSubmit={crearForm.handleSubmit((d) =>
                crear.mutate({
                  grupo_id: d.grupo_id,
                  fecha: d.fecha,
                  tema: d.tema || undefined,
                  observaciones: d.observaciones || undefined,
                })
              )}
              className="space-y-3"
            >
              <div>
                <label className="text-sm font-medium text-slate-700">Grupo *</label>
                <select
                  {...crearForm.register("grupo_id")}
                  className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C] bg-white"
                >
                  <option value="">Seleccioná un grupo</option>
                  {grupos?.map((g) => (
                    <option key={g.id} value={g.id}>{g.nombre}</option>
                  ))}
                </select>
                {crearForm.formState.errors.grupo_id && (
                  <p className="text-xs text-[#C0392B] mt-1">{crearForm.formState.errors.grupo_id.message}</p>
                )}
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Fecha *</label>
                <input
                  type="date"
                  {...crearForm.register("fecha")}
                  className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]"
                />
                {crearForm.formState.errors.fecha && (
                  <p className="text-xs text-[#C0392B] mt-1">{crearForm.formState.errors.fecha.message}</p>
                )}
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Tema</label>
                <input
                  {...crearForm.register("tema")}
                  placeholder="Opcional"
                  className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Observaciones</label>
                <textarea
                  {...crearForm.register("observaciones")}
                  rows={3}
                  placeholder="Opcional"
                  className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C] resize-none"
                />
              </div>
              {crear.isError && (
                <p className="text-xs text-[#C0392B]">Error al crear el encuentro</p>
              )}
              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => { setModalCrear(false); crearForm.reset({ fecha: today() }); }}
                  className="px-4 py-2 text-sm rounded-lg border border-slate-300 text-slate-600 hover:bg-slate-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={crear.isPending}
                  className="px-4 py-2 text-sm rounded-lg bg-[#F5C518] text-[#1A1A1A] font-semibold hover:bg-[#E67E22] hover:text-white transition-colors disabled:opacity-50"
                >
                  {crear.isPending ? "Guardando..." : "Guardar"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Asistencia por Grupo ───────────────────────────────────────────────────────

interface AsistenciaPorGrupoProps {
  grupos: Grupo[];
}

function AsistenciaPorGrupo({ grupos }: AsistenciaPorGrupoProps) {
  const now = new Date();
  const [grupoId, setGrupoId] = useState("");
  const [mes, setMes] = useState(String(now.getMonth() + 1));
  const [anio, setAnio] = useState(String(now.getFullYear()));
  const [consultar, setConsultar] = useState(false);

  const queryKey = ["reporte-asistencia", grupoId, mes, anio];

  const { data, isLoading, isError } = useQuery({
    queryKey,
    queryFn: () => {
      const params = new URLSearchParams({ grupo_id: grupoId });
      if (mes) params.set("mes", mes);
      if (anio) params.set("anio", anio);
      return api.get<AsistenciaResponse>(`/reportes/asistencia?${params.toString()}`).then((r) => r.data);
    },
    enabled: consultar && !!grupoId,
  });

  function handleConsultar() {
    if (!grupoId) return;
    setConsultar(true);
  }

  function handleDescargarCsv() {
    if (!grupoId) return;
    const params = new URLSearchParams({ grupo_id: grupoId, formato: "csv" });
    if (mes) params.set("mes", mes);
    if (anio) params.set("anio", anio);
    const baseUrl = `${process.env.NEXT_PUBLIC_API_URL ?? ""}/api/v1`;
    const token = authStorage.getAccess();
    // Descargamos via fetch para incluir el token de auth
    fetch(`${baseUrl}/reportes/asistencia?${params.toString()}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
      .then((res) => res.blob())
      .then((blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "reporte_asistencia.csv";
        a.click();
        URL.revokeObjectURL(url);
      });
  }

  const miembros: AsistenciaMiembroItem[] = data?.miembros
    ? [...data.miembros].sort((a, b) => b.total_asistencias - a.total_asistencias)
    : [];

  const meses = [
    { value: "1", label: "Enero" }, { value: "2", label: "Febrero" },
    { value: "3", label: "Marzo" }, { value: "4", label: "Abril" },
    { value: "5", label: "Mayo" }, { value: "6", label: "Junio" },
    { value: "7", label: "Julio" }, { value: "8", label: "Agosto" },
    { value: "9", label: "Septiembre" }, { value: "10", label: "Octubre" },
    { value: "11", label: "Noviembre" }, { value: "12", label: "Diciembre" },
  ];

  const anios = Array.from({ length: 5 }, (_, i) => String(now.getFullYear() - i));

  return (
    <div>
      {/* Filtros */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 mb-6">
        <div className="flex flex-wrap gap-3 items-end">
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-slate-600">Grupo *</label>
            <select
              value={grupoId}
              onChange={(e) => { setGrupoId(e.target.value); setConsultar(false); }}
              className="border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C] bg-white min-w-[180px]"
            >
              <option value="">Seleccioná un grupo</option>
              {grupos.map((g) => (
                <option key={g.id} value={g.id}>{g.nombre}</option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-slate-600">Mes</label>
            <select
              value={mes}
              onChange={(e) => { setMes(e.target.value); setConsultar(false); }}
              className="border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C] bg-white"
            >
              {meses.map((m) => (
                <option key={m.value} value={m.value}>{m.label}</option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-slate-600">Año</label>
            <select
              value={anio}
              onChange={(e) => { setAnio(e.target.value); setConsultar(false); }}
              className="border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C] bg-white"
            >
              {anios.map((a) => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
          </div>
          <button
            onClick={handleConsultar}
            disabled={!grupoId}
            className="px-4 py-2 text-sm rounded-lg bg-[#1A4B8C] text-white font-semibold hover:bg-[#E67E22] transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Consultar
          </button>
          {consultar && data && miembros.length > 0 && (
            <button
              onClick={handleDescargarCsv}
              className="px-4 py-2 text-sm rounded-lg border border-[#1A4B8C] text-[#1A4B8C] font-semibold hover:bg-[#1A4B8C]/5 transition-colors"
            >
              Descargar CSV
            </button>
          )}
        </div>
      </div>

      {/* Loading */}
      {isLoading && (
        <p className="text-slate-500 text-sm">Cargando asistencia...</p>
      )}

      {/* Error */}
      {isError && (
        <p className="text-sm text-[#C0392B]">Error al cargar el reporte. Intentá de nuevo.</p>
      )}

      {/* Tabla resultados */}
      {consultar && !isLoading && !isError && data && (
        <div className="rounded-xl border border-slate-200 overflow-hidden bg-white overflow-x-auto">
          <table className="w-full text-sm min-w-[700px]">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 text-left font-medium">Miembro</th>
                <th className="px-4 py-3 text-left font-medium">Asiste desde</th>
                <th className="px-4 py-3 text-left font-medium">Encuentros período</th>
                <th className="px-4 py-3 text-left font-medium">Asistencias</th>
                <th className="px-4 py-3 text-left font-medium w-40">% Asistencia</th>
                <th className="px-4 py-3 text-left font-medium">Total acumulado</th>
                <th className="px-4 py-3 text-left font-medium">Consagración</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {miembros.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-slate-400">
                    Sin registros para este grupo en el período seleccionado
                  </td>
                </tr>
              ) : (
                miembros.map((m) => {
                  const pct = m.porcentaje ?? 0;
                  const barColor =
                    pct >= 75 ? "bg-[#27AE60]" : pct >= 50 ? "bg-[#F5C518]" : "bg-[#C0392B]";
                  const textColor =
                    pct >= 75 ? "text-[#27AE60]" : pct >= 50 ? "text-[#B7860A]" : "text-[#C0392B]";

                  return (
                    <tr key={m.miembro_id} className="hover:bg-slate-50">
                      <td className="px-4 py-3 text-slate-700 font-medium">{m.nombre}</td>
                      <td className="px-4 py-3 text-slate-500 text-sm">
                        {m.fecha_ingreso
                          ? m.fecha_ingreso.split("-").reverse().join("/")
                          : "—"}
                      </td>
                      <td className="px-4 py-3 text-slate-700 text-center">{m.total_encuentros}</td>
                      <td className="px-4 py-3 text-slate-700 text-center">{m.total_asistencias}</td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="flex-1 bg-slate-100 rounded-full h-2 min-w-[60px]">
                            <div
                              className={`h-2 rounded-full ${barColor} transition-all`}
                              style={{ width: `${Math.min(pct, 100)}%` }}
                            />
                          </div>
                          <span className={`text-xs font-semibold ${textColor} w-10 text-right`}>
                            {pct.toFixed(0)}%
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-slate-700 text-center">{m.total_asistencias}</td>
                      <td className="px-4 py-3">
                        {m.apto_consagracion ? (
                          <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-[#27AE60]/10 text-[#27AE60]">
                            Apto
                          </span>
                        ) : (
                          <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-500">
                            No apto
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ── Vista detalle / pase de lista ──────────────────────────────────────────────

interface DetalleProps {
  encuentro: Encuentro;
  grupos: Grupo[];
  me: Usuario | null;
  onVolver: () => void;
  onActualizar: (enc: Encuentro) => void;
}

function DetalleEncuentro({ encuentro, grupos, me, onVolver, onActualizar }: DetalleProps) {
  const queryClient = useQueryClient();
  const [modalReabrir, setModalReabrir] = useState(false);
  const [modalAgregarMiembro, setModalAgregarMiembro] = useState(false);

  const grupo = grupos.find((g) => g.id === encuentro.grupo_id);
  const esAdmin = me?.roles?.some((r) => r.rol === "administrador") ?? false;

  // Asistencias del encuentro
  const { data: asistencias, isLoading: loadAsistencia } = useQuery({
    queryKey: ["asistencias", encuentro.id],
    queryFn: () =>
      api.get<AsistenciaEncuentro[]>(`/encuentros/${encuentro.id}/asistencia`).then((r) => r.data),
  });

  // Miembros del grupo para cruzar nombres
  const { data: miembros } = useQuery({
    queryKey: ["miembros-grupo", encuentro.grupo_id],
    queryFn: () =>
      api.get<Miembro[]>(`/miembros/?grupo_id=${encuentro.grupo_id}`).then((r) => r.data),
  });

  // Métricas (si cerrado)
  const { data: metricas } = useQuery({
    queryKey: ["metricas-encuentro", encuentro.id],
    queryFn: () =>
      api.get<MetricasEncuentro>(`/encuentros/${encuentro.id}/metricas`).then((r) => r.data),
    enabled: encuentro.estado === "cerrado",
  });

  // Cerrar encuentro
  const cerrar = useMutation({
    mutationFn: () =>
      api.post<{ encuentro: Encuentro; advertencia: string | null }>(`/encuentros/${encuentro.id}/cerrar`).then((r) => r.data),
    onSuccess: (data) => {
      onActualizar(data.encuentro);
      queryClient.invalidateQueries({ queryKey: ["metricas-encuentro", encuentro.id] });
    },
  });

  // Reabrir encuentro
  const reabrirForm = useForm<ReopenForm>({ resolver: zodResolver(reabrirSchema) });
  const reabrir = useMutation({
    mutationFn: (motivo: string) =>
      api.post<Encuentro>(`/encuentros/${encuentro.id}/reabrir`, { motivo }).then((r) => r.data),
    onSuccess: (enc) => {
      onActualizar(enc);
      setModalReabrir(false);
      reabrirForm.reset();
    },
  });

  // Registrar asistencia individual
  const registrarAsistencia = useMutation({
    mutationFn: ({ miembro_id, estado }: { miembro_id: string; estado: EstadoAsistencia }) =>
      api
        .put(`/encuentros/${encuentro.id}/asistencia/${miembro_id}`, { miembro_id, estado })
        .then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["asistencias", encuentro.id] });
    },
  });

  // Agregar miembro nuevo
  const miembroForm = useForm<CrearMiembroForm>({
    resolver: zodResolver(crearMiembroSchema),
    defaultValues: { fecha_ingreso: today() },
  });
  const crearMiembro = useMutation({
    mutationFn: (data: MiembroCreate & { encuentro_id: string }) =>
      api.post<Miembro>("/miembros/", data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["asistencias", encuentro.id] });
      queryClient.invalidateQueries({ queryKey: ["miembros-grupo", encuentro.grupo_id] });
      setModalAgregarMiembro(false);
      miembroForm.reset({ fecha_ingreso: today() });
    },
  });

  // Mapa asistencia por miembro_id para lookup rápido
  const asistenciaMap = new Map(asistencias?.map((a) => [a.miembro_id, a]) ?? []);

  // Miembros del grupo con su asistencia
  const miembrosConAsistencia = miembros?.map((m) => ({
    miembro: m,
    asistencia: asistenciaMap.get(m.id) ?? null,
  })) ?? [];

  // Si el encuentro está cerrado, mostrar solo los que asistieron
  const miembrosAMostrar =
    encuentro.estado === "cerrado"
      ? miembrosConAsistencia.filter(({ asistencia }) => asistencia?.estado === "asistio")
      : miembrosConAsistencia;

  return (
    <div>
      {/* Botón volver */}
      <button
        onClick={onVolver}
        className="flex items-center gap-2 text-sm text-[#1A4B8C] font-medium mb-4 hover:underline"
      >
        ← Volver a encuentros
      </button>

      {/* Header del encuentro */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 mb-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h2 className="text-xl font-bold text-[#1A4B8C]">
                {encuentro.fecha} — {grupo?.nombre ?? encuentro.grupo_id}
              </h2>
              {badgeEstado(encuentro.estado)}
            </div>
            {encuentro.tema && (
              <p className="text-sm text-slate-700 font-medium">{encuentro.tema}</p>
            )}
            {encuentro.observaciones && (
              <p className="text-sm text-slate-500 mt-1">{encuentro.observaciones}</p>
            )}
            <p className="text-xs text-slate-400 mt-2">
              {encuentro.total_asistentes} asistente{encuentro.total_asistentes !== 1 ? "s" : ""}
              {encuentro.porcentaje_asistencia > 0 &&
                ` · ${encuentro.porcentaje_asistencia.toFixed(1)}% cobertura`}
            </p>
          </div>
          <div className="flex gap-2">
            {encuentro.estado === "abierto" && (
              <button
                onClick={() => cerrar.mutate()}
                disabled={cerrar.isPending}
                className="px-4 py-2 text-sm rounded-lg bg-slate-700 text-white font-semibold hover:bg-slate-900 transition-colors disabled:opacity-50"
              >
                {cerrar.isPending ? "Cerrando..." : "Cerrar Encuentro"}
              </button>
            )}
            {encuentro.estado === "cerrado" && esAdmin && (
              <button
                onClick={() => setModalReabrir(true)}
                className="px-4 py-2 text-sm rounded-lg border border-[#1A4B8C] text-[#1A4B8C] font-semibold hover:bg-[#1A4B8C]/5 transition-colors"
              >
                Reabrir
              </button>
            )}
          </div>
        </div>
        {cerrar.isError && (
          <p className="text-xs text-[#C0392B] mt-2">Error al cerrar el encuentro</p>
        )}
      </div>

      {/* Métricas si cerrado */}
      {encuentro.estado === "cerrado" && metricas && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
          {[
            { label: "Total miembros", value: metricas.total_miembros },
            { label: "Asistieron", value: metricas.total_asistio, color: "text-[#27AE60]" },
            { label: "No asistieron", value: metricas.total_no_asistio, color: "text-[#C0392B]" },
            { label: "Cobertura", value: `${metricas.porcentaje_asistencia?.toFixed(1) ?? 0}%` },
          ].map((m) => (
            <div key={m.label} className="bg-white rounded-xl border border-slate-200 p-4 text-center">
              <p className={`text-2xl font-bold ${m.color ?? "text-[#1A4B8C]"}`}>{m.value}</p>
              <p className="text-xs text-slate-500 mt-1">{m.label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Pase de lista */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
          <h3 className="font-semibold text-[#1A1A1A]">Pase de lista</h3>
          {encuentro.estado === "abierto" && (
            <button
              onClick={() => { miembroForm.reset({ fecha_ingreso: today() }); setModalAgregarMiembro(true); }}
              className="text-sm bg-[#1A4B8C] text-white px-3 py-1.5 rounded-lg hover:bg-[#E67E22] transition-colors"
            >
              + Agregar Miembro
            </button>
          )}
        </div>

        {loadAsistencia && (
          <p className="px-5 py-6 text-slate-500 text-sm">Cargando asistencia...</p>
        )}

        {!loadAsistencia && miembrosAMostrar.length === 0 && (
          <p className="px-5 py-6 text-slate-400 text-sm text-center">
            {encuentro.estado === "cerrado" ? "Nadie asistió a este encuentro" : "No hay miembros en este grupo"}
          </p>
        )}

        {!loadAsistencia && miembrosAMostrar.length > 0 && (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 text-left font-medium">Miembro</th>
                <th className="px-4 py-3 text-left font-medium">Estado</th>
                {encuentro.estado === "abierto" && (
                  <th className="px-4 py-3 text-left font-medium">Acciones</th>
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {miembrosAMostrar.map(({ miembro, asistencia }) => {
                const estadoActual = asistencia?.estado ?? null;
                const isPending =
                  registrarAsistencia.isPending &&
                  (registrarAsistencia.variables as { miembro_id: string })?.miembro_id === miembro.id;

                return (
                  <tr key={miembro.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 text-slate-700 font-medium">
                      {miembro.nombre_completo}
                    </td>
                    <td className="px-4 py-3">
                      {estadoActual ? badgeAsistencia(estadoActual) : (
                        <span className="text-xs text-slate-400">Sin registrar</span>
                      )}
                    </td>
                    {encuentro.estado === "abierto" && (
                      <td className="px-4 py-3">
                        <div className="flex gap-1.5">
                          {(
                            [
                              { estado: "asistio" as EstadoAsistencia, label: "Asistió", active: "bg-[#27AE60] text-white", inactive: "border border-[#27AE60] text-[#27AE60] hover:bg-[#27AE60]/10" },
                              { estado: "no_asistio" as EstadoAsistencia, label: "No asistió", active: "bg-[#C0392B] text-white", inactive: "border border-[#C0392B] text-[#C0392B] hover:bg-[#C0392B]/10" },
                              { estado: "justificado" as EstadoAsistencia, label: "Justificado", active: "bg-[#F5C518] text-[#1A1A1A]", inactive: "border border-[#F5C518] text-[#B7860A] hover:bg-[#F5C518]/10" },
                            ] as const
                          ).map((btn) => (
                            <button
                              key={btn.estado}
                              disabled={isPending}
                              onClick={() =>
                                registrarAsistencia.mutate({
                                  miembro_id: miembro.id,
                                  estado: btn.estado,
                                })
                              }
                              className={`text-xs px-2.5 py-1 rounded-lg font-medium transition-colors disabled:opacity-50 ${estadoActual === btn.estado ? btn.active : btn.inactive}`}
                            >
                              {btn.label}
                            </button>
                          ))}
                        </div>
                      </td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Modal Reabrir */}
      {modalReabrir && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-sm p-6 shadow-xl">
            <h2 className="text-lg font-bold text-[#1A4B8C] mb-4">Reabrir Encuentro</h2>
            <form
              onSubmit={reabrirForm.handleSubmit((d) => reabrir.mutate(d.motivo))}
              className="space-y-3"
            >
              <div>
                <label className="text-sm font-medium text-slate-700">Motivo *</label>
                <textarea
                  {...reabrirForm.register("motivo")}
                  rows={3}
                  placeholder="Explicá por qué se reabre este encuentro"
                  className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C] resize-none"
                />
                {reabrirForm.formState.errors.motivo && (
                  <p className="text-xs text-[#C0392B] mt-1">
                    {reabrirForm.formState.errors.motivo.message}
                  </p>
                )}
              </div>
              {reabrir.isError && (
                <p className="text-xs text-[#C0392B]">Error al reabrir el encuentro</p>
              )}
              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => { setModalReabrir(false); reabrirForm.reset(); }}
                  className="px-4 py-2 text-sm rounded-lg border border-slate-300 text-slate-600 hover:bg-slate-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={reabrir.isPending}
                  className="px-4 py-2 text-sm rounded-lg bg-[#1A4B8C] text-white font-semibold hover:bg-[#E67E22] transition-colors disabled:opacity-50"
                >
                  {reabrir.isPending ? "Reabriendo..." : "Confirmar"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Agregar Miembro */}
      {modalAgregarMiembro && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-md p-6 shadow-xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-lg font-bold text-[#1A4B8C] mb-4">Agregar Nuevo Miembro</h2>
            <form
              onSubmit={miembroForm.handleSubmit((d) =>
                crearMiembro.mutate({
                  nombre_completo: d.nombre_completo,
                  fecha_nacimiento: d.fecha_nacimiento,
                  fecha_ingreso: d.fecha_ingreso,
                  telefono_personal: d.telefono_personal || undefined,
                  nombre_acudiente: d.nombre_acudiente || undefined,
                  telefono_acudiente: d.telefono_acudiente || undefined,
                  encuentro_id: encuentro.id,
                })
              )}
              className="space-y-3"
            >
              <div>
                <label className="text-sm font-medium text-slate-700">Nombre completo *</label>
                <input
                  {...miembroForm.register("nombre_completo")}
                  className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]"
                />
                {miembroForm.formState.errors.nombre_completo && (
                  <p className="text-xs text-[#C0392B] mt-1">
                    {miembroForm.formState.errors.nombre_completo.message}
                  </p>
                )}
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-sm font-medium text-slate-700">Fecha nacimiento *</label>
                  <input
                    type="date"
                    {...miembroForm.register("fecha_nacimiento")}
                    className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]"
                  />
                  {miembroForm.formState.errors.fecha_nacimiento && (
                    <p className="text-xs text-[#C0392B] mt-1">
                      {miembroForm.formState.errors.fecha_nacimiento.message}
                    </p>
                  )}
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-700">Fecha ingreso *</label>
                  <input
                    type="date"
                    {...miembroForm.register("fecha_ingreso")}
                    className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]"
                  />
                  {miembroForm.formState.errors.fecha_ingreso && (
                    <p className="text-xs text-[#C0392B] mt-1">
                      {miembroForm.formState.errors.fecha_ingreso.message}
                    </p>
                  )}
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Teléfono personal</label>
                <input
                  {...miembroForm.register("telefono_personal")}
                  className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Nombre acudiente</label>
                <input
                  {...miembroForm.register("nombre_acudiente")}
                  className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Teléfono acudiente</label>
                <input
                  {...miembroForm.register("telefono_acudiente")}
                  className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]"
                />
              </div>
              {crearMiembro.isError && (
                <p className="text-xs text-[#C0392B]">Error al agregar el miembro</p>
              )}
              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => { setModalAgregarMiembro(false); miembroForm.reset({ fecha_ingreso: today() }); }}
                  className="px-4 py-2 text-sm rounded-lg border border-slate-300 text-slate-600 hover:bg-slate-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={crearMiembro.isPending}
                  className="px-4 py-2 text-sm rounded-lg bg-[#F5C518] text-[#1A1A1A] font-semibold hover:bg-[#E67E22] hover:text-white transition-colors disabled:opacity-50"
                >
                  {crearMiembro.isPending ? "Guardando..." : "Guardar"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
