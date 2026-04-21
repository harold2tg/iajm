"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Venta } from "@/types/api";

export default function TiendaPage() {
  const { data, isLoading } = useQuery<Venta[]>({
    queryKey: ["tienda", "ventas"],
    queryFn: () => api.get("/tienda/ventas").then((r) => r.data),
  });

  if (isLoading) return <p className="p-6 text-slate-500">Cargando...</p>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Tienda</h1>
      <div className="rounded-lg border border-slate-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-slate-600">
            <tr>
              <th className="px-4 py-3 text-left font-medium">Fecha</th>
              <th className="px-4 py-3 text-left font-medium">Total</th>
              <th className="px-4 py-3 text-left font-medium">Observaciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {data?.map((v) => (
              <tr key={v.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 text-slate-700">{v.fecha}</td>
                <td className="px-4 py-3 text-slate-700">${v.total.toLocaleString()}</td>
                <td className="px-4 py-3 text-slate-500">{v.observaciones ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
