"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/grupos", label: "Grupos" },
  { href: "/miembros", label: "Miembros" },
  { href: "/asesores", label: "Asesores" },
  { href: "/encuentros", label: "Encuentros" },
  { href: "/tesoreria", label: "Tesorería" },
  { href: "/gastos", label: "Gastos" },
  { href: "/tienda", label: "Tienda" },
  { href: "/inventario", label: "Inventario" },
  { href: "/parroquial", label: "Parroquial" },
  { href: "/reportes", label: "Reportes" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-60 shrink-0 bg-[#1A4B8C] flex flex-col h-full">
      <div className="px-6 py-5 border-b border-white/10">
        <span className="font-bold text-white text-lg tracking-wide">IAM</span>
      </div>
      <nav className="flex-1 px-3 py-4 flex flex-col gap-1">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "rounded-lg px-3 py-2 text-sm font-medium transition-colors",
              pathname === item.href
                ? "bg-[#F5C518] text-[#1A1A1A]"
                : "text-white/80 hover:bg-white/10 hover:text-white"
            )}
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
