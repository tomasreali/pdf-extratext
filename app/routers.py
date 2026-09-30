from fastapi import APIRouter, UploadFile, File, HTTPException
import logging
from pydantic import BaseModel

from service.pdf_service import (
    procesar_archivo, listar_documentos, buscar_documento_por_id,
    modificar_nombre_documento, borrar_documento
)

router = APIRouter()
logger = logging.getLogger(__name__)

class NombreUpdate(BaseModel):
    nuevo_nombre: str

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/documents")
def get_all_documents():
    return {"documentos": listar_documentos()}

@router.get("/documents/{doc_id}")
def get_document_by_id(doc_id: str):
    doc = buscar_documento_por_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="No se encontró ningún documento con ese ID.")
    return doc

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    logger.info(f"Recibiendo archivo para procesar: {file.filename}")
    
    # Leemos los bytes del archivo
    contenido = await file.read()
    
    # ¡Magia! Delegamos TODO el trabajo a la capa de Service
    documento_procesado = procesar_archivo(
        contenido=contenido, 
        filename=file.filename, 
        content_type=file.content_type
    )
    
    # El router ahora es "tonto", solo devuelve la respuesta de éxito
    return {
        "id": documento_procesado.id, 
        "filename": documento_procesado.filename,
        "checksum": documento_procesado.checksum,
        "resumen": documento_procesado.resumen,
        "mensaje": "PDF subido, validado y resumido con IA exitosamente."
    }

@router.patch("/documents/{doc_id}")
def update_document_name(doc_id: str, datos: NombreUpdate):
    resultado = modificar_nombre_documento(doc_id, datos.nuevo_nombre)
    if not resultado or resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Documento no encontrado o ID inválido.")
    return {"mensaje": f"Nombre actualizado a {datos.nuevo_nombre}"}

@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    resultado = borrar_documento(doc_id)
    if not resultado or resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Documento no encontrado o ID inválido.")
    return {"mensaje": "Documento eliminado correctamente"}