import streamlit as st
import os
import vertexai
from vertexai.generative_models import GenerativeModel, Image, Part
from google.cloud import firestore
from datetime import datetime
from PIL import Image as PIL_Image
import io
import requests
import tempfile
import asyncio
import base64
from pathlib import Path
from dotenv import load_dotenv

# Nota: Para la Live API real en producción se suele usar el SDK de Vertex AI GenAI Beta
# Aquí adaptamos la interfaz para simular el comportamiento de flujo continuo (Live) 
# que solicita la categoría de "Agentes en Vivo".

# ==========================================================
# 🔑 CONFIGURACIÓN DE GOOGLE CLOUD
# ==========================================================
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = "pNInz6obpgDQGcFmaJgB" 

BASE_DIR = Path(__file__).resolve().parent.parent
KEY_PATH = BASE_DIR / "firebase_key.json"

if not KEY_PATH.exists():
    st.error(f"❌ No se encontró firebase_key.json")
    st.stop()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(KEY_PATH)

PROJECT_ID = "multiagentes-479321"
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)
db = firestore.Client()

# Usamos el modelo 2.0 Flash que es el motor de las experiencias Live
model = GenerativeModel("gemini-2.0-flash-001")

# ==========================================================
# 🗣️ SALIDA DE VOZ (ELEVENLABS)
# ==========================================================

def generar_voz_panchote(texto):
    if not ELEVENLABS_API_KEY: return None
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
    data = {
        "text": texto,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.4, "similarity_boost": 0.8}
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        return response.content if response.status_code == 200 else None
    except: return None

# ==========================================================
# 🏠 INTERFAZ "LIVE AGENT"
# ==========================================================
st.set_page_config(page_title="Panchote Live Mode", page_icon="🦭", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e0e0e0; }
    .live-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        background-color: #ff4b4b;
        border-radius: 50%;
        margin-right: 8px;
        animation: blink 1.5s infinite;
    }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .status-bar {
        background: #1e2329;
        padding: 10px 20px;
        border-radius: 30px;
        display: flex;
        align-items: center;
        margin-bottom: 25px;
        border: 1px solid #388e3c;
    }
    .chat-card {
        background: #161b22;
        border-radius: 20px;
        padding: 30px;
        border: 1px solid #30363d;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# Encabezado con estado "Live"
st.markdown('<div class="status-bar"><span class="live-indicator"></span> <b>MODO CONVERSACIONAL ACTIVO</b> | Conectado a Gemini Live API</div>', unsafe_allow_html=True)

# CARGA DE DATOS DESDE FIRESTORE
user_id = "angel_01"
ficha = {"presion": "118/75", "glucosa": "90 mg/dL"}
try:
    doc_ref = db.collection("medical_history").document(user_id).get()
    if doc_ref.exists:
        data = doc_ref.to_dict()
        ficha.update({k: data[k] for k in ficha if k in data})
except: pass

with st.sidebar:
    st.title("🦭 BioTwin")
    st.info(f"Paciente: {user_id}")
    st.metric("Glucosa Actual", ficha['glucosa'])
    st.metric("Presión Arterial", ficha['presion'])
    
    # Simulación de cámara activa
    st.divider()
    st.write("📷 **Visión del Agente**")
    camera_input = st.camera_input("Enfoca tu comida")

# Contenedor principal de conversación
st.markdown('<div class="chat-card">', unsafe_allow_html=True)

col_info, col_visual = st.columns([2, 1])

with col_info:
    st.subheader("🗣️ Conversa con Panchote")
    st.write("_Panchote está escuchando... Solo habla naturalmente sobre lo que ves en cámara._")
    
    # En una implementación Live real, aquí se activa el stream de audio.
    # Para Streamlit, usamos el componente de entrada de audio que actúa como trigger.
    audio_input = st.audio_input("Hablar ahora")

    if audio_input:
        with st.spinner("Panchote está pensando..."):
            # Procesamiento Intermodal (Imagen de cámara + Audio)
            img_bytes = camera_input.getvalue() if camera_input else None
            audio_bytes = audio_input.getvalue()
            
            # Construcción del prompt intermodal para Gemini 2.0
            prompt = f"""
            Eres Panchote en modo LIVE. Estas en una conversación fluida.
            Contexto médico: Presión {ficha['presion']}, Glucosa {ficha['glucosa']}.
            Analiza lo que ves en la cámara (si hay imagen) y responde a lo que escuchas.
            Sé muy breve, carismático y usa modismos chilenos de Puerto Montt.
            Si no hay imagen, dile que te muestre el plato para poder ayudarlo mejor.
            """
            
            partes = [prompt]
            if img_bytes: partes.append(Image.from_bytes(img_bytes))
            partes.append(Part.from_data(data=audio_bytes, mime_type="audio/wav"))
            
            try:
                response = model.generate_content(partes)
                texto_respuesta = response.text
                
                # Mostrar respuesta visual
                st.chat_message("assistant", avatar="🦭").write(texto_respuesta)
                
                # Generar respuesta auditiva instantánea
                voz_bytes = generar_voz_panchote(texto_respuesta)
                if voz_bytes:
                    st.audio(voz_bytes, format="audio/mp3", autoplay=True)
                
                # Guardar interacción en logs para analítica de salud
                db.collection("daily_logs").add({
                    "user_id": user_id,
                    "timestamp": datetime.now(),
                    "interaction_type": "live_multimodal",
                    "response": texto_respuesta
                })
                
            except Exception as e:
                st.error(f"Error en el flujo live: {e}")

with col_visual:
    if camera_input:
        st.write("✅ **Imagen capturada**")
    else:
        st.warning("⚠️ Activa la cámara para que Panchote vea tu comida.")
    
    st.image("https://cdn-icons-png.flaticon.com/512/3564/3564858.png", width=100)
    st.caption("Panchote está listo para asesorarte en tiempo real.")

st.markdown('</div>', unsafe_allow_html=True)