# IAJM — Integrated Management System

**IAJM (Infancia, Adolescencia y Juventud Misionera)** is an integrated management system designed to support the organization and administration of parish groups dedicated to children, adolescents and young people.

The system provides a centralized platform for managing members, advisors, groups, weekly meetings, attendance, finances, inventory and other parish activities.

The project includes:

* 🌐 Web application
* 📱 Mobile application
* ⚙️ Centralized REST API
* 🗄️ PostgreSQL database
* 🐳 Docker-based infrastructure

> **This is the first version of the project and represents its initial functional state. The system is actively evolving and its architecture, features and workflows may change as the project grows.**

---

## 🎯 Project Purpose

The purpose of IAJM is to provide a centralized technological platform for managing the different activities and processes involved in parish missionary groups.

The project aims to reduce manual administrative work and provide a single source of information for:

* Members
* Advisors
* Groups
* Weekly meetings
* Attendance
* Financial activities
* Expenses
* Inventory
* Sales
* Parish activities

The system is designed to grow progressively according to the real needs of the parish community.

---

## 🚧 Project Status

### Version 1 — Initial Release

This repository represents the **first version of IAJM**.

At this stage, the project establishes the initial architecture and core functionality of the system.

The current implementation includes:

* Backend API
* Web application
* Mobile application
* Authentication
* User roles
* Member management
* Advisor management
* Group management
* Weekly meetings
* Attendance tracking
* Financial management
* Expense management
* Store management
* Inventory management
* Parish activities
* Database migrations
* Development infrastructure
* Production infrastructure

The project should be considered an **initial version rather than a finished product**.

Future versions may introduce new functionality, improve existing workflows, change the architecture and refine the user experience.

---

## 🏗️ Architecture

IAJM follows a multi-platform architecture centered around a single backend API.

```text
                         ┌──────────────────┐
                         │      Users       │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
             ┌──────────────┐            ┌──────────────┐
             │ Web Platform │            │ Mobile App   │
             │   Next.js    │            │   Flutter    │
             └───────┬──────┘            └──────┬───────┘
                     │                          │
                     └──────────┬───────────────┘
                                │
                                ▼
                      ┌──────────────────┐
                      │    FastAPI API   │
                      │     Backend      │
                      └────────┬─────────┘
                               │
                               ▼
                      ┌──────────────────┐
                      │   PostgreSQL     │
                      │     Database     │
                      └──────────────────┘
```

The web and mobile applications consume the same centralized API, providing a consistent data and business-logic layer.

---

## 🧰 Technology Stack

| Layer                   | Technology     |
| ----------------------- | -------------- |
| API                     | FastAPI        |
| Language                | Python         |
| ORM                     | SQLAlchemy     |
| Migrations              | Alembic        |
| Validation              | Pydantic       |
| Database                | PostgreSQL     |
| Web                     | Next.js        |
| Web Language            | TypeScript     |
| Web UI                  | Tailwind CSS   |
| Mobile                  | Flutter        |
| Mobile Language         | Dart           |
| Mobile State Management | Riverpod       |
| Mobile HTTP Client      | Dio            |
| Infrastructure          | Docker Compose |
| Reverse Proxy           | Nginx          |
| Deployment              | DigitalOcean   |

---

## 🧩 Main Domains

The system is organized around several business domains:

| Domain       | Description                                       |
| ------------ | ------------------------------------------------- |
| `usuarios`   | Authentication, users, roles and account security |
| `grupos`     | Management of missionary groups                   |
| `miembros`   | Children, adolescents and young members           |
| `asesores`   | Advisors and their roles                          |
| `encuentros` | Weekly meetings and attendance                    |
| `tesoreria`  | Fundraising activities and income                 |
| `gastos`     | Expense categories and records                    |
| `tienda`     | Product sales                                     |
| `inventario` | Inventory management                              |
| `parroquial` | Parish activities                                 |

---

## 🔐 Authentication and Security

The initial version includes authentication and role-based access control.

The system includes:

