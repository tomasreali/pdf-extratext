import hashlib

def generar_resumen_mock(texto: str) -> str:
    return "Este es un resumen simulado del texto. Acá en el futuro irá la respuesta de la IA (Ollama)."

def calcular_checksum(contenido: bytes) -> str:
    return hashlib.sha256(contenido).hexdigest()

def extraer_texto_mock() -> str:
    # Esta es la simulación de lo que extrae pdfplumber
    return "Texto de prueba extraído del PDF..."