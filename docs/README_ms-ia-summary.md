# ms-ia-summary

Microservicio de resumen de texto mediante Inteligencia Artificial (Ollama + LLaMA 3.2). Parte del ecosistema **pdf-extratext** (arquitectura de microservicios).

## Integrantes

Reali Tomás, Calvente Matías, Barros Nazareno, Parola Marcos, Rossi Emiliano, Del Pozo Mateo

---

## Arquitectura

```
ms-ia-summary/
├── app/                         ← Capa de Presentación (Endpoints)
│   ├── models/
│   │   └── summary_models.py    ← SummarizeRequest / SummarizeResponse
│   └── routers.py               ← Endpoints HTTP
├── service/                     ← Capa de Lógica de Negocio
│   └── summary_service.py      ← Generación de resúmenes con Ollama
├── config/                      ← Capa de Configuración
│   ├── logging_config.py        ← Logging JSON estructurado (stdout)
│   └── settings.py              ← Pydantic Settings (variables de entorno)
├── tests/                       ← Tests unitarios (pytest + mocks)
│   └── test_main.py
├── Dockerfile                   ← Python 3.12-slim + uv
├── docker-compose.yml           ← Incluye servicio Ollama con volumen persistente
├── pyproject.toml               ← Dependencias (uv)
├── main.py                      ← Punto de entrada FastAPI
└── .env.example                 ← Variables de entorno ejemplo
```

## Tecnologías

| Tecnología | Versión | Propósito |
|---|---|---|
| Python | 3.12 | Lenguaje base |
| FastAPI | ≥0.142 | Framework web asíncrono |
| Ollama (LLaMA 3.2) | latest | Motor de IA local para generación de resúmenes |
| Uvicorn | ≥0.54 | Servidor ASGI |
| Pydantic Settings | ≥2.15 | Configuración tipada vía variables de entorno |
| pytest + pytest-mock | ≥9.1 / ≥3.16 | Framework de testing con mocks |
| uv | latest | Gestor de paquetes y entornos virtuales |
| Docker | - | Contenerización |

## Endpoints

| Método | Ruta | Descripción | Input | Output |
|---|---|---|---|---|
| `GET` | `/health` | Health check con uptime y versión | - | `{"status": "ok", "service": "ms-ia-summary", "version": "1.0.0", "uptime_seconds": N, "timestamp": "..."}` |
| `POST` | `/summarize` | Genera resumen con IA del texto recibido | `application/json`: `{"text": "..."}` | `{"summary": "..."}` |

### Ejemplo de uso

```bash
# Health check
curl http://localhost:8002/health

# Solicitar resumen
curl -X POST http://localhost:8002/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "La inteligencia artificial es una rama de la informática que busca crear sistemas capaces de realizar tareas que normalmente requieren inteligencia humana."}'
```

## Variables de Entorno

| Variable | Descripción | Default |
|---|---|---|
| `APP_NAME` | Nombre del servicio (logs y health check) | `ms-ia-summary` |
| `OLLAMA_URL` | URL del servidor Ollama | `http://localhost:11434` |
| `OLLAMA_MODEL` | Modelo de IA a utilizar | `llama3.2` |

---

## Cómo Ejecutar

### Opción A: Desarrollo local (sin Docker)

**Requisitos:** Python 3.12, [uv](https://docs.astral.sh/uv/), [Ollama](https://ollama.ai/) instalado localmente

```bash
# 1. Clonar el repositorio
git clone https://github.com/tomasreali/ms-ia-summary.git
cd ms-ia-summary

# 2. Instalar dependencias
uv sync

# 3. Configurar variables de entorno
cp .env.example .env

# 4. Asegurarse de que Ollama esté corriendo y descargar el modelo
ollama run llama3.2
# Cuando aparezca el cursor >>> escribir /bye para salir

# 5. Iniciar el servidor
uv run uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

La API estará disponible en `http://localhost:8002/docs` (Swagger UI).

### Opción B: Con Docker (standalone)

```bash
# 1. Configurar variables de entorno
cp .env.example .env
# Editar OLLAMA_URL a: http://ollama:11434

# 2. Construir y levantar (incluye servicio Ollama)
docker compose up --build -d

# 3. Descargar el modelo de IA (primera vez solamente)
docker exec -it summary_ollama ollama run llama3.2
# Escribir /bye y Enter para salir

# 4. Verificar que está corriendo
curl http://localhost:8002/health
```

### Opción C: Ecosistema completo (recomendado)

Ver las instrucciones en el repositorio `pdf-extratext-infra` para levantar todo el ecosistema con Traefik + ms-pdf-extract + ms-ia-summary.

---

## Cómo Correr Tests

```bash
# Tests unitarios (no requieren Docker ni Ollama)
uv run pytest tests/ -v

# Output esperado:
# tests/test_main.py::test_health_check           PASSED
# tests/test_main.py::test_summarize_exitoso       PASSED
# tests/test_main.py::test_summarize_texto_vacio   PASSED
# tests/test_main.py::test_summarize_texto_corto   PASSED
```

Los tests usan `pytest-mock` para simular Ollama. No se necesita tener Ollama corriendo para ejecutarlos (principio F.I.R.S.T: Fast, Independent, Repeatable, Self-validating, Timely).

---

## Decisiones de Diseño

| Decisión | Justificación |
|---|---|
| **Ollama** como motor de IA | Permite correr LLMs localmente sin depender de APIs externas (OpenAI, etc.) |
| **LLaMA 3.2** como modelo | Buen balance entre calidad de resúmenes y consumo de recursos |
| **Volumen Docker persistente** | El modelo descargado (~2GB) se persiste entre reinicios del contenedor |
| **Logging JSON a stdout** | Twelve-Factor App Factor 11; logs parseables por herramientas de observabilidad |
| **Usuario no root en Docker** | Seguridad; el proceso corre como `appuser` |

## Comunicación Inter-servicios

Este microservicio es consumido por `ms-pdf-extract` a través de su endpoint `POST /summarize`. La comunicación se realiza internamente dentro de la red Docker. `ms-pdf-extract` implementa patrones de resiliencia (Circuit Breaker + Retry) para manejar indisponibilidad de este servicio.

```
ms-pdf-extract  ──HTTP POST──▶  ms-ia-summary  ──▶  Ollama (LLaMA 3.2)
     │                              │
     └── Circuit Breaker ◀──────────┘
         + Retry (3 intentos)
         + Degradación elegante
```
