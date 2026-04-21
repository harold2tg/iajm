# IAJM — Coding Standards

## General
- Conventional commits: `feat:`, `fix:`, `chore:`, `refactor:`, `docs:`
- No secrets, credentials, or `.env` files committed
- All enums must match the backend exactly before hardcoding in frontend/mobile

## Backend (FastAPI / Python)
- Architecture by domain: `app/domains/<domain>/{models,schemas,repository,service,router}.py`
- Use Pydantic v2 for all schemas
- All DB operations go through the repository layer — no raw queries in routers
- Migrations via Alembic — never modify the DB schema directly
- Enums must be defined in `models.py` and reflected in `schemas.py`
- No print statements — use proper logging

## Frontend (Next.js 15 / TypeScript)
- All API types must live in `types/api.ts` — no inline type definitions
- Use React Query for all server state — no `useState` for API data
- Validate forms with Zod + react-hook-form
- No `any` types
- API calls go through `lib/api.ts` — never use fetch directly
- Endpoint: `/usuarios/me` (NOT `/auth/me`)

## Mobile (Flutter / Dart)
- Architecture feature-first: `lib/features/<feature>/{data,domain/models,presentation}/`
- No codegen — Dart models are manual with `fromJson/toJson`
- State management: `StateNotifierProvider` and `FutureProvider` (Riverpod)
- Always run `flutter analyze` with 0 issues before building APK
- Enums must match backend values exactly (lowercase, with underscores)

## Enums (source of truth: backend)
- `TipoGrupo`: `infancia`, `adolescencia`, `juventud`
- `TipoMiembro`: `infancia`, `adolescencia`, `juventud`
- `TipoAsesor`: `base`, `coordinador`, `de_apoyo`, `de_contingencia`
- `EstadoEncuentro`: `abierto`, `cerrado`
- `EstadoAsistencia`: `asistio`, `no_asistio`, `justificado`
