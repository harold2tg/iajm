"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type {
  Usuario,
  Grupo,
  BalanceResponse,
  DonacionesResponse,
  AsistenciaResponse,
  EncuentrosResponse,
  TiendaResponse,
  CuotasResponse,
  InventarioResponse,
  UsuariosResponse,
  ActividadReporteResponse,
} from "@/types/api";

// ── Helpers ───────────────────────────────────────────────────────────────────

const MESES = [
  "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
];

const hoy = new Date();
const MES_ACTUAL = hoy.getMonth() + 1;
const ANIO_ACTUAL = hoy.getFullYear();

function fmt(n: number) {
  return new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 }).format(n);
}

function pct(n: number) {
  return `${n.toFixed(1)}%`;
}

const descargarCSV = async (endpoint: string, params: Record<string, unknown>, filename: string) => {
  const response = await api.get(endpoint, {
    params: { ...params, formato: "csv" },
    responseType: "blob",
  });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
};

// ── Sub-componentes reutilizables ─────────────────────────────────────────────

function Spinner() {
  return (
    <div className="flex items-center justify-center py-16">
      <div className="w-8 h-8 border-4 border-[#1A4B8C]/20 border-t-[#1A4B8C] rounded-full animate-spin" />
    </div>
  );
}

function ErrorMsg({ msg }: { msg: string }) {
  return (
    <div className="rounded-lg bg-[#C0392B]/10 border border-[#C0392B]/20 text-[#C0392B] px-4 py-3 text-sm">
      {msg}
    </div>
  );
}

function SinDatos() {
  return (
    <p className="text-center text-slate-400 py-10 text-sm">Sin datos para el período seleccionado</p>
  );
}

function BtnCSV({ onClick }: { onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="text-sm px-3 py-1.5 rounded-lg border border-[#1A4B8C] text-[#1A4B8C] hover:bg-[#1A4B8C] hover:text-white transition-colors"
    >
      ↓ Descargar CSV
    </button>
  );
}

