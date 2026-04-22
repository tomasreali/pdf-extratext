from fastapi import FastAPI, UploadFile, File, HTTPException
from config.settings import settings
from config.database import collection
import pdfplumber

app = FastAPI(title=settings.app_name)

# Función para extraer texto del PDF
def extraer_texto_pdf(archivo) -> str:
    texto_completo = ""
    with pdfplumber.open(archivo) as pdf:
        for pagina in pdf.pages:
            texto_extraido = pagina.extract_text()
            if texto_extraido:
                texto_completo += texto_extraido + "\n"
    return texto_completo


@app.get("/health")
def health_check():
    return {
        "status": "ok", 
        "mensaje": "Servidor funcionando perfecto",
        "app": settings.app_name
    }


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    
    es_pdf = file.filename.endswith(".pdf")
    es_mime_pdf = file.content_type == "application/pdf"

    if not es_pdf and not es_mime_pdf:
        raise HTTPException(
            status_code=400, 
            detail="El archivo debe ser un documento PDF válido."
        )

    # 🔹 Extraer texto
    texto_crudo = extraer_texto_pdf(file.file)

    # 🔹 Crear documento para Mongo
    documento = {
        "filename": file.filename,
        "texto": texto_crudo
    }

    # 🔹 Guardar en MongoDB
    resultado = collection.insert_one(documento)

    # 🔹 Responder con ID
    return {
        "mensaje": "PDF procesado y guardado correctamente",
        "filename": file.filename,
        "id": str(resultado.inserted_id)
    }