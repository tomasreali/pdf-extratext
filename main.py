from fastapi import FastAPI, UploadFile, File, HTTPException
from config import settings
import pdfplumber # NUEVO: Importamos la librería

app = FastAPI(title=settings.app_name)

# NUEVO: Función para extraer texto
def extraer_texto_pdf(archivo) -> str:
    texto_completo = ""
    # Abrimos el archivo PDF directamente desde la memoria
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
    
    # NUEVO: Usamos nuestra función pasándole el archivo en memoria (file.file)
    texto_crudo = extraer_texto_pdf(file.file)
    
    # Devolvemos el texto extraído para comprobar que funciona
    return {
        "filename": file.filename, 
        "mensaje": "PDF recibido y procesado correctamente",
        "texto_extraido": texto_crudo
    }
