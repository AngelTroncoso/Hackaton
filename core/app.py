import streamlit as st
import os
import vertexai
from vertexai.generative_models import GenerativeModel, Image
from google.cloud import firestore
from datetime import datetime
from PIL import Image as PIL_Image
import io

# ==========================================================
# 🔑 CONFIGURACIÓN DE INFRAESTRUCTURA (GCP)
# ==========================================================
# Asegúrate de que el JSON esté en la misma carpeta
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "firebase_key.json"

PROJECT_ID = "multiagentes-479321"
LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)

db = firestore.Client()
model = GenerativeModel("gemini-2.0-flash-001")

# ==========================================================
# 🏠 INTERFAZ DE USUARIO (STREAMLIT)
# ==========================================================
st.set_page_config(page_title="BioTwin AI - Panchote", page_icon="🤠")

st.title("🤠 BioTwin AI: El Consejo de Panchote")
st.markdown("""
    ### ¡Hola, m'hijo! 
    Suba una fotito de lo que va a comer y yo le digo si le hace bien pa' su salud.
""")

# Sidebar con datos del paciente (Simulando el "Digital Twin")
st.sidebar.header("📊 Ficha Digital (BioTwin)")
user_id = "angel_01"

def obtener_ficha(uid):
    doc = db.collection("medical_history").document(uid).get()
    if doc.exists:
        return doc.to_dict()
    return None

ficha = obtener_ficha(user_id)
if ficha:
    st.sidebar.success(f"Paciente: {user_id}")
    st.sidebar.info(f"❤️ Presión: 118/75\n\n🍭 Glucosa: 90 mg/dL")
else:
    st.sidebar.warning("No se encontró ficha médica.")

# ==========================================================
# 📸 PROCESAMIENTO MULTIMODAL
# ==========================================================
uploaded_file = st.file_uploader("Eliga una imagen de su plato...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Mostrar la imagen en la UI
    img_display = PIL_Image.open(uploaded_file)
    st.image(img_display, caption='Su plato de hoy', use_container_width=True)
    
    if st.button("Preguntarle a Panchote"):
        with st.spinner('Panchote está mirando el plato...'):
            try:
                # Convertir para Vertex AI
                img_bytes = uploaded_file.getvalue()
                foto_gemini = Image.from_bytes(img_bytes)
                
                # Contexto médico para el Agente
                contexto = "Presión 118/75, Glucosa 90 mg/dL."
                
                prompt = f"""
                Eres Panchote, un asistente de salud chileno de campo, sabio y cercano.
                Contexto médico del usuario: {contexto}
                
                Misión:
                1. Identifica la comida en la foto.
                2. Analiza si es saludable para estos signos vitales.
                3. Responde con mucha chilenidad (m'hijo, un siete, iñor).
                4. Si es malo, usa tu frase: "¡Frene el carro, m'hijo!".
                """
                
                # Llamada al Agente
                response = model.generate_content([prompt, foto_gemini])
                consejo = response.text
                
                # Mostrar resultado
                st.subheader("🗣️ El consejo de Panchote:")
                st.write(consejo)
                
                # --- GUARDAR EN HISTORIAL (GCP Firestore) ---
                log_ref = db.collection("daily_logs").document()
                log_ref.set({
                    "user_id": user_id,
                    "fecha": datetime.now(),
                    "consejo": consejo,
                    "tipo": "interaccion_envivo"
                })
                st.toast("✅ Consejo guardado en su historial médico.")
                
            except Exception as e:
                st.error(f"Error: {e}")

st.divider()
st.caption("BioTwin AI | Proyecto para Gemini Live Agent Challenge | Santiago, Chile")