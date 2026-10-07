# ms-pdf-extract

Microservicio de extracción de texto de archivos PDF. Parte del ecosistema **pdf-extratext** (arquitectura de microservicios).

## Integrantes

Reali Tomás, Calvente Matías, Barros Nazareno, Parola Marcos, Rossi Emiliano, Del Pozo Mateo

---

## Arquitectura

```
ms-pdf-extract/
├── app/                         ← Capa de Presentación (Endpoints)
│   ├── models/
│   │   ├── extract_response.py
│   │   └── extract_and_summarize_response.py
│   └── routers.py               ← Endpoints + Backpressure (semáforo)
├── service/                     ← Capa de Lógica de Negocio
│   ├── extract_service.py       ← Extracción de texto con PyMuPDF
│   ├── circuit_breaker.py       ← Patrón Circuit Breaker
│   └── summary_client.py       ← Cliente HTTP a ms-ia-summary (Retry + CB)
├── config/                      ← Capa de Configuración
│   ├── logging_config.py        ← Logging JSON estructurado (stdout)
│   └── settings.py              ← Pydantic Settings (variables de entorno)
├── tests/                       ← Tests unitarios (pytest + mocks)
│   ├── test_main.py
│   ├── test_circuit_breaker.py
│   └── stress/                  ← Scripts de pruebas de carga
│       ├── pdfs/                ← PDFs de prueba (liviano → muy_pesado)
│       ├── spike_test.js        ← Script k6 (Spike Test - 100 VUs)
│       ├── vegeta_test.ps1      ← Script Vegeta (50 req/s fijas)
│       ├── benchmark_simple.ps1 ← Benchmark secuencial rápido
│       ├── run_benchmarks.ps1   ← Script maestro
│       └── RESULTADOS.md        ← Métricas obtenidas
├── Dockerfile                   ← Python 3.12-slim + uv + 4 workers Uvicorn
├── docker-compose.yml
├── pyproject.toml               ← Dependencias (uv)
├── main.py                      ← Punto de entrada FastAPI
└── .env.example                 ← Variables de entorno ejemplo
```

## Tecnologías

| Tecnología | Versión | Propósito |
|---|---|---|
| Python | 3.12 | Lenguaje base |
| FastAPI | ≥0.142 | Framework web asíncrono |
| PyMuPDF (fitz) | ≥1.28 | Extracción de texto de PDF (motor C, alta velocidad) |
| Uvicorn | ≥0.54 | Servidor ASGI con soporte multi-worker |
| httpx | ≥0.28 | Cliente HTTP async para comunicación inter-servicios |
| Pydantic Settings | ≥2.15 | Configuración tipada vía variables de entorno |
| pytest + pytest-mock | ≥9.1 / ≥3.16 | Framework de testing con mocks |
| uv | latest | Gestor de paquetes y entornos virtuales |
| Docker | - | Contenerización |

## Endpoints

| Método | Ruta | Descripción | Input | Output |
|---|---|---|---|---|
| `GET` | `/health` | Health check con uptime y versión | - | `{"status": "ok", "service": "...", "version": "1.0.0", "uptime_seconds": N, "timestamp": "..."}` |
| `POST` | `/extract` | Extrae texto de un PDF | `multipart/form-data` (campo `file`) | `{"content": "...", "page_count": N}` |
| `POST` | `/extract-and-summarize` | Extrae texto + solicita resumen a ms-ia-summary | `multipart/form-data` (campo `file`) | `{"content": "...", "page_count": N, "summary": "...", "summary_error": null}` |

## Variables de Entorno

| Variable | Descripción | Default |
|---|---|---|
| `APP_NAME` | Nombre del servicio (logs y health check) | `ms-pdf-extract` |
| `MAX_FILE_SIZE_MB` | Tamaño máximo de PDF aceptado | `10` |
| `SUMMARY_SERVICE_URL` | URL de ms-ia-summary para resúmenes | `http://ms-ia-summary:8000/summarize` |

---

## Cómo Ejecutar

### Opción A: Desarrollo local (sin Docker)