function FiltroMesAnio({
  mes, anio, onMes, onAnio,
}: {
  mes: number; anio: number;
  onMes: (v: number) => void;
  onAnio: (v: number) => void;
}) {
  return (
    <div className="flex gap-3 flex-wrap">
      <select
        value={mes}
        onChange={(e) => onMes(Number(e.target.value))}
        className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-[#1A4B8C]/30"
      >
        {MESES.map((m, i) => (
          <option key={m} value={i + 1}>{m}</option>
        ))}
      </select>
      <input
        type="number"
        value={anio}
        min={2020}
        max={2100}
        onChange={(e) => onAnio(Number(e.target.value))}
        className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm bg-white text-slate-700 w-24 focus:outline-none focus:ring-2 focus:ring-[#1A4B8C]/30"
      />
    </div>
  );
}

function Card({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5">
      <p className="text-sm text-slate-500 mb-1">{label}</p>
      <p className={`text-2xl font-bold ${color ?? "text-[#1A4B8C]"}`}>{value}</p>
    </div>
  );
}

// ── Tab: Balance ──────────────────────────────────────────────────────────────

function TabBalance() {
  const [mes, setMes] = useState(MES_ACTUAL);
  const [anio, setAnio] = useState(ANIO_ACTUAL);

  const { data, isLoading, isError, refetch } = useQuery<BalanceResponse>({
    queryKey: ["reporte-balance", mes, anio],
    queryFn: () => api.get<BalanceResponse>("/reportes/balance", { params: { mes, anio } }).then((r) => r.data),
  });

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <FiltroMesAnio mes={mes} anio={anio} onMes={setMes} onAnio={setAnio} />
        <div className="flex gap-2">
          <button
            onClick={() => refetch()}
            className="text-sm px-3 py-1.5 rounded-lg bg-[#1A4B8C] text-white hover:bg-[#1A4B8C]/90 transition-colors"
          >
            Consultar
          </button>
          <BtnCSV onClick={() => descargarCSV("/reportes/balance", { mes, anio }, `balance-${mes}-${anio}.csv`)} />
        </div>
      </div>

      {isLoading && <Spinner />}
      {isError && <ErrorMsg msg="Error al cargar el balance. Verificá los filtros e intentá de nuevo." />}
      {data && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card label="Total Ingresos" value={fmt(data.total_ingresos)} color="text-[#27AE60]" />
            <Card label="Total Gastos" value={fmt(data.total_gastos)} color="text-[#C0392B]" />
            <Card
              label="Saldo"
              value={fmt(data.saldo)}
              color={data.saldo >= 0 ? "text-[#27AE60]" : "text-[#C0392B]"}
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
              <div className="px-4 py-3 border-b border-slate-100 bg-[#27AE60]/5">
                <h3 className="font-semibold text-[#27AE60] text-sm">Detalle de Ingresos</h3>
              </div>
              {data.detalle_ingresos.length === 0 ? <SinDatos /> : (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-slate-50">
                      <th className="text-left px-4 py-2 text-slate-500 font-medium">Descripción</th>
                      <th className="text-left px-4 py-2 text-slate-500 font-medium">Tipo</th>
                      <th className="text-left px-4 py-2 text-slate-500 font-medium">Fecha</th>
                      <th className="text-right px-4 py-2 text-slate-500 font-medium">Valor</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.detalle_ingresos.map((item, i) => (
                      <tr key={i} className="border-t border-slate-50">
                        <td className="px-4 py-2 text-slate-700">{item.descripcion}</td>
                        <td className="px-4 py-2 text-slate-500 capitalize">{item.tipo.replace(/_/g, " ")}</td>
                        <td className="px-4 py-2 text-slate-500">{item.fecha}</td>
                        <td className="px-4 py-2 text-right text-[#27AE60] font-medium">{fmt(item.valor)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>

            <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
              <div className="px-4 py-3 border-b border-slate-100 bg-[#C0392B]/5">
                <h3 className="font-semibold text-[#C0392B] text-sm">Detalle de Gastos</h3>
              </div>
              {data.detalle_gastos.length === 0 ? <SinDatos /> : (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-slate-50">
                      <th className="text-left px-4 py-2 text-slate-500 font-medium">Descripción</th>
                      <th className="text-left px-4 py-2 text-slate-500 font-medium">Categoría</th>
                      <th className="text-left px-4 py-2 text-slate-500 font-medium">Fecha</th>
                      <th className="text-right px-4 py-2 text-slate-500 font-medium">Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.detalle_gastos.map((item, i) => (
                      <tr key={i} className="border-t border-slate-50">
                        <td className="px-4 py-2 text-slate-700">{item.descripcion}</td>
                        <td className="px-4 py-2 text-slate-500">{item.categoria}</td>
                        <td className="px-4 py-2 text-slate-500">{item.fecha}</td>
                        <td className="px-4 py-2 text-right text-[#C0392B] font-medium">{fmt(item.valor_total)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

// ── Tab: Donaciones ───────────────────────────────────────────────────────────

function TabDonaciones() {
  const [mes, setMes] = useState(MES_ACTUAL);
  const [anio, setAnio] = useState(ANIO_ACTUAL);
  const [tipo, setTipo] = useState("todos");

  const { data, isLoading, isError, refetch } = useQuery<DonacionesResponse>({
    queryKey: ["reporte-donaciones", mes, anio, tipo],
    queryFn: () =>
      api.get<DonacionesResponse>("/reportes/donaciones", { params: { mes, anio, tipo } }).then((r) => r.data),
  });

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex gap-3 flex-wrap">
          <FiltroMesAnio mes={mes} anio={anio} onMes={setMes} onAnio={setAnio} />
          <select
            value={tipo}
            onChange={(e) => setTipo(e.target.value)}
            className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-[#1A4B8C]/30"
          >
            <option value="todos">Todos</option>
            <option value="efectivo">Efectivo</option>
            <option value="especie">Especie</option>
          </select>
        </div>
        <div className="flex gap-2">
          <button onClick={() => refetch()} className="text-sm px-3 py-1.5 rounded-lg bg-[#1A4B8C] text-white hover:bg-[#1A4B8C]/90 transition-colors">
            Consultar
          </button>
          <BtnCSV onClick={() => descargarCSV("/reportes/donaciones", { mes, anio, tipo }, `donaciones-${mes}-${anio}.csv`)} />
        </div>
      </div>

      {isLoading && <Spinner />}
      {isError && <ErrorMsg msg="Error al cargar las donaciones." />}
      {data && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Card label="Total Efectivo" value={fmt(data.total_efectivo)} color="text-[#27AE60]" />
            <Card label="Total Especie" value={fmt(data.total_especie)} color="text-[#E67E22]" />
          </div>

          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            {data.donaciones.length === 0 ? <SinDatos /> : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-[#1A4B8C]">
                    <th className="text-left px-4 py-3 text-white font-medium">Fecha</th>
                    <th className="text-left px-4 py-3 text-white font-medium">Donante</th>
                    <th className="text-left px-4 py-3 text-white font-medium">Tipo</th>
                    <th className="text-left px-4 py-3 text-white font-medium">Descripción</th>
                    <th className="text-right px-4 py-3 text-white font-medium">Valor</th>
                  </tr>
                </thead>
                <tbody>
                  {data.donaciones.map((d, i) => (
                    <tr key={d.id} className={`border-t border-slate-50 ${i % 2 === 0 ? "bg-white" : "bg-slate-50"}`}>
                      <td className="px-4 py-2 text-slate-500">{d.fecha}</td>
                      <td className="px-4 py-2 text-slate-700">{d.donante ?? "—"}</td>
                      <td className="px-4 py-2">
                        <span className={`text-xs font-medium px-2 py-0.5 rounded-full capitalize ${d.tipo === "efectivo" ? "bg-[#27AE60]/10 text-[#27AE60]" : "bg-[#E67E22]/10 text-[#E67E22]"}`}>
                          {d.tipo}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-slate-500">{d.descripcion ?? "—"}</td>
                      <td className="px-4 py-2 text-right font-medium text-slate-700">
                        {d.valor != null ? fmt(d.valor) : d.valor_estimado != null ? fmt(d.valor_estimado) : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </div>
  );
}

// ── Tab: Asistencia ───────────────────────────────────────────────────────────

function TabAsistencia() {
  const [mes, setMes] = useState(MES_ACTUAL);
  const [anio, setAnio] = useState(ANIO_ACTUAL);
  const [grupoId, setGrupoId] = useState("");

  const { data: grupos } = useQuery<Grupo[]>({
    queryKey: ["grupos"],
    queryFn: () => api.get<Grupo[]>("/grupos/").then((r) => r.data),
  });

  const { data, isLoading, isError, refetch } = useQuery<AsistenciaResponse>({
    queryKey: ["reporte-asistencia", grupoId, mes, anio],
    queryFn: () =>
      api.get<AsistenciaResponse>("/reportes/asistencia", { params: { grupo_id: grupoId || undefined, mes, anio } }).then((r) => r.data),
    enabled: false,
  });

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex gap-3 flex-wrap">
          <select
            value={grupoId}
            onChange={(e) => setGrupoId(e.target.value)}
            className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-[#1A4B8C]/30"
          >
            <option value="">Todos los grupos</option>
            {grupos?.map((g) => (
              <option key={g.id} value={g.id}>{g.nombre}</option>
            ))}
          </select>
          <FiltroMesAnio mes={mes} anio={anio} onMes={setMes} onAnio={setAnio} />
        </div>
        <div className="flex gap-2">
          <button onClick={() => refetch()} className="text-sm px-3 py-1.5 rounded-lg bg-[#1A4B8C] text-white hover:bg-[#1A4B8C]/90 transition-colors">
            Consultar
          </button>
          <BtnCSV onClick={() => descargarCSV("/reportes/asistencia", { grupo_id: grupoId || undefined, mes, anio }, `asistencia-${mes}-${anio}.csv`)} />
        </div>
      </div>

      {isLoading && <Spinner />}
      {isError && <ErrorMsg msg="Error al cargar el reporte de asistencia." />}
      {data && (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          {data.miembros.length === 0 ? <SinDatos /> : (
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-[#1A4B8C]">
                  <th className="text-left px-4 py-3 text-white font-medium">Miembro</th>
                  <th className="text-center px-4 py-3 text-white font-medium">Encuentros</th>
                  <th className="text-center px-4 py-3 text-white font-medium">Asistencias</th>
                  <th className="text-left px-4 py-3 text-white font-medium w-40">% Asistencia</th>
                  <th className="text-center px-4 py-3 text-white font-medium">Apto Consagración</th>
                </tr>
              </thead>
              <tbody>
                {data.miembros.map((m, i) => (
                  <tr key={m.miembro_id} className={`border-t border-slate-50 ${i % 2 === 0 ? "bg-white" : "bg-slate-50"}`}>
                    <td className="px-4 py-2 font-medium text-slate-700">{m.nombre}</td>
                    <td className="px-4 py-2 text-center text-slate-500">{m.total_encuentros}</td>
                    <td className="px-4 py-2 text-center text-slate-500">{m.total_asistencias}</td>
                    <td className="px-4 py-2">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-slate-100 rounded-full h-2">
                          <div
                            className="h-2 rounded-full bg-[#1A4B8C]"
                            style={{ width: `${Math.min(m.porcentaje, 100)}%` }}
                          />
                        </div>
                        <span className="text-xs text-slate-600 w-10 text-right">{pct(m.porcentaje)}</span>
                      </div>
                    </td>
                    <td className="px-4 py-2 text-center">
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${m.apto_consagracion ? "bg-[#27AE60]/10 text-[#27AE60]" : "bg-slate-100 text-slate-400"}`}>
                        {m.apto_consagracion ? "Apto" : "No apto"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
      {!data && !isLoading && (
        <p className="text-center text-slate-400 py-10 text-sm">Seleccioná los filtros y presioná Consultar</p>
      )}
    </div>
  );
}

// ── Tab: Encuentros ───────────────────────────────────────────────────────────

function TabEncuentros() {
  const [mes, setMes] = useState(MES_ACTUAL);
  const [anio, setAnio] = useState(ANIO_ACTUAL);
  const [grupoId, setGrupoId] = useState("");

  const { data: grupos } = useQuery<Grupo[]>({
    queryKey: ["grupos"],
    queryFn: () => api.get<Grupo[]>("/grupos/").then((r) => r.data),
  });

  const { data, isLoading, isError, refetch } = useQuery<EncuentrosResponse>({
    queryKey: ["reporte-encuentros", grupoId, mes, anio],
    queryFn: () =>
      api.get<EncuentrosResponse>("/reportes/encuentros", { params: { grupo_id: grupoId || undefined, mes, anio } }).then((r) => r.data),
    enabled: false,
  });

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex gap-3 flex-wrap">
          <select
            value={grupoId}
            onChange={(e) => setGrupoId(e.target.value)}
            className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-[#1A4B8C]/30"
          >
            <option value="">Todos los grupos</option>
            {grupos?.map((g) => (
              <option key={g.id} value={g.id}>{g.nombre}</option>
            ))}
          </select>
          <FiltroMesAnio mes={mes} anio={anio} onMes={setMes} onAnio={setAnio} />
        </div>
        <div className="flex gap-2">
          <button onClick={() => refetch()} className="text-sm px-3 py-1.5 rounded-lg bg-[#1A4B8C] text-white hover:bg-[#1A4B8C]/90 transition-colors">
            Consultar
          </button>
          <BtnCSV onClick={() => descargarCSV("/reportes/encuentros", { grupo_id: grupoId || undefined, mes, anio }, `encuentros-${mes}-${anio}.csv`)} />
        </div>
      </div>

      {isLoading && <Spinner />}
      {isError && <ErrorMsg msg="Error al cargar el reporte de encuentros." />}
      {data && (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          {data.encuentros.length === 0 ? <SinDatos /> : (
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-[#1A4B8C]">
                  <th className="text-left px-4 py-3 text-white font-medium">Fecha</th>
                  <th className="text-left px-4 py-3 text-white font-medium">Grupo</th>
                  <th className="text-left px-4 py-3 text-white font-medium">Tema</th>
                  <th className="text-center px-4 py-3 text-white font-medium">Miembros</th>
                  <th className="text-center px-4 py-3 text-white font-medium">Asistieron</th>
                  <th className="text-center px-4 py-3 text-white font-medium">% Cobertura</th>
                </tr>
              </thead>
              <tbody>
                {data.encuentros.map((e, i) => (
                  <tr key={e.encuentro_id} className={`border-t border-slate-50 ${i % 2 === 0 ? "bg-white" : "bg-slate-50"}`}>
                    <td className="px-4 py-2 text-slate-500">{e.fecha}</td>
                    <td className="px-4 py-2 text-slate-700">{e.grupo}</td>
                    <td className="px-4 py-2 text-slate-500">{e.tema ?? "—"}</td>
                    <td className="px-4 py-2 text-center text-slate-500">{e.total_miembros}</td>
                    <td className="px-4 py-2 text-center text-slate-500">{e.total_asistieron}</td>
                    <td className="px-4 py-2 text-center">
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${e.porcentaje_cobertura >= 70 ? "bg-[#27AE60]/10 text-[#27AE60]" : "bg-[#C0392B]/10 text-[#C0392B]"}`}>
                        {pct(e.porcentaje_cobertura)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
      {!data && !isLoading && (
        <p className="text-center text-slate-400 py-10 text-sm">Seleccioná los filtros y presioná Consultar</p>
      )}
    </div>
  );
}

// ── Tab: Tienda ───────────────────────────────────────────────────────────────

function TabTienda() {
  const [mes, setMes] = useState(MES_ACTUAL);
  const [anio, setAnio] = useState(ANIO_ACTUAL);

  const { data, isLoading, isError, refetch } = useQuery<TiendaResponse>({
    queryKey: ["reporte-tienda", mes, anio],
    queryFn: () =>
      api.get<TiendaResponse>("/reportes/tienda", { params: { mes, anio } }).then((r) => r.data),
  });

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <FiltroMesAnio mes={mes} anio={anio} onMes={setMes} onAnio={setAnio} />
        <div className="flex gap-2">
          <button onClick={() => refetch()} className="text-sm px-3 py-1.5 rounded-lg bg-[#1A4B8C] text-white hover:bg-[#1A4B8C]/90 transition-colors">
            Consultar
          </button>
          <BtnCSV onClick={() => descargarCSV("/reportes/tienda", { mes, anio }, `tienda-${mes}-${anio}.csv`)} />
        </div>
      </div>

      {isLoading && <Spinner />}
      {isError && <ErrorMsg msg="Error al cargar el reporte de tienda." />}
      {data && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Card label="Total del Mes" value={fmt(data.total_mes)} color="text-[#1A4B8C]" />
            <Card label="Acumulado Histórico" value={fmt(data.acumulado_historico)} color="text-[#E67E22]" />
          </div>

          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <div className="px-4 py-3 border-b border-slate-100">
              <h3 className="font-semibold text-slate-700 text-sm">Ventas por Día</h3>
            </div>
            {data.ventas_por_dia.length === 0 ? <SinDatos /> : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50">
                    <th className="text-left px-4 py-2 text-slate-500 font-medium">Fecha</th>
                    <th className="text-right px-4 py-2 text-slate-500 font-medium">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {data.ventas_por_dia.map((v, i) => (
                    <tr key={i} className="border-t border-slate-50">
                      <td className="px-4 py-2 text-slate-700">{v.fecha}</td>
                      <td className="px-4 py-2 text-right font-medium text-[#1A4B8C]">{fmt(v.total)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </div>
  );
}

// ── Tab: Cuotas ───────────────────────────────────────────────────────────────

function TabCuotas() {
  const [mes, setMes] = useState(MES_ACTUAL);
  const [anio, setAnio] = useState(ANIO_ACTUAL);

  const { data, isLoading, isError, refetch } = useQuery<CuotasResponse>({
    queryKey: ["reporte-cuotas", mes, anio],
    queryFn: () =>
      api.get<CuotasResponse>("/reportes/cuotas", { params: { mes, anio } }).then((r) => r.data),
  });

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <FiltroMesAnio mes={mes} anio={anio} onMes={setMes} onAnio={setAnio} />
        <div className="flex gap-2">
          <button onClick={() => refetch()} className="text-sm px-3 py-1.5 rounded-lg bg-[#1A4B8C] text-white hover:bg-[#1A4B8C]/90 transition-colors">
            Consultar
          </button>
          <BtnCSV onClick={() => descargarCSV("/reportes/cuotas", { mes, anio }, `cuotas-${mes}-${anio}.csv`)} />
        </div>
      </div>

      {isLoading && <Spinner />}
      {isError && <ErrorMsg msg="Error al cargar el reporte de cuotas." />}
      {data && (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          {data.cuotas.length === 0 ? <SinDatos /> : (
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-[#1A4B8C]">
                  <th className="text-left px-4 py-3 text-white font-medium">Asesor</th>
                  <th className="text-center px-4 py-3 text-white font-medium">Estado</th>
                  <th className="text-right px-4 py-3 text-white font-medium">Monto</th>
                  <th className="text-center px-4 py-3 text-white font-medium">Fecha Pago</th>
                </tr>
              </thead>
              <tbody>
                {data.cuotas.map((c, i) => (
                  <tr key={c.asesor_id} className={`border-t border-slate-50 ${i % 2 === 0 ? "bg-white" : "bg-slate-50"}`}>
                    <td className="px-4 py-2 font-medium text-slate-700">{c.nombre}</td>
                    <td className="px-4 py-2 text-center">
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full capitalize ${c.estado === "pagado" ? "bg-[#27AE60]/10 text-[#27AE60]" : "bg-[#C0392B]/10 text-[#C0392B]"}`}>
                        {c.estado}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-right text-slate-700">{fmt(c.monto)}</td>
                    <td className="px-4 py-2 text-center text-slate-500">{c.fecha_pago ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}

// ── Tab: Inventario ───────────────────────────────────────────────────────────

function TabInventario() {
  const { data, isLoading, isError } = useQuery<InventarioResponse>({
    queryKey: ["reporte-inventario"],
    queryFn: () => api.get<InventarioResponse>("/reportes/inventario").then((r) => r.data),
  });

  return (
    <div className="space-y-5">
      <div className="flex justify-end">
        <BtnCSV onClick={() => descargarCSV("/reportes/inventario", {}, "inventario.csv")} />
      </div>

      {isLoading && <Spinner />}
      {isError && <ErrorMsg msg="Error al cargar el inventario." />}
      {data && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card label="Total Ítems" value={String(data.total_items)} />
            <div className="bg-white rounded-xl border border-slate-200 p-5">
              <p className="text-sm text-slate-500 mb-2">Por Tipo</p>
              <div className="space-y-1">
                {data.por_tipo.map((t) => (
                  <div key={t.clave} className="flex justify-between text-sm">
                    <span className="text-slate-600 capitalize">{t.clave}</span>
                    <span className="font-medium text-[#1A4B8C]">{t.cantidad}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-white rounded-xl border border-slate-200 p-5">
              <p className="text-sm text-slate-500 mb-2">Por Origen</p>
              <div className="space-y-1">
                {data.por_origen.map((o) => (
                  <div key={o.clave} className="flex justify-between text-sm">
                    <span className="text-slate-600 capitalize">{o.clave}</span>
                    <span className="font-medium text-[#1A4B8C]">{o.cantidad}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            {data.items.length === 0 ? <SinDatos /> : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-[#1A4B8C]">
                    <th className="text-left px-4 py-3 text-white font-medium">Nombre</th>
                    <th className="text-center px-4 py-3 text-white font-medium">Cantidad</th>
                    <th className="text-left px-4 py-3 text-white font-medium">Tipo</th>
                    <th className="text-left px-4 py-3 text-white font-medium">Origen</th>
                    <th className="text-left px-4 py-3 text-white font-medium">Estado</th>
                    <th className="text-left px-4 py-3 text-white font-medium">Ubicación</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((item, i) => (
                    <tr key={item.id} className={`border-t border-slate-50 ${i % 2 === 0 ? "bg-white" : "bg-slate-50"}`}>
                      <td className="px-4 py-2 font-medium text-slate-700">{item.nombre}</td>
                      <td className="px-4 py-2 text-center text-slate-500">{item.cantidad}</td>
                      <td className="px-4 py-2 text-slate-500 capitalize">{item.tipo ?? "—"}</td>
                      <td className="px-4 py-2 text-slate-500 capitalize">{item.origen ?? "—"}</td>
                      <td className="px-4 py-2 text-slate-500 capitalize">{item.estado ?? "—"}</td>
                      <td className="px-4 py-2 text-slate-500">{item.ubicacion ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </div>
  );
}

// ── Tab: Usuarios ─────────────────────────────────────────────────────────────

function TabUsuarios() {
  const { data: me } = useQuery<Usuario>({
    queryKey: ["me"],
    queryFn: () => api.get<Usuario>("/usuarios/me").then((r) => r.data),
  });

  const { data, isLoading, isError } = useQuery<UsuariosResponse>({
    queryKey: ["reporte-usuarios"],
    queryFn: () => api.get<UsuariosResponse>("/reportes/usuarios").then((r) => r.data),
    enabled: me?.rol === "administrador",
  });

  if (me && me.rol !== "administrador") {
    return (
      <div className="rounded-lg bg-[#F5C518]/10 border border-[#F5C518]/30 text-slate-700 px-4 py-6 text-center text-sm">
        Este reporte sólo está disponible para administradores.
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {isLoading && <Spinner />}
      {isError && <ErrorMsg msg="Error al cargar el reporte de usuarios." />}
      {data && (
        <>
          <div className="flex items-center justify-between">
            <Card label="Usuarios Activos" value={String(data.total_activos)} />
          </div>
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            {data.usuarios.length === 0 ? <SinDatos /> : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-[#1A4B8C]">
                    <th className="text-left px-4 py-3 text-white font-medium">Nombre</th>
                    <th className="text-left px-4 py-3 text-white font-medium">Email</th>
                    <th className="text-left px-4 py-3 text-white font-medium">Roles</th>
                    <th className="text-left px-4 py-3 text-white font-medium">Último Acceso</th>
                  </tr>
                </thead>
                <tbody>
                  {data.usuarios.map((u, i) => (
                    <tr key={u.id} className={`border-t border-slate-50 ${i % 2 === 0 ? "bg-white" : "bg-slate-50"}`}>
                      <td className="px-4 py-2 font-medium text-slate-700">{u.nombre}</td>
                      <td className="px-4 py-2 text-slate-500">{u.email}</td>
                      <td className="px-4 py-2">
                        <div className="flex flex-wrap gap-1">
                          {u.roles.map((r) => (
                            <span key={r} className="text-xs px-2 py-0.5 rounded-full bg-[#1A4B8C]/10 text-[#1A4B8C] capitalize">
                              {r.replace(/_/g, " ")}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="px-4 py-2 text-slate-500">{u.ultimo_acceso ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </div>
  );
}

// ── Tab: Actividades ──────────────────────────────────────────────────────────

function TabActividades() {
  const [actividadId, setActividadId] = useState("");
  const [queryId, setQueryId] = useState("");

  const { data, isLoading, isError } = useQuery<ActividadReporteResponse>({
    queryKey: ["reporte-actividad", queryId],
    queryFn: () =>
      api.get<ActividadReporteResponse>(`/reportes/actividades/${queryId}`).then((r) => r.data),
    enabled: !!queryId,
  });

  return (
    <div className="space-y-5">
      <div className="flex gap-3">
        <input
          type="text"
          value={actividadId}
          onChange={(e) => setActividadId(e.target.value)}
          placeholder="ID de la actividad"
          className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm bg-white text-slate-700 flex-1 max-w-xs focus:outline-none focus:ring-2 focus:ring-[#1A4B8C]/30"
        />
        <button
          onClick={() => setQueryId(actividadId.trim())}
          disabled={!actividadId.trim()}
          className="text-sm px-4 py-1.5 rounded-lg bg-[#1A4B8C] text-white hover:bg-[#1A4B8C]/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Consultar
        </button>
      </div>

      {isLoading && <Spinner />}
      {isError && <ErrorMsg msg="No se encontró la actividad o hubo un error al cargar." />}
      {data && (
        <>
          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <h3 className="font-bold text-[#1A4B8C] text-base mb-2">{data.nombre}</h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm text-slate-600">
              <div><span className="text-slate-400">Tipo: </span>{data.tipo}</div>
              <div><span className="text-slate-400">Fecha: </span>{data.fecha}</div>
              <div><span className="text-slate-400">Responsable: </span>{data.responsable}</div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card label="Total Ingresos" value={fmt(data.total_ingresos)} color="text-[#27AE60]" />
            <Card label="Total Costos" value={fmt(data.total_costos)} color="text-[#C0392B]" />
            <Card
              label="Utilidad"
              value={fmt(data.utilidad)}
              color={data.utilidad >= 0 ? "text-[#27AE60]" : "text-[#C0392B]"}
            />
          </div>

          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <div className="px-4 py-3 border-b border-slate-100">
              <h3 className="font-semibold text-slate-700 text-sm">Productos</h3>
            </div>
            {data.productos.length === 0 ? <SinDatos /> : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50">
                    <th className="text-left px-4 py-2 text-slate-500 font-medium">Producto</th>
                    <th className="text-center px-4 py-2 text-slate-500 font-medium">Cantidad</th>
                    <th className="text-right px-4 py-2 text-slate-500 font-medium">Costo Unit.</th>
                    <th className="text-right px-4 py-2 text-slate-500 font-medium">Precio Venta</th>
                    <th className="text-center px-4 py-2 text-slate-500 font-medium">Donado</th>
                  </tr>
                </thead>
                <tbody>
                  {data.productos.map((p) => (
                    <tr key={p.id} className="border-t border-slate-50">
                      <td className="px-4 py-2 text-slate-700">{p.nombre}</td>
                      <td className="px-4 py-2 text-center text-slate-500">{p.cantidad}</td>
                      <td className="px-4 py-2 text-right text-slate-500">{p.costo_unitario != null ? fmt(p.costo_unitario) : "—"}</td>
                      <td className="px-4 py-2 text-right font-medium text-[#1A4B8C]">{fmt(p.precio_venta)}</td>
                      <td className="px-4 py-2 text-center">
                        <span className={`text-xs px-2 py-0.5 rounded-full ${p.es_donado ? "bg-[#27AE60]/10 text-[#27AE60]" : "bg-slate-100 text-slate-400"}`}>
                          {p.es_donado ? "Sí" : "No"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
      {!queryId && (
        <p className="text-center text-slate-400 py-10 text-sm">Ingresá el ID de una actividad y presioná Consultar</p>
      )}
    </div>
  );
}

// ── Tabs config ───────────────────────────────────────────────────────────────

const TABS = [
  { key: "balance", label: "Balance", component: TabBalance },
  { key: "donaciones", label: "Donaciones", component: TabDonaciones },
  { key: "asistencia", label: "Asistencia", component: TabAsistencia },
  { key: "encuentros", label: "Encuentros", component: TabEncuentros },
  { key: "tienda", label: "Tienda", component: TabTienda },
  { key: "cuotas", label: "Cuotas", component: TabCuotas },
  { key: "inventario", label: "Inventario", component: TabInventario },
  { key: "usuarios", label: "Usuarios", component: TabUsuarios },
  { key: "actividades", label: "Actividades", component: TabActividades },
] as const;

type TabKey = (typeof TABS)[number]["key"];

// ── Página principal ──────────────────────────────────────────────────────────

export default function ReportesPage() {
  const [activeTab, setActiveTab] = useState<TabKey>("balance");

  const ActiveComponent = TABS.find((t) => t.key === activeTab)!.component;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[#1A4B8C]">Reportes</h1>
        <p className="text-sm text-slate-500 mt-1">Consultas e informes del sistema</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200 overflow-x-auto">
        <div className="flex gap-1 min-w-max">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px whitespace-nowrap ${
                activeTab === tab.key
                  ? "border-[#1A4B8C] text-[#1A4B8C]"
                  : "border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Contenido del tab activo */}
      <div>
        <ActiveComponent />
      </div>
    </div>
  );
}
