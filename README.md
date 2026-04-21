# IAJM — Sistema de Gestión Integral

Sistema de gestión para grupos parroquiales de **Infancia, Adolescencia y Misión Parroquial**.

Administra miembros, asesores, encuentros semanales, tesorería e inventario. Disponible como **app web** (Next.js) y **app móvil** (Flutter), respaldadas por una **API centralizada** (FastAPI + PostgreSQL).

---

## Stack

| Capa | Tecnología |
|---|---|
| **API** | FastAPI · Python 3.11+ · SQLAlchemy 2.0 · Alembic · Pydantic v2 |
| **Base de datos** | PostgreSQL 16 |
| **Web** | Next.js 15 (App Router) · TypeScript · Tailwind CSS |
| **Móvil** | Flutter 3.41+ · Dart · Riverpod · Dio |
| **Infraestructura** | Docker Compose · Nginx · Digital Ocean |

---

## Grupos del sistema

Los grupos son fijos y no se pueden crear ni eliminar:

| Nombre | Tipo | Rango de edad |
|---|---|---|
| Trigo Verde | Infancia | 4 – 6 años |
| Trigo Maduro | Infancia | 7 – 9 años |
| Trigo Maduro Avanzado | Infancia | 10 – 12 años |
| Adolescencia | Adolescencia | 13 – 15 años |
| Juventud | Juventud | 16 – 24 años |

---

## Estructura del proyecto

```
iajm/
├── backend/
│   ├── app/
│   │   ├── core/           # config, database, security, dependencies
│   │   ├── domains/        # usuarios, grupos, miembros, asesores, encuentros, ...
│   │   ├── cron/           # jobs APScheduler (reasignación grupos + cuotas)
│   │   └── main.py
│   ├── alembic/            # migraciones
│   ├── scripts/
│   │   └── seed.py
│   └── tests/
├── frontend/
│   ├── app/                # Next.js App Router
│   ├── components/
│   ├── lib/                # api.ts, auth.ts, utils.ts
│   └── types/
├── mobile/
│   └── lib/
│       ├── core/           # network, router, theme
│       └── features/       # auth, grupos, miembros, asesores, encuentros
├── docker/
│   ├── backend.Dockerfile
│   └── nginx/nginx.conf
├── docker-compose.yml      # desarrollo
└── docker-compose.prod.yml # producción
```

---

## Desarrollo local

### Requisitos

- Docker Desktop
- Python 3.11+ · Poetry
- Node.js 20+
- Flutter 3.41+

### 1. Base de datos

```bash
docker compose up -d db
```

Credenciales dev: `iajm` / `iajm` / `iajm_db` en `127.0.0.1:5432`

### 2. Backend

```bash
cd backend
export PATH="$HOME/.local/bin:$PATH"
poetry install
poetry run alembic upgrade head
poetry run python scripts/seed.py   # carga grupos, admin, asesores y miembros de ejemplo
poetry run uvicorn app.main:app --reload --port 8000
```

API disponible en `http://localhost:8000/api/docs`

Credenciales seed: `admin@iajm.org` / `Admin1234!`

### 3. Frontend web

```bash
cd frontend
npm install
npm run dev
```

App disponible en `http://localhost:3000`

### 4. App móvil

```bash
cd mobile
flutter pub get
flutter run
```

Configurar la URL del backend en `mobile/lib/core/network/api_client.dart`.

### 5. Tests

```bash
cd backend
poetry run pytest -v
```

---

## Dominios del sistema

| Dominio | Descripción |
|---------|-------------|
| `usuarios` | Autenticación JWT, roles, lockout por intentos fallidos |
| `grupos` | 5 grupos parroquiales fijos con rango de edad |
| `miembros` | Niños/adolescentes, reasignación automática por edad |
| `asesores` | Asesores con tipo (`base`, `coordinador`, `de_apoyo`, `de_contingencia`) y cuotas mensuales |
| `encuentros` | Reuniones semanales con asistencia y métricas |
| `tesoreria` | Actividades pro-fondos, donaciones, ingresos |
| `gastos` | Categorías y registro de gastos |
| `tienda` | Ventas con detalle de ítems |
| `inventario` | Ítems con tipo, estado y origen |
| `parroquial` | Actividades parroquiales con entrega |

---

## Despliegue en Digital Ocean

### Requisitos del servidor

- Droplet Ubuntu 22.04 LTS (mínimo 2 GB RAM)
- Docker + Docker Compose instalados
- Dominio apuntando al IP del Droplet

### Variables de entorno

Crear `.env` en la raíz del proyecto en el servidor:

```env
POSTGRES_USER=iajm
POSTGRES_PASSWORD=<password-seguro>
POSTGRES_DB=iajm_db
DATABASE_URL=postgresql://iajm:<password-seguro>@db:5432/iajm_db
SECRET_KEY=<output de: openssl rand -hex 32>
```

> **NUNCA** commitear el `.env` al repositorio.

### SSL con Let's Encrypt

```bash
apt install -y certbot
certbot certonly --standalone -d tudominio.com
```

Actualizar `docker/nginx/nginx.conf` con el dominio real y descomentar el bloque SSL.

### Deploy

```bash
git clone <repo-url> /opt/iajm
cd /opt/iajm
nano .env

docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
docker compose -f docker-compose.prod.yml exec backend python scripts/seed.py
```

### Actualizar

```bash
cd /opt/iajm
git pull
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### Backup de la base de datos

```bash
# Exportar
docker compose -f docker-compose.prod.yml exec db \
  pg_dump -U iajm iajm_db > backup_$(date +%Y%m%d).sql

# Restaurar
docker compose -f docker-compose.prod.yml exec -T db \
  psql -U iajm iajm_db < backup_20260101.sql
```

---

## Licencia

Uso interno — Parroquia IAJM. Todos los derechos reservados.