**Requisitos:** Python 3.12, [uv](https://docs.astral.sh/uv/)

```bash
# 1. Clonar el repositorio
git clone https://github.com/tomasreali/ms-pdf-extract.git
cd ms-pdf-extract

# 2. Instalar dependencias
uv sync

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env si es necesario

# 4. Iniciar el servidor
uv run uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

La API estará disponible en `http://localhost:8001/docs` (Swagger UI).

### Opción B: Con Docker (standalone)

```bash
# 1. Construir y levantar
docker compose up --build -d

# 2. Verificar que está corriendo
curl http://localhost:8001/health
```

### Opción C: Ecosistema completo (recomendado)

Ver las instrucciones en el repositorio [`pdf-extratext-infra`](#ecosistema-completo) para levantar todo con Traefik + ms-ia-summary + ms-pdf-extract (5 réplicas).

---

## Cómo Correr Tests

```bash
# Tests unitarios (no requieren Docker ni servicios externos)
uv run pytest tests/ -v

# Output esperado:
# tests/test_main.py::test_health_check                            PASSED
# tests/test_main.py::test_extract_pdf_exitoso                     PASSED
# tests/test_main.py::test_extract_archivo_no_pdf                  PASSED
# tests/test_main.py::test_extract_archivo_muy_grande              PASSED
# tests/test_main.py::test_extract_and_summarize_exitoso           PASSED
# tests/test_main.py::test_extract_and_summarize_ia_caida          PASSED
# tests/test_main.py::test_extract_and_summarize_archivo_no_pdf    PASSED
# tests/test_main.py::test_extract_and_summarize_archivo_muy_grande PASSED
# tests/test_circuit_breaker.py::TestCircuitBreaker::test_estado_inicial_cerrado          PASSED
# tests/test_circuit_breaker.py::TestCircuitBreaker::test_se_abre_tras_umbral_de_fallas   PASSED
# tests/test_circuit_breaker.py::TestCircuitBreaker::test_no_se_abre_con_menos_fallas     PASSED
# tests/test_circuit_breaker.py::TestCircuitBreaker::test_exito_resetea_contador_fallas    PASSED
# tests/test_circuit_breaker.py::TestCircuitBreaker::test_transicion_open_a_half_open      PASSED
# tests/test_circuit_breaker.py::TestCircuitBreaker::test_half_open_exito_cierra_circuito  PASSED
# tests/test_circuit_breaker.py::TestCircuitBreaker::test_half_open_falla_abre_circuito    PASSED
# tests/test_circuit_breaker.py::TestCircuitBreaker::test_reset_vuelve_a_estado_inicial    PASSED
```

Los tests usan `pytest-mock` para simular las dependencias externas (principio F.I.R.S.T).

---

## Cómo Correr Benchmarks (Pruebas de Carga)

### Prerequisitos

- El servicio debe estar corriendo (idealmente con las 5 réplicas via `pdf-extratext-infra`)
- Los scripts están en `tests/stress/`

### Benchmark Simple (PowerShell - no requiere herramientas externas)

```powershell
# PDF liviano
.\tests\stress\benchmark_simple.ps1 -TotalRequests 50 -PdfPath "tests\stress\pdfs\liviano.pdf"

# PDF pesado (5MB)
.\tests\stress\benchmark_simple.ps1 -TotalRequests 50 -PdfPath "tests\stress\pdfs\pesado.pdf"
```

### Spike Test con k6

```bash
# Instalar k6: https://k6.io/docs/getting-started/installation/
k6 run tests/stress/spike_test.js
```

Perfil: subida a 100 VUs en 10s → 20s sostenidos → rampa descendente 10s.

### Carga Fija con Vegeta

```powershell
.\tests\stress\vegeta_test.ps1
```

Perfil: 50 req/s constantes durante 30 segundos.

### Resultados Obtenidos

Ver [`tests/stress/RESULTADOS.md`](tests/stress/RESULTADOS.md) para las métricas completas y comparativa contra el benchmark del profesor.

---

## Decisiones de Diseño Clave

| Decisión | Justificación |
|---|---|
| **PyMuPDF** en lugar de pdfplumber | Motor C nativo, ~10x más rápido para extracción de texto |
| **4 workers Uvicorn** por réplica | Paralelismo real (supera limitación del GIL de Python) |
| **`run_in_executor()`** | Ejecuta tareas CPU-bound en thread pool sin bloquear el event loop |
| **Semáforo de backpressure (10 concurrentes)** | Previene saturación de RAM; rechaza con 503 en lugar de acumular |
| **Circuit Breaker + Retry** | Resiliencia ante caídas de ms-ia-summary con degradación elegante |
| **Logging JSON a stdout** | Twelve-Factor App Factor 11; parseable por herramientas de observabilidad |
| **Usuario no root en Docker** | Seguridad; el proceso corre como `appuser` |

---

## Patrones Aplicados

- **Circuit Breaker** — Protege contra fallas en cascada con ms-ia-summary
- **Retry + Backoff Exponencial** — 3 reintentos (0s, 1s, 2s) antes de activar el circuit breaker
- **Chain** — POST /extract-and-summarize encadena extracción + resumen
- **Degradación Elegante** — Si la IA falla, devuelve texto sin resumen
- **Database per Service** — Cada microservicio es independiente y stateless
