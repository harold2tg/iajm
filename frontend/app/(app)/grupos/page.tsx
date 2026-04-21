"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { api } from "@/lib/api";
import type { Grupo, GrupoUpdate } from "@/types/api";

const editarSchema = z.object({
  nombre: z.string().min(1, "Requerido").optional(),
  edad_minima: z.string().optional(),
  edad_maxima: z.string().optional(),
  activo: z.boolean().optional(),
});

type EditarForm = z.infer<typeof editarSchema>;

function grupoBorderColor(tipo: string): string {
  if (tipo === "infancia") return "border-l-[#27AE60]";
  if (tipo === "adolescencia") return "border-l-[#E67E22]";
  if (tipo === "juventud") return "border-l-[#1A4B8C]";
  return "border-l-[#1A4B8C]";
}

export default function GruposPage() {
  const queryClient = useQueryClient();
  const [modal, setModal] = useState<"editar" | null>(null);
  const [selected, setSelected] = useState<Grupo | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["grupos"],
    queryFn: () => api.get<Grupo[]>("/grupos").then((r) => r.data),
  });

  const editar = useMutation({
    mutationFn: ({ id, data }: { id: string; data: GrupoUpdate }) =>
      api.patch(`/grupos/${id}`, data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["grupos"] });
      setModal(null);
    },
  });

  const editarForm = useForm<EditarForm>({ resolver: zodResolver(editarSchema) });

  function abrirEditar(g: Grupo) {
    setSelected(g);
    editarForm.reset({
      nombre: g.nombre,
      edad_minima: String(g.edad_minima),
      edad_maxima: String(g.edad_maxima),
      activo: g.activo,
    });
    setModal("editar");
  }

  function cerrar() {
    setModal(null);
    setSelected(null);
    editarForm.reset();
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-[#1A4B8C]">Grupos</h1>
      </div>

      {isLoading && <p className="text-slate-500 text-sm">Cargando...</p>}

      {/* Lista */}
      <div className="grid gap-3">
        {data?.map((grupo) => (
          <div
            key={grupo.id}
            className={`rounded-xl border border-slate-200 border-l-4 bg-white p-4 flex items-center justify-between ${grupoBorderColor(grupo.tipo)}`}
          >
            <div>
              <p className="font-semibold text-[#1A1A1A]">{grupo.nombre}</p>
              <p className="text-sm text-slate-500 capitalize">{grupo.tipo} · {grupo.edad_minima}–{grupo.edad_maxima} años</p>
            </div>
            <div className="flex items-center gap-2">
              <span className={`text-xs font-medium px-2 py-1 rounded-full ${grupo.activo ? "bg-[#27AE60]/10 text-[#27AE60]" : "bg-slate-100 text-slate-500"}`}>
                {grupo.activo ? "Activo" : "Inactivo"}
              </span>
              <button
                onClick={() => abrirEditar(grupo)}
                className="text-xs bg-[#1A4B8C] text-white px-3 py-1.5 rounded-lg hover:bg-[#E67E22] transition-colors"
              >
                Editar
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Modal Editar */}
      {modal === "editar" && selected && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-md p-6 shadow-xl">
            <h2 className="text-lg font-bold text-[#1A4B8C] mb-4">Editar grupo</h2>
            <form onSubmit={editarForm.handleSubmit((d) => editar.mutate({ id: selected.id, data: {
              ...d,
              edad_minima: d.edad_minima !== undefined ? Number(d.edad_minima) : undefined,
              edad_maxima: d.edad_maxima !== undefined ? Number(d.edad_maxima) : undefined,
            } }))} className="space-y-3">
              <div>
                <label className="text-sm font-medium text-slate-700">Nombre</label>
                <input {...editarForm.register("nombre")} className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]" />
                {editarForm.formState.errors.nombre && <p className="text-xs text-[#C0392B] mt-1">{editarForm.formState.errors.nombre.message}</p>}
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-sm font-medium text-slate-700">Edad mínima</label>
                  <input type="number" {...editarForm.register("edad_minima")} className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]" />
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-700">Edad máxima</label>
                  <input type="number" {...editarForm.register("edad_maxima")} className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]" />
                </div>
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" id="activo-grupo" {...editarForm.register("activo")} className="w-4 h-4 accent-[#27AE60]" />
                <label htmlFor="activo-grupo" className="text-sm font-medium text-slate-700">Activo</label>
              </div>
              {editar.isError && <p className="text-xs text-[#C0392B]">Error al actualizar el grupo</p>}
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={cerrar} className="px-4 py-2 text-sm rounded-lg border border-slate-300 text-slate-600 hover:bg-slate-50">Cancelar</button>
                <button type="submit" disabled={editar.isPending} className="px-4 py-2 text-sm rounded-lg bg-[#F5C518] text-[#1A1A1A] font-semibold hover:bg-[#E67E22] hover:text-white transition-colors disabled:opacity-50">
                  {editar.isPending ? "Guardando..." : "Guardar"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
