"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { authStorage } from "@/lib/auth";
import type { LoginResponse } from "@/types/api";

const schema = z.object({
  email: z.string().email("Email inválido"),
  password: z.string().min(1, "Requerido"),
});

type FormData = z.infer<typeof schema>;

export default function LoginPage() {
  const router = useRouter();
  const { register, handleSubmit, formState: { errors, isSubmitting }, setError } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    try {
      const res = await api.post<LoginResponse>("/auth/login", {
        email: data.email,
        password: data.password,
      });
      authStorage.setTokens(res.data.access_token, res.data.refresh_token);
      router.push("/dashboard");
    } catch {
      setError("root", { message: "Credenciales incorrectas" });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#1A4B8C]">
      <div className="w-full max-w-sm bg-white rounded-2xl shadow-lg border-t-4 border-t-[#F5C518] p-8">
        <h1 className="text-2xl font-bold text-[#1A4B8C] mb-1">IAM</h1>
        <p className="text-sm text-slate-500 mb-8">Iniciá sesión para continuar</p>

        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
          <div>
            <label className="text-sm font-medium text-slate-700">Email</label>
            <input
              {...register("email")}
              type="email"
              autoComplete="email"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-[#1A4B8C] focus:ring-2 focus:ring-[#1A4B8C]/20"
            />
            {errors.email && <p className="mt-1 text-xs text-[#C0392B]">{errors.email.message}</p>}
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700">Contraseña</label>
            <input
              {...register("password")}
              type="password"
              autoComplete="current-password"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-[#1A4B8C] focus:ring-2 focus:ring-[#1A4B8C]/20"
            />
            {errors.password && <p className="mt-1 text-xs text-[#C0392B]">{errors.password.message}</p>}
          </div>

          {errors.root && (
            <p className="rounded-lg bg-[#C0392B]/10 border border-[#C0392B]/30 px-3 py-2 text-sm text-[#C0392B]">
              {errors.root.message}
            </p>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="mt-2 w-full rounded-lg bg-[#F5C518] px-4 py-2 text-sm font-semibold text-[#1A1A1A] hover:bg-[#E67E22] hover:text-white disabled:opacity-50 transition-colors"
          >
            {isSubmitting ? "Ingresando..." : "Ingresar"}
          </button>
        </form>
      </div>
    </div>
  );
}