* JWT authentication
* User roles
* Failed-login attempt tracking
* Account lockout
* Protected API endpoints

Sensitive credentials and security configuration should be handled through environment variables.

---

## 📁 Project Structure

```text
iajm/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── domains/
│   │   ├── cron/
│   │   └── main.py
│   ├── alembic/
│   ├── scripts/
│   └── tests/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── types/
│
├── mobile/
│   └── lib/
│
├── docker/
│   ├── backend.Dockerfile
│   └── nginx/
│
├── docker-compose.yml
├── docker-compose.prod.yml
├── AGENTS.md
├── SRS.md
└── README.md
```

---

## 🐳 Infrastructure

The project includes Docker configurations for development and production environments.

### Development

```bash
docker compose up -d
```

### Production

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

The infrastructure includes:

* PostgreSQL
* FastAPI backend
* Nginx
* Web application
* Supporting services

---

## 💻 Local Development

### Requirements

* Docker Desktop
* Python
* Poetry
* Node.js
* Flutter

### Backend

```bash
cd backend

poetry install

poetry run alembic upgrade head

poetry run python scripts/seed.py

poetry run uvicorn app.main:app --reload --port 8000
```

### Web Application

```bash
cd frontend

npm install

npm run dev
```

### Mobile Application

```bash
cd mobile

flutter pub get

flutter run
```

---

## 🧪 Testing

Backend tests can be executed with:

```bash
cd backend

poetry run pytest -v
```

Testing will continue to expand as the project evolves.

---

## 🗃️ Database

The project uses PostgreSQL as its primary relational database.

Database schema changes are managed using Alembic migrations.

```bash
poetry run alembic upgrade head
```

Development data can be initialized using the seed script:

```bash
poetry run python scripts/seed.py
```

---

## ☁️ Deployment

The initial deployment configuration is designed for DigitalOcean using Docker.

The production environment can be started with:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

---

## 🔄 Development Philosophy

IAJM is being developed incrementally.

The first version establishes the foundation of the platform rather than attempting to solve every possible requirement from the beginning.

```text
Real Requirements
       ↓
Initial Architecture
       ↓
Version 1
       ↓
Real-world Usage
       ↓
Feedback
       ↓
Improvements
       ↓
Future Versions
```

The system will evolve based on actual operational requirements and feedback.

---

## 🛣️ Future Development

Future versions may include:

* Enhanced dashboards and reporting
* Improved attendance management
* Additional financial tools
* Notifications
* Advanced permissions
* Improved mobile functionality
* Analytics and metrics
* Additional parish management features
* Automation of administrative tasks
* Improved monitoring and deployment
* Additional integrations

The roadmap is intentionally flexible and will evolve with the project.

---

## 📌 Current State

**IAJM Version 1** represents the initial foundation of a larger system.

It establishes:

* Core architecture
* Web application
* Mobile application
* Central API
* Database model
* Main business domains
* Initial security model
* Development infrastructure
* Production infrastructure

The project is still under active development.

Some workflows, interfaces, business rules and technical components may change as real-world usage provides additional requirements and feedback.

---

## 🤝 Contributions

At this stage, the project is primarily intended for internal development and parish use.

Any external contribution, reuse, modification or distribution requires prior authorization from the copyright holder.

---

## 📄 License

This project is **proprietary software**.

Copyright © 2026 Harold Torres Gallo. All rights reserved.

The source code may be publicly visible for reference and development purposes, but **no license is granted** to use, reproduce, modify, distribute, sublicense, publish, sell, or commercially exploit this software without prior written permission from the copyright holder.

Third-party dependencies and components remain subject to their respective licenses.

For permissions or licensing inquiries, please contact the copyright holder.

---

## ❤️ Project Vision

IAJM is more than a software project.

Its purpose is to provide technology that supports the organization and administration of missionary work with children, adolescents and young people within the parish community.

The long-term vision is to build a reliable, maintainable and scalable platform that simplifies administrative processes and allows coordinators and advisors to dedicate more time to their real mission.

> **Version 1 is only the beginning.**
