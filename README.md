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
* Development and production Docker configurations

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
| Language                | Python 3.11+   |
| ORM                     | SQLAlchemy 2.0 |
| Migrations              | Alembic        |
| Validation              | Pydantic v2    |
| Database                | PostgreSQL 16  |
| Web                     | Next.js 15     |
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

## 👥 Groups

The first version defines five predefined groups.

Groups are currently fixed and cannot be created or deleted through the application.

| Group                 | Category    | Age Range |
| --------------------- | ----------- | --------: |
| Trigo Verde           | Childhood   |       4–6 |
| Trigo Maduro          | Childhood   |       7–9 |
| Trigo Maduro Avanzado | Childhood   |     10–12 |
| Adolescencia          | Adolescence |     13–15 |
| Juventud              | Youth       |     16–24 |

The system also supports automatic group reassignment based on member age.

---

## 🧩 Main Domains

The backend is organized around business domains.

| Domain       | Description                                       |
| ------------ | ------------------------------------------------- |
| `usuarios`   | Authentication, users, roles and account security |
| `grupos`     | Management of the predefined missionary groups    |
| `miembros`   | Children, adolescents and young members           |
| `asesores`   | Advisors and their roles and monthly quotas       |
| `encuentros` | Weekly meetings, attendance and metrics           |
| `tesoreria`  | Fundraising activities, donations and income      |
| `gastos`     | Expense categories and expense records            |
| `tienda`     | Product sales and sale details                    |
| `inventario` | Inventory items, status and origin                |
| `parroquial` | Parish activities and related deliveries          |

---

## 🔐 Authentication and Security

The initial version includes authentication and role-based access control.

The system includes:

* JWT authentication
* User roles
* Failed-login attempt tracking
* Account lockout
* Protected API endpoints

Security-related configuration should be handled through environment variables.

Sensitive credentials must never be committed to the repository.

---

## 📁 Project Structure

```text
iajm/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config/
│   │   │   ├── database/
│   │   │   ├── security/
│   │   │   └── dependencies/
│   │   ├── domains/
│   │   │   ├── usuarios/
│   │   │   ├── grupos/
│   │   │   ├── miembros/
│   │   │   ├── asesores/
│   │   │   ├── encuentros/
│   │   │   └── ...
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
│       ├── core/
│       └── features/
│
├── docker/
│   ├── backend.Dockerfile
│   └── nginx/
│       └── nginx.conf
│
├── docker-compose.yml
├── docker-compose.prod.yml
├── AGENTS.md
├── SRS.md
└── README.md
```

---

## 🐳 Infrastructure

The project includes Docker configurations for both development and production environments.

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
* Supporting services required by the project

---

## 💻 Local Development

### Requirements

* Docker Desktop
* Python 3.11+
* Poetry
* Node.js 20+
* Flutter 3.41+

### Backend

```bash
cd backend

poetry install

poetry run alembic upgrade head

poetry run python scripts/seed.py

poetry run uvicorn app.main:app --reload --port 8000
```

API documentation:

```text
http://localhost:8000/api/docs
```

### Web Application

```bash
cd frontend

npm install

npm run dev
```

Web application:

```text
http://localhost:3000
```

### Mobile Application

```bash
cd mobile

flutter pub get

flutter run
```

Configure the backend URL in:

```text
mobile/lib/core/network/api_client.dart
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

The project uses **PostgreSQL 16** as its primary relational database.

Database schema changes are managed using **Alembic migrations**.

To apply migrations:

```bash
poetry run alembic upgrade head
```

The project also provides a seed script for initializing development data:

```bash
poetry run python scripts/seed.py
```

---

## ☁️ Deployment

The initial deployment configuration is designed for **DigitalOcean** using Docker.

A production environment can be deployed using:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

The production configuration supports:

* Docker-based deployment
* PostgreSQL
* Nginx
* Domain configuration
* HTTPS / Let's Encrypt
* Database migrations
* Database backups

---

## 🔄 Development Philosophy

IAJM is being developed incrementally.

The first version establishes the foundation of the platform rather than attempting to solve every possible requirement from the beginning.

The development approach is:

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

This allows the system to evolve based on actual operational needs rather than trying to define the entire platform upfront.

---

## 🛣️ Future Development

Future versions may include improvements and new functionality in areas such as:

* Enhanced dashboards and reporting
* Improved attendance and meeting management
* More financial tools
* Notifications
* Advanced permissions
* Improved mobile functionality
* Better analytics and metrics
* Additional parish management features
* Automation of repetitive administrative tasks
* Improved deployment and monitoring
* Additional integrations

The roadmap is intentionally flexible and will evolve with the project.

---

## 📌 Current State

**IAJM Version 1** should be understood as the **initial foundation of a larger system**.

It already establishes:

* The core architecture
* The main applications
* The central API
* The database model
* The main business domains
* The initial security model
* Development infrastructure
* Production infrastructure

However, the project is still under active development.

Some workflows, interfaces, business rules and technical components may change as real-world usage provides additional requirements and feedback.

---

## 🤝 Contributing

This project is currently intended primarily for internal development and parish use.

As the project evolves, contribution guidelines may be introduced for external collaborators.

---

## 📄 License

**Internal Use — IAJM Parish Project**

All rights reserved.

---

## ❤️ Project Vision

IAJM is more than a software project.

Its purpose is to provide technology that supports the organization and administration of missionary work with children, adolescents and young people within the parish community.

The long-term vision is to build a reliable, maintainable and scalable platform that simplifies administrative processes and allows coordinators and advisors to dedicate more time to their real mission.

> **Version 1 is only the beginning.**
