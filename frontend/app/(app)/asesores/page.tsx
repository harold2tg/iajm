"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { api } from "@/lib/api";
import type { Asesor, AsesorUpdate, Grupo } from "@/types/api";

const crearSchema = z.object({
  nombre_completo: z.string().min(1, "Requerido"),
  telefono: z.string().min(1, "Requerido"),
  tipo: z.enum(["base", "coordinador", "de_apoyo", "de_contingencia"]),
  fecha_nacimiento: z.string().min(1, "Requerido"),
  grupo_id: z.string().min(1, "Seleccioná un grupo"),
});

const editarSchema = z.object({
  nombre_completo: z.string().min(1, "Requerido").optional(),
  telefono: z.string().optional(),
  fecha_nacimiento: z.string().optional(),
  activo: z.boolean().optional(),
});

type CrearForm = z.infer<typeof crearSchema>;
type EditarForm = z.infer<typeof editarSchema>;

export default function AsesoresPage() {
  const queryClient = useQueryClient();
  const [modal, setModal] = useState<"crear" | "editar" | "desactivar" | null>(null);
  const [selected, setSelected] = useState<Asesor | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["asesores"],
    queryFn: () => api.get<Asesor[]>("/asesores").then((r) => r.data),
  });

  const { data: grupos } = useQuery({
    queryKey: ["grupos"],
    queryFn: () => api.get<Grupo[]>("/grupos").then((r) => r.data),
  });

  const crear = useMutation({
    mutationFn: (d: CrearForm) =>
      api.post("/asesores", {
        nombre_completo: d.nombre_completo,
        telefono: d.telefono,
        tipo: d.tipo,
        fecha_nacimiento: d.fecha_nacimiento,
        grupo_ids: [d.grupo_id],
      }).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["asesores"] });
      setModal(null);
    },
  });

  const editar = useMutation({
    mutationFn: ({ id, data }: { id: string; data: AsesorUpdate }) =>
      api.patch(`/asesores/${id}`, data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["asesores"] });
      setModal(null);
    },
  });

  const desactivar = useMutation({
    mutationFn: (id: string) => api.delete(`/asesores/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["asesores"] });
      setModal(null);
    },
  });

  const crearForm = useForm<CrearForm>({ resolver: zodResolver(crearSchema) });
  const editarForm = useForm<EditarForm>({ resolver: zodResolver(editarSchema) });

  function abrirEditar(a: Asesor) {
    setSelected(a);
    editarForm.reset({
      nombre_completo: a.nombre_completo,
      telefono: a.telefono,
      fecha_nacimiento: a.fecha_nacimiento ?? "",
      activo: a.activo,
    });
    setModal("editar");
  }

  function cerrar() {
    setModal(null);
    setSelected(null);
    crearForm.reset();
    editarForm.reset();
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-[#1A4B8C]">Asesores</h1>
        <button
          onClick={() => { crearForm.reset(); setModal("crear"); }}
          className="bg-[#F5C518] text-[#1A1A1A] font-semibold px-4 py-2 rounded-lg hover:bg-[#E67E22] hover:text-white transition-colors"
        >
          + Nuevo asesor
        </button>
      </div>

      {isLoading && <p className="text-slate-500 text-sm">Cargando...</p>}

      <div className="grid gap-3">
        {data?.map((a) => {
          return (
            <div key={a.id} className="rounded-xl border border-slate-200 bg-white p-4 flex items-center justify-between">
              <div>
                <p className="font-semibold text-[#1A1A1A]">{a.nombre_completo}</p>
                <p className="text-sm text-slate-500">{a.telefono}{a.fecha_nacimiento ? ` · ${a.fecha_nacimiento}` : ""}</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-[#1A4B8C]/10 text-[#1A4B8C] capitalize">{a.tipo}</span>
                  {a.grupos?.[0] && (
                    <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-[#F5C518]/30 text-[#1A1A1A]">
                      {a.grupos[0].nombre}
                    </span>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`text-xs font-medium px-2 py-1 rounded-full ${a.activo ? "bg-[#27AE60]/10 text-[#27AE60]" : "bg-slate-100 text-slate-500"}`}>
                  {a.activo ? "Activo" : "Inactivo"}
                </span>
                <button
                  onClick={() => abrirEditar(a)}
                  className="text-xs bg-[#1A4B8C] text-white px-3 py-1.5 rounded-lg hover:bg-[#E67E22] transition-colors"
                >
                  Editar
                </button>
                {a.activo && (
                  <button
                    onClick={() => { setSelected(a); setModal("desactivar"); }}
                    className="text-xs bg-[#C0392B] text-white px-3 py-1.5 rounded-lg hover:opacity-80 transition-opacity"
                  >
                    Desactivar
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Modal Crear */}
      {modal === "crear" && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-md p-6 shadow-xl border-t-4 border-[#F5C518]">
            <h2 className="text-lg font-bold text-[#1A4B8C] mb-4">Nuevo asesor</h2>
            <form onSubmit={crearForm.handleSubmit((d) => crear.mutate(d))} className="space-y-3">
              <div>
                <label className="text-sm font-medium text-slate-700">Nombre completo *</label>
                <input {...crearForm.register("nombre_completo")} className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]" />
                {crearForm.formState.errors.nombre_completo && <p className="text-xs text-[#C0392B] mt-1">{crearForm.formState.errors.nombre_completo.message}</p>}
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Teléfono *</label>
                <input {...crearForm.register("telefono")} className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]" />
                {crearForm.formState.errors.telefono && <p className="text-xs text-[#C0392B] mt-1">{crearForm.formState.errors.telefono.message}</p>}
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Tipo *</label>
                <select {...crearForm.register("tipo")} className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C] bg-white">
                  <option value="">Seleccionar...</option>
                  <option value="base">Base</option>
                  <option value="coordinador">Coordinador</option>
                  <option value="de_apoyo">De apoyo</option>
                  <option value="de_contingencia">De contingencia</option>
                </select>
                {crearForm.formState.errors.tipo && <p className="text-xs text-[#C0392B] mt-1">{crearForm.formState.errors.tipo.message}</p>}
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Fecha de nacimiento *</label>
                <input type="date" {...crearForm.register("fecha_nacimiento")} className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]" />
                {crearForm.formState.errors.fecha_nacimiento && <p className="text-xs text-[#C0392B] mt-1">{crearForm.formState.errors.fecha_nacimiento.message}</p>}
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Grupo asignado *</label>
                <select {...crearForm.register("grupo_id")} className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C] bg-white">
                  <option value="">Seleccionar grupo...</option>
                  {grupos?.map((g) => (
                    <option key={g.id} value={g.id}>
                      {g.nombre} ({g.edad_minima}–{g.edad_maxima} años)
                    </option>
                  ))}
                </select>
                {crearForm.formState.errors.grupo_id && <p className="text-xs text-[#C0392B] mt-1">{crearForm.formState.errors.grupo_id.message}</p>}
              </div>
              {crear.isError && <p className="text-xs text-[#C0392B]">Error al crear el asesor</p>}
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={cerrar} className="px-4 py-2 text-sm rounded-lg border border-slate-300 text-slate-600 hover:bg-slate-50">Cancelar</button>
                <button type="submit" disabled={crear.isPending} className="px-4 py-2 text-sm rounded-lg bg-[#F5C518] text-[#1A1A1A] font-semibold hover:bg-[#E67E22] hover:text-white transition-colors disabled:opacity-50">
                  {crear.isPending ? "Guardando..." : "Guardar"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Editar */}
      {modal === "editar" && selected && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-md p-6 shadow-xl border-t-4 border-[#1A4B8C]">
            <h2 className="text-lg font-bold text-[#1A4B8C] mb-4">Editar asesor</h2>
            <form onSubmit={editarForm.handleSubmit((d) => editar.mutate({ id: selected.id, data: d }))} className="space-y-3">
              <div>
                <label className="text-sm font-medium text-slate-700">Nombre completo</label>
                <input {...editarForm.register("nombre_completo")} className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]" />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Teléfono</label>
                <input {...editarForm.register("telefono")} className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]" />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Fecha de nacimiento</label>
                <input type="date" {...editarForm.register("fecha_nacimiento")} className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]" />
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" id="activo-asesor" {...editarForm.register("activo")} className="w-4 h-4 accent-[#27AE60]" />
                <label htmlFor="activo-asesor" className="text-sm font-medium text-slate-700">Activo</label>
              </div>
              {editar.isError && <p className="text-xs text-[#C0392B]">Error al actualizar</p>}
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

      {/* Modal Desactivar */}
      {modal === "desactivar" && selected && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-sm p-6 shadow-xl">
            <h2 className="text-lg font-bold text-[#1A1A1A] mb-2">¿Desactivar asesor?</h2>
            <p className="text-sm text-slate-500 mb-6">
              Esto desactivará a <span className="font-semibold text-[#1A1A1A]">{selected.nombre_completo}</span>.
            </p>
            {desactivar.isError && <p className="text-xs text-[#C0392B] mb-3">Error al desactivar</p>}
            <div className="flex justify-end gap-3">
              <button onClick={cerrar} className="px-4 py-2 text-sm rounded-lg border border-slate-300 text-slate-600 hover:bg-slate-50">Cancelar</button>
              <button
                onClick={() => desactivar.mutate(selected.id)}
                disabled={desactivar.isPending}
                className="px-4 py-2 text-sm rounded-lg bg-[#C0392B] text-white font-semibold hover:opacity-80 disabled:opacity-50"
              >
                {desactivar.isPending ? "Desactivando..." : "Confirmar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
