# pdf-extratext

Extrae texto de un PDF proporcionado por el usuario y genera un resumen usando IA.

## Tecnología
- Python 3.12
- uv (manejo de dependencias)
- FastAPI (framework web)
- OLLAMA con llama3.2 (modelo de IA local)
- MongoDB (base de datos no relacional)

## Metodologías
- TDD
- 12 Factor App (primeros 6 principios)

## Principios de programación
- KISS, DRY, YAGNI, SOLID

## Estructura
- `app/` → Endpoints y modelos
- `service/` → Lógica de negocio
- `repository/` → Acceso a datos
- `config/` → Configuraciones