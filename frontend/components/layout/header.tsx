"use client";

import { useRouter } from "next/navigation";
import { authStorage } from "@/lib/auth";

export function Header() {
  const router = useRouter();

  const handleLogout = () => {
    authStorage.clear();
    router.push("/login");
  };

  return (
    <header className="h-14 shrink-0 border-b-2 border-[#F5C518] bg-white flex items-center justify-between px-6">
      <span className="font-bold text-[#1A4B8C] text-base tracking-wide">
        Infancia y Adolescencia Misionera
      </span>
      <button
        onClick={handleLogout}
        className="text-sm text-slate-500 hover:text-[#1A4B8C] transition-colors"
      >
        Cerrar sesión
      </button>
    </header>
  );
}
