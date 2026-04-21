"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { ActividadParroquial } from "@/types/api";

export default function ParroquialPage() {
  const { data, isLoading } = useQuery<ActividadParroquial[]>({
    queryKey: ["parroquial"],
    queryFn: () => api.get("/parroquial/").then((r) => r.data),
  });

  if (isLoading) return <p className="p-6 text-slate-500">Cargando...</p>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Actividades Parroquiales</h1>
      <div className="rounded-lg border border-slate-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-slate-600">
            <tr>
              <th className="px-4 py-3 text-left font-medium">Nombre</th>
              <th className="px-4 py-3 text-left font-medium">Fecha</th>
              <th className="px-4 py-3 text-left font-medium">Entregado</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {data?.map((a) => (
              <tr key={a.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 text-slate-700">{a.nombre}</td>
                <td className="px-4 py-3 text-slate-700">{a.fecha}</td>
                <td className="px-4 py-3">
                  <span
                    className={cn(
                      "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
                      a.entregado
                        ? "bg-green-100 text-green-700"
                        : "bg-slate-100 text-slate-600"
                    )}
                  >
                    {a.entregado ? "Sí" : "No"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
