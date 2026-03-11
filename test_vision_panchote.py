import os
import vertexai
from vertexai.generative_models import GenerativeModel, Image
from google.cloud import firestore
from datetime import datetime

# ==========================================================
# 🔑 CONFIGURACIÓN DE IDENTIDAD
# ==========================================================
NOMBRE_DE_TU_JSON = "firebase_key.json" 
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = NOMBRE_DE_TU_JSON

PROJECT_ID = "multiagentes-479321"
LOCATION = "us-central1" 
vertexai.init(project=PROJECT_ID, location=LOCATION)

db = firestore.Client()
model = GenerativeModel("gemini-2.0-flash-001") 

def guardar_en_historial(user_id, plato, consejo):
    """Guarda el análisis en una nueva colección para historial"""
    try:
        log_ref = db.collection("daily_logs").document() # ID automático
        log_ref.set({
            "user_id": user_id,
            "fecha": datetime.now(),
            "comida_detectada": plato,
            "consejo_panchote": consejo,
            "tipo": "analisis_visual"
        })
        print("✅ Historial guardado en Firestore (colección: daily_logs)")
    except Exception as e:
        print(f"⚠️ No se pudo guardar el historial: {e}")

def panchote_vidente(image_path, user_id="angel_01"):
    print(f"🔍 Consultando ficha de: {user_id}...")
    
    doc_ref = db.collection("medical_history").document(user_id)
    doc = doc_ref.get()
    
    contexto = "No tengo tu ficha, m'hijo."
    if doc.exists:
        contexto = "Presión 118/75, Glucosa 90 mg/dL."

    if not os.path.exists(image_path):
        print(f"❌ Error: No está la imagen.")
        return

    foto = Image.load_from_file(image_path)
    
    prompt = f"""
    Eres Panchote, el asistente de salud chileno.
    Contexto médico: {contexto}
    Analiza la foto, identifica el plato y da un consejo de salud con mucha chilenidad.
    Si es poco sano, di "¡Frene el carro, m'hijo!".
    """

    print(f"📸 Analizando con Gemini 2.0...")
    
    try:
        response = model.generate_content([prompt, foto])
        consejo = response.text
        
        print("\n" + "="*50)
        print(consejo)
        print("="*50)
        
        # --- NUEVA MEJORA: PERSISTENCIA ---
        # Extraemos un nombre corto del plato (primeras palabras) para el log
        resumen_plato = consejo[:30] + "..." 
        guardar_en_historial(user_id, resumen_plato, consejo)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    panchote_vidente("assets/plato.jpg")