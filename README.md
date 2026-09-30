# 📄 PDF ExtraText — Analizador de PDF con IA

API REST desarrollada con **FastAPI** que extrae texto de documentos PDF y genera resúmenes automáticos usando inteligencia artificial (Ollama + LLaMA 3.2), con persistencia en **MongoDB**.

## Integrantes

Reali Tomás, Calvente Matías, Barros Nazareno, Parola Marcos, Rossi Emiliano, Del Pozo Mateo

## 📁 Arquitectura del Proyecto (3 Capas)

```
pdf-extratext/
├── app/                          # Capa de PRESENTACIÓN
│   ├── routers.py                # Endpoints HTTP (Router "delgado")
│   └── models/
│       └── documento.py          # Entidad de dominio (Pydantic)
├── service/                      # Capa de NEGOCIO (Lógica)
│   └── pdf_service.py            # Orquestación, validaciones, IA
├── repository/                   # Capa de DATOS
│   └── db_repo.py                # Operaciones CRUD contra MongoDB
├── config/                       # Configuración
│   ├── settings.py               # Variables de entorno (Pydantic Settings)
│   └── database.py               # Conexión a MongoDB
├── tests/                        # Tests automatizados
│   ├── test_main.py              # Suite de tests con mocks (F.I.R.S.T)
│   └── dummy.pdf                 # PDF de prueba real
├── main.py                       # Punto de entrada de la aplicación
├── Dockerfile                    # Imagen Docker de la API
├── docker-compose.yml            # Orquestación: API + Ollama
├── docker-compose.db.yml         # Base de datos MongoDB (aislada)
├── pyproject.toml                # Dependencias y config de herramientas
└── .env                          # Variables de entorno (NO versionado)
```

## Metodologías

- TDD
- 12 Factor App (primeros 6 principios)

## Principios de programación

- KISS, DRY, YAGNI, SOLID

## 🚀 Instalación y Configuración

### Requisitos previos

1. Python 3.12+
2. [uv](https://docs.astral.sh/uv/) (gestor de paquetes y entornos virtuales)
3. [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y corriendo
   - *Nota para usuarios de Windows: Asegurarse de tener habilitada la Virtualización en la BIOS y el motor WSL2 activado.*
4. **Git**

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/tomasreali/pdf-extratext.git
cd pdf-extratext
```

### Paso 2: Instalar dependencias

```bash
uv sync
```

### Paso 3: Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto con la siguiente configuración:

**Para desarrollo local (sin Docker para la API):**
```env
APP_NAME="Extraccion PDF API"
MONGO_URL=mongodb://localhost:27017
OLLAMA_URL=http://localhost:11434
DB_NAME="pdf_db"
```

**Para ejecución 100% en Docker:**
```env
APP_NAME="Extraccion PDF API"
MONGO_URL=mongodb://mongodb:27017
OLLAMA_URL=http://ollama:11434
DB_NAME="pdf_db"
```

### Paso 4: Levantar la infraestructura

Asegurarse de tener Docker Desktop abierto y ejecutándose de fondo. Luego, en la terminal del proyecto:

```bash
# Levantar la Base de Datos primero (crea la red interna)
docker compose -f docker-compose.db.yml up -d

# Levantar la IA
docker compose up -d ollama
```

### Paso 5: Descargar el modelo de Inteligencia Artificial

Se necesita descargar el modelo de lenguaje LLaMA 3.2 (solo la primera vez):

```bash
docker exec -it pdf_ollama ollama run llama3.2
```

Cuando aparezca el cursor `>>>` indicando que el chat inició, escribir `/bye` y presionar Enter para salir.

### Paso 6: Ejecutar la API en desarrollo

```bash
uv run uvicorn main:app --reload
```

La API estará disponible en `http://localhost:8000`.
La documentación interactiva (Swagger) estará en `http://localhost:8000/docs`.

### Ejecución completa con Docker (alternativa)

Si se prefiere ejecutar todo dentro de Docker (incluida la API):

```bash
docker compose -f docker-compose.db.yml up -d
docker compose up --build -d
```

### Frontend

Abrir el repositorio del frontend en VS Code y ejecutarlo con Live Server (Puerto 5500).

### Apagar el proyecto

Para apagar todos los servicios cuando se termine de usar:

```bash
docker compose down
docker compose -f docker-compose.db.yml down
```

## 🧪 Tests

La suite de tests usa **mocks** (pytest-mock) para simular MongoDB y Ollama, por lo que **no es necesario tener Docker corriendo** para ejecutar los tests.

```bash
uv run pytest tests/test_main.py -v
```

## 📡 Endpoints Disponibles

| Método   | Ruta                | Descripción                                          |
|----------|---------------------|------------------------------------------------------|
| `GET`    | `/health`           | Health check del servidor                            |
| `POST`   | `/upload`           | Subir un PDF, extraer texto y generar resumen con IA |
| `GET`    | `/documents`        | Listar todos los documentos procesados               |
| `GET`    | `/documents/{id}`   | Obtener un documento por su ID                       |
| `PATCH`  | `/documents/{id}`   | Modificar el nombre de un documento                  |
| `DELETE` | `/documents/{id}`   | Eliminar un documento                                |

## 🛠️ Tecnologías Utilizadas

- **Python 3.12** — Lenguaje de programación
- **FastAPI** — Framework web async
- **Pydantic** — Validación y serialización de datos
- **pdfplumber** — Extracción de texto de PDFs
- **Ollama (LLaMA 3.2)** — Generación de resúmenes con IA local
- **MongoDB + PyMongo** — Base de datos NoSQL
- **Docker / Docker Compose** — Contenerización
- **Pytest + pytest-mock** — Testing con principios F.I.R.S.T
- **uv** — Gestión de dependencias y entornos virtuales
