from fastapi import FastAPI
# Importamos la configuración
from config import settings

# Le decimos a FastAPI que use el nombre de la app que está en el .env
app = FastAPI(title=settings.app_name)

@app.get("/health")
def health_check():
    return {
        "status": "ok", 
        "mensaje": "Servidor funcionando perfecto",
        # Mostramos el nombre para comprobación
        "app": settings.app_name
    }