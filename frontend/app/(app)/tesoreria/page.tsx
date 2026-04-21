"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { ResumenTesoreria, ActividadTesoreria, Donacion } from "@/types/api";

export default function TesoreriaPage() {
  const { data: resumen, isLoading: loadingResumen } = useQuery<ResumenTesoreria>({
    queryKey: ["tesoreria", "resumen"],
    queryFn: () => api.get("/tesoreria/resumen").then((r) => r.data),
  });

  const { data: actividades, isLoading: loadingActividades } = useQuery<ActividadTesoreria[]>({
    queryKey: ["tesoreria", "actividades"],
    queryFn: () => api.get("/tesoreria/actividades").then((r) => r.data),
  });

  const { data: donaciones, isLoading: loadingDonaciones } = useQuery<Donacion[]>({
    queryKey: ["tesoreria", "donaciones"],
    queryFn: () => api.get("/tesoreria/donaciones").then((r) => r.data),
  });

  if (loadingResumen || loadingActividades || loadingDonaciones)
    return <p className="p-6 text-slate-500">Cargando...</p>;

  return (
    <div className="p-6 space-y-8">
      <h1 className="text-2xl font-bold text-slate-900">Tesorería</h1>

      {/* Cards de resumen */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500 mb-1">Ingresos</p>
          <p className="text-2xl font-bold text-green-600">
            ${resumen?.total_ingresos.toLocaleString()}
          </p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500 mb-1">Gastos</p>
          <p className="text-2xl font-bold text-red-600">
            ${resumen?.total_gastos.toLocaleString()}
          </p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500 mb-1">Balance</p>
          <p className={`text-2xl font-bold ${(resumen?.balance ?? 0) >= 0 ? "text-blue-600" : "text-red-600"}`}>
            ${resumen?.balance.toLocaleString()}
          </p>
        </div>
      </div>

      {/* Actividades pro-fondos */}
      <div>
        <h2 className="text-lg font-semibold text-slate-800 mb-3">Actividades Pro-Fondos</h2>
        <div className="rounded-lg border border-slate-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 text-left font-medium">Nombre</th>
                <th className="px-4 py-3 text-left font-medium">Fecha</th>
                <th className="px-4 py-3 text-left font-medium">Monto Recaudado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {actividades?.map((a) => (
                <tr key={a.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 text-slate-700">{a.nombre}</td>
                  <td className="px-4 py-3 text-slate-700">{a.fecha}</td>
                  <td className="px-4 py-3 text-slate-700">${a.monto_recaudado.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Donaciones */}
      <div>
        <h2 className="text-lg font-semibold text-slate-800 mb-3">Donaciones</h2>
        <div className="rounded-lg border border-slate-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 text-left font-medium">Donante</th>
                <th className="px-4 py-3 text-left font-medium">Monto</th>
                <th className="px-4 py-3 text-left font-medium">Fecha</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {donaciones?.map((d) => (
                <tr key={d.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 text-slate-700">{d.donante}</td>
                  <td className="px-4 py-3 text-slate-700">${d.monto.toLocaleString()}</td>
                  <td className="px-4 py-3 text-slate-700">{d.fecha}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
