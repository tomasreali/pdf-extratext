import hashlib
import os
import pdfplumber # <-- Importante
import io         # <-- Importante
from ollama import Client

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
cliente_ia = Client(host=OLLAMA_URL)

def calcular_checksum(contenido: bytes) -> str:
    return hashlib.sha256(contenido).hexdigest()

# --- ESTA ES LA FUNCIÓN NUEVA Y REAL ---
def extraer_texto_real(contenido_pdf: bytes) -> str:
    texto_completo = ""
    # Abrimos los bytes del PDF en memoria
    with pdfplumber.open(io.BytesIO(contenido_pdf)) as pdf:
        for pagina in pdf.pages:
            texto_extraido = pagina.extract_text()
            if texto_extraido:
                texto_completo += texto_extraido + "\n"
    return texto_completo

def generar_resumen_ia(texto: str) -> str:
    # Si el texto es muy corto o está vacío, le avisamos para que no falle
    if not texto or len(texto.strip()) < 10:
        return "El documento parece estar vacío o no contiene texto extraíble."

    prompt = f"Haz un resumen claro, conciso y en español del siguiente texto:\n\n{texto}"
    try:
        respuesta = cliente_ia.generate(model='llama3.2', prompt=prompt)
        return respuesta['response']
    except Exception as e:
        return f"Error con la IA: {str(e)}"