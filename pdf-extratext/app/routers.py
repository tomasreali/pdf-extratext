from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from repository.db_repo import (
    obtener_todos, obtener_por_id, obtener_por_checksum,
    guardar_documento, actualizar_nombre, eliminar_documento
)
# MODIFICADO: Importamos la función de IA y la de extracción REAL
from service.pdf_service import generar_resumen_ia, calcular_checksum, extraer_texto_real

# Creamos el enrutador
router = APIRouter()

class NombreUpdate(BaseModel):
    nuevo_nombre: str

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/documents")
def get_all_documents():
    return {"documentos": obtener_todos()}

@router.get("/documents/{doc_id}")
def get_document_by_id(doc_id: str):
    doc = obtener_por_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="No se encontró ningún documento con ese ID.")
    doc["_id"] = str(doc["_id"])
    return doc

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # 1. Validación de extensión
    es_pdf = file.filename.endswith(".pdf")
    es_mime_pdf = file.content_type == "application/pdf"
    if not es_pdf and not es_mime_pdf:
        raise HTTPException(status_code=400, detail="El archivo debe ser un documento PDF válido.")
    
    # 2. Lectura y validación de tamaño
    contenido = await file.read()
    TAMANO_MAXIMO_BYTES = 5 * 1024 * 1024
    if len(contenido) > TAMANO_MAXIMO_BYTES:
        raise HTTPException(status_code=400, detail="El archivo es demasiado grande. El máximo permitido es 5MB.")

    # 3. Verificación de duplicados (Checksum)
    checksum_calculado = calcular_checksum(contenido)
    if obtener_por_checksum(checksum_calculado):
        raise HTTPException(status_code=409, detail="Este documento ya fue subido y procesado previamente.")
    
    # 4. Extracción de texto (¡AHORA ES REAL!)
    # Le pasamos la variable "contenido" que tiene los bytes del archivo
    texto_extraido = extraer_texto_real(contenido) 
    
    # 5. Generación de resumen con la IA
    resumen_generado = generar_resumen_ia(texto_extraido)
    
    # 6. Persistencia en BD
    nuevo_documento = {
        "filename": file.filename,
        "content_type": file.content_type,
        "text": texto_extraido,
        "resumen": resumen_generado,
        "checksum": checksum_calculado
    }
    
    resultado = guardar_documento(nuevo_documento)
    
    return {
        "id": str(resultado.inserted_id), 
        "filename": file.filename,
        "checksum": checksum_calculado,
        "resumen": resumen_generado,
        "mensaje": "PDF subido, validado y resumido con IA exitosamente."
    }

@router.patch("/documents/{doc_id}")
def update_document_name(doc_id: str, datos: NombreUpdate):
    resultado = actualizar_nombre(doc_id, datos.nuevo_nombre)
    if not resultado or resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Documento no encontrado o ID inválido.")
    return {"mensaje": f"Nombre actualizado a {datos.nuevo_nombre}"}

@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    resultado = eliminar_documento(doc_id)
    if not resultado or resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Documento no encontrado o ID inválido.")
    return {"mensaje": "Documento eliminado correctamente"}