"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { api } from "@/lib/api";
import type { Grupo, Miembro, Asesor, Encuentro } from "@/types/api";

function grupoBorderColor(tipo: string): string {
  if (tipo === "infancia") return "border-t-[#27AE60]";
  if (tipo === "adolescencia") return "border-t-[#E67E22]";
  if (tipo === "juventud") return "border-t-[#1A4B8C]";
  return "border-t-[#1A4B8C]";
}

export default function DashboardPage() {
  const { data: grupos } = useQuery({
    queryKey: ["grupos"],
    queryFn: () => api.get<Grupo[]>("/grupos").then((r) => r.data),
  });
  const { data: miembros } = useQuery({
    queryKey: ["miembros"],
    queryFn: () => api.get<Miembro[]>("/miembros").then((r) => r.data),
  });
  const { data: asesores } = useQuery({
    queryKey: ["asesores"],
    queryFn: () => api.get<Asesor[]>("/asesores").then((r) => r.data),
  });
  const { data: encuentros } = useQuery({
    queryKey: ["encuentros"],
    queryFn: () => api.get<Encuentro[]>("/encuentros").then((r) => r.data),
  });

  const stats = [
    { label: "Grupos", value: grupos?.length ?? "—", href: "/grupos" },
    { label: "Miembros", value: miembros?.length ?? "—", href: "/miembros" },
    { label: "Asesores", value: asesores?.length ?? "—", href: "/asesores" },
    { label: "Encuentros", value: encuentros?.length ?? "—", href: "/encuentros" },
  ];

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-[#1A4B8C] mb-6">Dashboard</h1>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((s) => (
          <Link
            key={s.label}
            href={s.href}
            className="rounded-xl border border-slate-200 border-l-4 border-l-[#F5C518] bg-white p-5 hover:shadow-sm transition-all"
          >
            <p className="text-sm text-slate-500 mb-1">{s.label}</p>
            <p className="text-3xl font-bold text-[#1A4B8C]">{s.value}</p>
          </Link>
        ))}
      </div>

      {/* Grupos */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-[#1A4B8C]">Grupos</h2>
          <Link href="/grupos" className="text-sm text-[#1A4B8C] hover:underline">Ver todos</Link>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {grupos?.map((g) => {
            const total = miembros?.filter((m) => m.grupo_id === g.id && m.activo).length ?? 0;
            return (
              <div
                key={g.id}
                className={`rounded-xl border border-slate-200 border-t-4 bg-white p-4 ${grupoBorderColor(g.tipo)}`}
              >
                <p className="font-semibold text-[#1A1A1A]">{g.nombre}</p>
                <p className="text-sm text-slate-500 mt-1">{g.edad_minima}–{g.edad_maxima} años</p>
                <div className="mt-3 flex items-center justify-between">
                  <span className="text-2xl font-bold text-[#1A4B8C]">{total}</span>
                  <span className="text-xs text-slate-400">integrantes</span>
                </div>
                <div className="mt-2 flex items-center justify-between">
                  <span className="text-xs text-slate-400 capitalize">{g.tipo}</span>
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${g.activo ? "bg-[#27AE60]/10 text-[#27AE60]" : "bg-slate-100 text-slate-500"}`}>
                    {g.activo ? "Activo" : "Inactivo"}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Miembros recientes */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-[#1A4B8C]">Miembros recientes</h2>
          <Link href="/miembros" className="text-sm text-[#1A4B8C] hover:underline">Ver todos</Link>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-[#1A4B8C]">
                <th className="text-left px-4 py-3 font-medium text-white">Nombre</th>
                <th className="text-left px-4 py-3 font-medium text-white">Tipo</th>
                <th className="text-left px-4 py-3 font-medium text-white">Ingreso</th>
                <th className="text-left px-4 py-3 font-medium text-white">Estado</th>
              </tr>
            </thead>
            <tbody>
              {miembros?.slice(0, 5).map((m, i) => (
                <tr
                  key={m.id}
                  className={`border-b border-slate-50 last:border-0 ${i % 2 === 0 ? "bg-white" : "bg-slate-50"}`}
                >
                  <td className="px-4 py-3 font-medium text-[#1A1A1A]">{m.nombre_completo}</td>
                  <td className="px-4 py-3 text-slate-500 capitalize">{m.tipo}</td>
                  <td className="px-4 py-3 text-slate-500">{m.fecha_ingreso}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${m.activo ? "bg-[#27AE60]/10 text-[#27AE60]" : "bg-slate-100 text-slate-500"}`}>
                      {m.activo ? "Activo" : "Inactivo"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
