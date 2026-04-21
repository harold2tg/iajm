"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { api } from "@/lib/api";
import type { Miembro, MiembroCreate, MiembroUpdate } from "@/types/api";

const crearSchema = z.object({
  nombre_completo: z.string().min(1, "Requerido"),
  fecha_nacimiento: z.string().min(1, "Requerido"),
  fecha_ingreso: z.string().min(1, "Requerido"),
  telefono_personal: z.string().optional(),
  nombre_acudiente: z.string().optional(),
  telefono_acudiente: z.string().optional(),
});

const editarSchema = z.object({
  nombre_completo: z.string().min(1, "Requerido").optional(),
  telefono_personal: z.string().optional(),
  nombre_acudiente: z.string().optional(),
  telefono_acudiente: z.string().optional(),
});

type CrearForm = z.infer<typeof crearSchema>;
type EditarForm = z.infer<typeof editarSchema>;

export default function MiembrosPage() {
  const queryClient = useQueryClient();
  const [modal, setModal] = useState<"crear" | "editar" | "desactivar" | null>(null);
  const [selected, setSelected] = useState<Miembro | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["miembros"],
    queryFn: () => api.get<Miembro[]>("/miembros").then((r) => r.data),
  });

  const crear = useMutation({
    mutationFn: (data: MiembroCreate) => api.post("/miembros", data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["miembros"] });
      setModal(null);
    },
  });

  const editar = useMutation({
    mutationFn: ({ id, data }: { id: string; data: MiembroUpdate }) =>
      api.patch(`/miembros/${id}`, data).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["miembros"] });
      setModal(null);
    },
  });

  const desactivar = useMutation({
    mutationFn: (id: string) => api.delete(`/miembros/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["miembros"] });
      setModal(null);
    },
  });

  const crearForm = useForm<CrearForm>({ resolver: zodResolver(crearSchema) });
  const editarForm = useForm<EditarForm>({ resolver: zodResolver(editarSchema) });

  function abrirEditar(m: Miembro) {
    setSelected(m);
    editarForm.reset({
      nombre_completo: m.nombre_completo,
      telefono_personal: m.telefono_personal ?? "",
      nombre_acudiente: m.nombre_acudiente ?? "",
      telefono_acudiente: "",
    });
    setModal("editar");
  }

  function abrirDesactivar(m: Miembro) {
    setSelected(m);
    setModal("desactivar");
  }

  function cerrar() {
    setModal(null);
    setSelected(null);
    crearForm.reset();
    editarForm.reset();
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-[#1A4B8C]">Miembros</h1>
        <button
          onClick={() => { crearForm.reset(); setModal("crear"); }}
          className="bg-[#F5C518] text-[#1A1A1A] font-semibold px-4 py-2 rounded-lg hover:bg-[#E67E22] hover:text-white transition-colors"
        >
          + Nuevo miembro
        </button>
      </div>

      {isLoading && <p className="text-slate-500 text-sm">Cargando...</p>}

      {/* Lista */}
      <div className="grid gap-3">
        {data?.map((m) => (
          <div key={m.id} className="rounded-xl border border-slate-200 bg-white p-4 flex items-center justify-between">
            <div>
              <p className="font-semibold text-[#1A1A1A]">{m.nombre_completo}</p>
              <p className="text-sm text-slate-500">
                {m.tipo}
                {m.nombre_grupo && <> · <span className="text-[#1A4B8C] font-medium">{m.nombre_grupo}</span></>}
                {" · "}ingresó {m.fecha_ingreso}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span className={`text-xs font-medium px-2 py-1 rounded-full ${m.activo ? "bg-[#27AE60]/10 text-[#27AE60]" : "bg-slate-100 text-slate-500"}`}>
                {m.activo ? "Activo" : "Inactivo"}
              </span>
              <button
                onClick={() => abrirEditar(m)}
                className="text-xs bg-[#1A4B8C] text-white px-3 py-1.5 rounded-lg hover:bg-[#E67E22] transition-colors"
              >
                Editar
              </button>
              {m.activo && (
                <button
                  onClick={() => abrirDesactivar(m)}
                  className="text-xs bg-[#C0392B] text-white px-3 py-1.5 rounded-lg hover:opacity-80 transition-opacity"
                >
                  Desactivar
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Modal Crear */}
      {modal === "crear" && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-md p-6 shadow-xl">
            <h2 className="text-lg font-bold text-[#1A4B8C] mb-4">Nuevo miembro</h2>
            <form onSubmit={crearForm.handleSubmit((d) => crear.mutate(d))} className="space-y-3">
              <div>
                <label className="text-sm font-medium text-slate-700">Nombre completo *</label>
                <input {...crearForm.register("nombre_completo")} className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]" />
                {crearForm.formState.errors.nombre_completo && <p className="text-xs text-[#C0392B] mt-1">{crearForm.formState.errors.nombre_completo.message}</p>}
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-sm font-medium text-slate-700">Fecha nacimiento *</label>
                  <input type="date" {...crearForm.register("fecha_nacimiento")} className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]" />
                  {crearForm.formState.errors.fecha_nacimiento && <p className="text-xs text-[#C0392B] mt-1">{crearForm.formState.errors.fecha_nacimiento.message}</p>}
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-700">Fecha ingreso *</label>
                  <input type="date" {...crearForm.register("fecha_ingreso")} className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]" />
                  {crearForm.formState.errors.fecha_ingreso && <p className="text-xs text-[#C0392B] mt-1">{crearForm.formState.errors.fecha_ingreso.message}</p>}
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Teléfono personal</label>
                <input {...crearForm.register("telefono_personal")} className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]" />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Nombre acudiente</label>
                <input {...crearForm.register("nombre_acudiente")} className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]" />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Teléfono acudiente</label>
                <input {...crearForm.register("telefono_acudiente")} className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]" />
              </div>
              {crear.isError && <p className="text-xs text-[#C0392B]">Error al crear el miembro</p>}
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
          <div className="bg-white rounded-2xl w-full max-w-md p-6 shadow-xl">
            <h2 className="text-lg font-bold text-[#1A4B8C] mb-4">Editar miembro</h2>
            <form onSubmit={editarForm.handleSubmit((d) => editar.mutate({ id: selected.id, data: d }))} className="space-y-3">
              <div>
                <label className="text-sm font-medium text-slate-700">Nombre completo</label>
                <input {...editarForm.register("nombre_completo")} className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]" />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Teléfono personal</label>
                <input {...editarForm.register("telefono_personal")} className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]" />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Nombre acudiente</label>
                <input {...editarForm.register("nombre_acudiente")} className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]" />
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700">Teléfono acudiente</label>
                <input {...editarForm.register("telefono_acudiente")} className="mt-1 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#1A4B8C]" />
              </div>
              {editar.isError && <p className="text-xs text-[#C0392B]">Error al actualizar el miembro</p>}
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
            <h2 className="text-lg font-bold text-[#1A1A1A] mb-2">¿Desactivar miembro?</h2>
            <p className="text-sm text-slate-500 mb-6">
              Esto desactivará a <span className="font-semibold text-[#1A1A1A]">{selected.nombre_completo}</span>. Podrás reactivarlo más adelante.
            </p>
            {desactivar.isError && <p className="text-xs text-[#C0392B] mb-3">Error al desactivar el miembro</p>}
            <div className="flex justify-end gap-3">
              <button onClick={cerrar} className="px-4 py-2 text-sm rounded-lg border border-slate-300 text-slate-600 hover:bg-slate-50">Cancelar</button>
              <button
                onClick={() => desactivar.mutate(selected.id)}
                disabled={desactivar.isPending}
                className="px-4 py-2 text-sm rounded-lg bg-[#C0392B] text-white font-semibold hover:opacity-80 transition-opacity disabled:opacity-50"
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
