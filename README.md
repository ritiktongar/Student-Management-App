🎓 Student Management System — Full-Stack Flask + Nginx + Docker Application

A production-ready student lifecycle automation platform designed to streamline student registration, attendance tracking, and leave management.
This system is built with a strong focus on real-world DevOps workflows, containerization, API-driven architecture, and extensibility for enterprise use cases.

🚀 Key Highlights

🔐 JWT-enabled authentication (upcoming)

👨‍🏫 Admin-only student creation & secure operations

🧑‍🎓 Student self-service portal (attendance & leave submission)

🗂️ Centralized student database with validation

📅 Daily attendance tracking with duplication control

📝 Leave application workflow with statuses

📊 Smart analytics & statistics endpoints

🌐 Full REST API designed for frontend/mobile integration

🐳 Complete Dockerized architecture with Nginx, Flask & SQLite

🏗️ docker-compose orchestration for multi-container deployment

⚡ Real-time clock, alerts, and responsive UI

📦 Clean project structure with auto-initialized database

🛠️ Tech Stack

Backend: Flask (Python 3.11), SQLite

Frontend: HTML, CSS, Vanilla JavaScript

Web Server: Nginx

Containerization: Docker & Docker Compose

Architecture: RESTful service + reverse proxy + persistent database volume

📁 Core Modules
Module	Capabilities
Student Management	Register, list, delete students
Attendance	Daily attendance, duplication prevention, history view
Leave Management	Apply leave, track status, admin approval
Statistics	Per-student & global insights
API Layer	Fully documented JSON-based endpoints
🧱 Production-Ready Architecture
┌────────────────┐        ┌──────────────────────┐
│   Frontend     │        │      Backend API     │
│ (Nginx/HTML)   │◀──────▶│  Flask + SQLite DB   │
└────────────────┘        └──────────────────────┘
            ▲                     │
            │                     │ Persistent Volume
            └────────── Docker Compose ────────┘


Nginx serves the UI and proxies /api/* to Flask

Flask exposes a clean REST API

SQLite database persists inside a Docker volume

Containers orchestrated through docker-compose

Healthchecks ensure zero-downtime restarts
