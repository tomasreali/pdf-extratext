from pydantic import BaseModel
from typing import Optional

class Documento(BaseModel):
    # El id es opcional porque al crear un documento nuevo todavía no tiene ID de Mongo
    id: Optional[str] = None 
    filename: str
    text: str
    resumen: str
    checksum: str