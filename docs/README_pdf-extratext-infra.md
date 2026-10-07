# pdf-extratext-infra

Infraestructura del ecosistema **pdf-extratext**: Traefik como API Gateway + docker-compose maestro que orquesta todos los microservicios con un solo comando.

## Integrantes

Reali Tomás, Calvente Matías, Barros Nazareno, Parola Marcos, Rossi Emiliano, Del Pozo Mateo

---

## Arquitectura del Ecosistema

```
                         ┌────────────────────────────────┐
                         │        CLIENTE (Usuario)        │
                         │     curl / Frontend / k6        │
                         └──────────────┬─────────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │     🔀  TRAEFIK GATEWAY       │
                         │      Reverse Proxy +          │
                         │    Load Balancer (Round Robin) │
                         │    Puerto 80 (proxy)           │
                         │    Puerto 8080 (dashboard)     │
                         └─────────┬────────┬────────────┘
                                   │        │
                    ┌──────────────┘        └──────────────┐
                    │  /extract                            │  /summarize
                    │  /extract-and-summarize               │
                    ▼                                      ▼
    ┌───────────────────────────────┐     ┌──────────────────────────────┐
    │   ms-pdf-extract              │     │       ms-ia-summary          │
    │   × 5 réplicas                │     │       × 1 instancia          │
    │                               │     │                              │
    │   FastAPI + PyMuPDF           │────▶│   FastAPI + Ollama           │
    │   4 Workers Uvicorn/réplica   │HTTP │   (LLaMA 3.2)               │
    │   1.0 CPU, 512M RAM/réplica   │     │                              │
    └───────────────────────────────┘     └──────────┬───────────────────┘
                                                     │
                                                     ▼
                                          ┌──────────────────────────────┐
                                          │        OLLAMA SERVER         │
                                          │     Puerto 11434             │
                                          │     Volumen persistente      │
                                          └──────────────────────────────┘
```

## Repositorios del Proyecto

