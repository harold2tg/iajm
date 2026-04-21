"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { ItemInventario } from "@/types/api";

export default function InventarioPage() {
  const { data, isLoading } = useQuery<ItemInventario[]>({
    queryKey: ["inventario"],
    queryFn: () => api.get("/inventario/").then((r) => r.data),
  });

  if (isLoading) return <p className="p-6 text-slate-500">Cargando...</p>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Inventario</h1>
      <div className="rounded-lg border border-slate-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-slate-600">
            <tr>
              <th className="px-4 py-3 text-left font-medium">Nombre</th>
              <th className="px-4 py-3 text-left font-medium">Tipo</th>
              <th className="px-4 py-3 text-left font-medium">Estado</th>
              <th className="px-4 py-3 text-left font-medium">Origen</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {data?.map((item) => (
              <tr key={item.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 text-slate-700">{item.nombre}</td>
                <td className="px-4 py-3 text-slate-700">{item.tipo}</td>
                <td className="px-4 py-3 text-slate-700">{item.estado}</td>
                <td className="px-4 py-3 text-slate-700">{item.origen}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
