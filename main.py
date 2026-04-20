from fastapi import FastAPI, UploadFile, File, HTTPException
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

#3. Agregamos el nuevo endpoint del paso 3
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    #Subtarea 3: Validamos extension y tipo de contenido
    es_pdf = file.filename.endswith(".pdf")
    es_mime_pdf = file.content_type == "application/pdf"

    if not es_pdf and not es_mime_pdf:
        # Subtarea 4: Error si no es PDF
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser un documento PDF valido"
        )
    return{
        "filename": file.filename,
        "content_type": file.content_type,
        "mensaje": "PDF recibido y validado correctamente"
    }