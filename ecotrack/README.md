# 🌱 EcoTrack Pro — SaaS de Sostenibilidad Empresarial

Plataforma web para medir, visualizar y reducir la huella de carbono empresarial.

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Frontend | HTML5, CSS3, JavaScript ES6+, Chart.js |
| Backend | Python 3.12 + FastAPI |
| Base de datos | MySQL 8 |
| Auth | JWT + bcrypt |
| IA | OpenAI GPT-3.5 |
| Despliegue | Docker Compose (app + DB + nginx) |
| Estilo código | PEP8 (flake8) |
| Documentación | Swagger + Redoc (automático con FastAPI) |

---

## 🚀 Inicio rápido

### Con Docker (recomendado)

```bash
# 1. Clonar / entrar al proyecto
cd ecotrack

# 2. (Opcional) Configurar OpenAI
cp backend/.env.example backend/.env
# Editar backend/.env y añadir tu OPENAI_API_KEY

# 3. Levantar todo
docker compose up --build

# 4. Abrir en el navegador
# Frontend: http://localhost:3000
# API docs Swagger: http://localhost:8000/docs
# API docs Redoc: http://localhost:8000/redoc
```

### Sin Docker (desarrollo local)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Crear base de datos MySQL primero, luego:
cp .env.example .env
# Editar .env con tus credenciales

uvicorn app.main:app --reload --port 8000

# Frontend (en otra terminal)
# Abrir frontend/index.html en el navegador
# O usar un servidor simple:
cd frontend
python -m http.server 3000
```

---

## 📁 Estructura del proyecto

```
ecotrack/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app principal
│   │   ├── config.py        # Configuración (env vars)
│   │   ├── database.py      # SQLAlchemy + MySQL
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── models/
│   │   │   └── models.py    # User, Consumption, AIPlan
│   │   ├── routes/
│   │   │   ├── auth.py      # Login, Register, Me
│   │   │   ├── consumptions.py  # CRUD consumos + IA
│   │   │   └── dashboard.py     # Estadísticas
│   │   └── services/
│   │       ├── auth.py      # JWT + bcrypt
│   │       ├── carbon.py    # Cálculo huella CO₂
│   │       └── ai_service.py # OpenAI integration
│   ├── requirements.txt
│   ├── setup.cfg            # PEP8 / flake8
│   └── Dockerfile
├── frontend/
│   ├── index.html           # Login / Registro
│   ├── css/styles.css       # Estilos globales
│   ├── js/api.js            # Llamadas API + auth
│   └── pages/
│       ├── dashboard.html       # Gráficos Chart.js
│       ├── consumptions.html    # Lista CRUD
│       ├── register-consumption.html  # Formulario
│       └── ai-plan.html         # Plan IA
├── docker-compose.yml
├── nginx.conf
└── README.md
```

---

## 📋 Endpoints API

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/register` | Registrar usuario | ❌ |
| POST | `/api/auth/login` | Login → JWT | ❌ |
| GET | `/api/auth/me` | Perfil propio | ✅ |
| GET | `/api/dashboard` | Estadísticas globales | ✅ |
| GET | `/api/consumptions` | Listar consumos | ✅ |
| POST | `/api/consumptions` | Crear consumo | ✅ |
| PATCH | `/api/consumptions/{id}` | Editar consumo | ✅ |
| DELETE | `/api/consumptions/{id}` | Borrar consumo | ✅ |
| POST | `/api/consumptions/{id}/ai-plan` | Generar plan IA | ✅ |
| GET | `/api/consumptions/breakdown/{id}` | Desglose CO₂ | ✅ |

---

## 🔐 Seguridad

- **JWT** — Tokens firmados con HS256, expiran en 8 horas
- **bcrypt** — Las contraseñas se cifran con bcrypt antes de guardarse en MySQL. Nunca se almacena el texto plano
- **CORS** — Configurado para permitir solo orígenes autorizados

## 🤖 IA

Si tienes clave de OpenAI: añádela en `OPENAI_API_KEY` y el sistema usará GPT-3.5 para generar planes personalizados.

Sin clave: el sistema genera automáticamente planes detallados basados en reglas (sin coste).

## 📊 Cálculo de huella de carbono

| Fuente | Factor | Unidad |
|--------|--------|--------|
| Electricidad | 0.233 kg CO₂ | por kWh |
| Gas natural | 0.202 kg CO₂ | por kWh |
| Agua | 0.000298 kg CO₂ | por litro |
| Transporte | 0.171 kg CO₂ | por km |

Fuente: IPCC / IDAE España

## 🌿 Control de versiones (GitHub)

Estructura de ramas recomendada:
- `main` — código estable, listo para producción
- `develop` — rama de desarrollo activo
- `feature/nombre` — para nuevas funcionalidades