| Repositorio | Descripción | URL |
|---|---|---|
| **ms-pdf-extract** | Microservicio de extracción de texto de PDF | [GitHub](https://github.com/tomasreali/ms-pdf-extract) |
| **ms-ia-summary** | Microservicio de resumen con IA (Ollama) | [GitHub](https://github.com/tomasreali/ms-ia-summary) |
| **pdf-extratext-infra** | Infraestructura (este repositorio) | Este repo |

---

## Cómo Levantar Todo el Ecosistema

### Requisitos Previos

1. Tener instalado **[Docker Desktop](https://www.docker.com/products/docker-desktop/)**
   - *Windows:* Asegurarse de tener habilitada la Virtualización en la BIOS y WSL2 activado
2. Tener instalado **Git**
3. Tener al menos **4 GB de RAM** disponible para Docker

### Paso 1: Clonar los repositorios

```bash
# Crear carpeta del proyecto
mkdir pdf-extratext-proyecto && cd pdf-extratext-proyecto

# Clonar los 3 repositorios
git clone https://github.com/tomasreali/ms-pdf-extract.git
git clone https://github.com/tomasreali/ms-ia-summary.git
git clone https://github.com/tomasreali/pdf-extratext-infra.git
```

### Paso 2: Configurar variables de entorno

```bash
# ms-pdf-extract
cp ms-pdf-extract/.env.example ms-pdf-extract/.env

# ms-ia-summary
cp ms-ia-summary/.env.example ms-ia-summary/.env
```

Las variables de entorno por defecto funcionan correctamente dentro de Docker. Solo modificar si se necesita personalizar algo.

### Paso 3: Levantar todo con un solo comando

```bash
cd pdf-extratext-infra
docker compose up --build -d
```

Este comando:
- Construye las imágenes de `ms-pdf-extract` y `ms-ia-summary`
- Levanta **Traefik** como API Gateway en el puerto 80
- Despliega **5 réplicas** de `ms-pdf-extract` (con límites de 1.0 CPU y 512M RAM cada una)
- Despliega **1 instancia** de `ms-ia-summary`
- Levanta **Ollama** con volumen persistente para el modelo de IA
- Crea la red Docker compartida entre todos los servicios

### Paso 4: Descargar el modelo de IA (solo la primera vez)

```bash
# Descargar LLaMA 3.2 (~2GB, tarda unos minutos)
docker exec -it summary_ollama ollama run llama3.2
# Cuando aparezca el cursor >>> escribir /bye y Enter para salir
```

### Paso 5: Verificar que todo funciona

```bash
# Health check de ms-pdf-extract (a través de Traefik)
curl http://localhost/health

# Health check de ms-ia-summary
curl http://localhost/summarize-health

# Extraer texto de un PDF
curl -X POST http://localhost/extract \
  -F "file=@path/a/tu/archivo.pdf"

# Extraer texto + resumen con IA
curl -X POST http://localhost/extract-and-summarize \
  -F "file=@path/a/tu/archivo.pdf"
```

### Dashboard de Traefik

Abrir en el navegador: **http://localhost:8080**

El dashboard muestra:
- Estado de todos los servicios registrados
- Rutas activas y sus backends
- Réplicas saludables de `ms-pdf-extract`

---

## Cómo Apagar el Ecosistema

```bash
# Apagar todos los servicios
docker compose down

# Apagar y eliminar volúmenes (perderá el modelo de IA descargado)
docker compose down -v
```

---

## Cómo Correr las Pruebas de Carga

### Prerequisitos

El ecosistema debe estar corriendo (`docker compose up --build -d`).

### Benchmark Simple (sin herramientas externas)

```powershell
cd ms-pdf-extract

# PDF liviano
powershell -File tests\stress\benchmark_simple.ps1 -TotalRequests 50

# PDF pesado (5MB)
powershell -File tests\stress\benchmark_simple.ps1 -TotalRequests 50 -PdfPath "tests\stress\pdfs\pesado.pdf"
```

### Spike Test con Grafana k6

```bash
# Instalar k6: https://k6.io/docs/getting-started/installation/
cd ms-pdf-extract
k6 run tests/stress/spike_test.js
```

**Perfil:** 100 VUs en 10s → 20s sostenidos → rampa descendente 10s.

### Carga Fija con Vegeta

```powershell
cd ms-pdf-extract
powershell -File tests\stress\vegeta_test.ps1
```

**Perfil:** 50 req/s constantes durante 30 segundos.

### Resultados

Ver [`ms-pdf-extract/tests/stress/RESULTADOS.md`](../ms-pdf-extract/tests/stress/RESULTADOS.md) para las métricas completas.

---

## Configuración de Recursos

### Límites por réplica de ms-pdf-extract

```yaml
deploy:
  replicas: 5
  resources:
    limits:
      cpus: "1.0"
      memory: 512M
```

| Parámetro | Valor | Total (5 réplicas) |
|---|---|---|
| CPU por réplica | 1.0 core | 5.0 cores |
| RAM por réplica | 512 MB | 2.5 GB |
| Workers Uvicorn/réplica | 4 | 20 workers |

---

## Troubleshooting

| Problema | Solución |
|---|---|
| `Error: port 80 is already in use` | Detener otros servicios que usen el puerto 80 (Apache, Nginx, etc.) |
| `Error: port 8080 is already in use` | Cambiar el puerto del dashboard de Traefik en el docker-compose |
| Ollama tarda mucho en descargar el modelo | Es normal la primera vez (~2GB). El volumen persistente evita descargar de nuevo |
| `503 Service Unavailable` en /extract | El servicio está saturado (backpressure activado). Esperar unos segundos y reintentar |
| El resumen devuelve `summary: null` | ms-ia-summary podría no estar disponible. Verificar con `docker compose logs ms-ia-summary` |
| `Cannot connect to Docker daemon` | Asegurarse de que Docker Desktop esté abierto y corriendo |
