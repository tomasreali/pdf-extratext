from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import router
import logging

# 2. Configuramos el formato profesional de los logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 3. Instanciamos el logger para este archivo
logger = logging.getLogger(__name__)

app = FastAPI(title="PDF Extractor API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción se restringe, pero para la demo está perfecto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enganchamos todas las rutas que mudamos a la otra carpeta
app.include_router(router)

# 4. Un log de prueba para cuando levante el servidor
logger.info("Servidor FastAPI iniciado y configurado correctamente.")