import streamlit as st
import os
import PIL.Image
import io
import warnings
from google import genai
from google.genai import types
from google.cloud import firestore
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

# Suprimir advertencias deprecadas de google-genai
warnings.filterwarnings('ignore', category=FutureWarning)

# --- 1. CONFIGURACIÓN DE ENTORNO ---
load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID") or "multiagentes-479321"
LOCATION = os.getenv("LOCATION", "us-west1")
MODEL_ID = "gemini-pro"
ELEVEN_KEY = os.getenv("ELEVEN_LABS_API_KEY", "")

st.set_page_config(page_title="Panchote Multimodal GOLD", page_icon="🦭", layout="wide")

# --- 2. CARGA DE CLIENTES ---
@st.cache_resource
def get_clients():
    try:
        # Inicialización compatible con el SDK 1.67.0
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
        return client
    except Exception as e:
        st.error(f"Error en Google GenAI: {e}")
        return None

@st.cache_resource
def get_firestore_client():
    try:
        db = firestore.Client(project=PROJECT_ID)
        return db
    except Exception:
        return None

@st.cache_resource
def get_elevenlabs_client():
    try:
        el = ElevenLabs(api_key=ELEVEN_KEY) if ELEVEN_KEY else None
        return el
    except Exception:
        return None

client = get_clients()
db = get_firestore_client()
el_client = get_elevenlabs_client()

# --- 3. OBTENCIÓN DE DATOS DE SALUD ---
@st.cache_data(ttl=300)
def obtener_salud():
    glucosa, presion = "95 mg/dL", "120/80"
    if db:
        try:
            doc = db.collection("medical_history").document("angel_01").get()
            if doc.exists:
                d = doc.to_dict() or {}
                glucosa = d.get("glucosa", glucosa)
                presion = d.get("presion", presion)
        except Exception:
            pass
    return glucosa, presion

glucosa, presion = obtener_salud()

# --- 4. FUNCIÓN MULTIMODAL ROBUSTA ---
def llamar_a_panchote(audio_bytes=None, img_bytes=None):
    """
    Genera respuesta multimodal con audio e imagen opcionales.
    Usa client.models.generate_content (flujo estándar).
    Implementa extracción de texto segura con try/except.
    """
    if not client:
        return "Error: Cliente no inicializado", None
    
    instrucciones = (
        f"Eres Panchote, el lobo marino sabio de Puerto Montt. "
        f"Tu paciente tiene Glucosa {glucosa} y Presión {presion}. "
        "Escucha el audio y mira la imagen del plato. Usa modismos chilenos sureños. "
        "Sé muy breve: máximo 2 frases sobre si el alimento es seguro para su salud."
    )

    try:
        # Construcción robusta de contenido multimodal
        contents = [instrucciones]
        
        # Audio (si está disponible)
        if audio_bytes:
            audio_part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")
            contents.append(audio_part)
        
        # Imagen (si el usuario tomó una foto)
        if img_bytes:
            img_pil = PIL.Image.open(io.BytesIO(img_bytes))
            img_data = io.BytesIO()
            img_pil.save(img_data, format="PNG")
            img_data.seek(0)
            img_part = types.Part.from_bytes(data=img_data.getvalue(), mime_type="image/png")
            contents.append(img_part)
        
        # Generación de contenido (flujo estándar, no .live)
        try:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=contents
            )
        except Exception as e:
            return f"Error al generar contenido: {str(e)}", None
        
        # Extracción segura de texto con try/except
        respuesta_texto = None
        try:
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    parts = candidate.content.parts
                    if isinstance(parts, list) and len(parts) > 0:
                        part = parts[0]
                        if hasattr(part, 'text'):
                            respuesta_texto = part.text
        except (AttributeError, IndexError, TypeError) as e:
            st.warning(f"Advertencia al extraer texto: {e}")
            respuesta_texto = "Panchote necesita hablar contigo, pero ocurrió un error."
        
        return respuesta_texto or "Sin respuesta disponible", response
        
    except Exception as e:
        st.error(f"Error en generación multimodal: {e}")
        return f"Error: {str(e)}", None

# --- 5. FUNCIÓN TTS CON ELEVENLABS ---
def generar_audio_respuesta(texto):
    """
    Genera audio de la respuesta usando ElevenLabs.
    Usa eleven_multilingual_v2 para soporte multiidioma.
    """
    if not el_client or not texto:
        return None
    
    try:
        audio_stream = el_client.text_to_speech.convert(
            text=texto,
            voice_id="ErXwobaYiN4jkqXm7h7W",
            model_id="eleven_multilingual_v2",
            stream=True
        )
        
        # Recolectar audio en bytes
        audio_bytes = b""
        for chunk in audio_stream:
            if chunk:
                audio_bytes += chunk
        
        return audio_bytes if audio_bytes else None
    except Exception as e:
        st.warning(f"Error en TTS: {e}")
        return None

# --- 6. INTERFAZ STREAMLIT ---
st.title("🦭 Panchote - Asistente Médico Multimodal")
st.markdown("*El lobo marino sabio de Puerto Montt te ayuda con tu nutrición*")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Captura de Audio")
    audio_input = st.audio_input("Cuéntale a Panchote qué vas a comer")

with col2:
    st.subheader("Captura de Imagen")
    photo_input = st.camera_input("Muéstrale tu plato")

# Procesar entrada
if st.button("Consultar a Panchote", type="primary"):
    audio_bytes = None
    img_bytes = None
    
    # Convertir audio de Streamlit
    if audio_input:
        audio_bytes = audio_input.getvalue()
    
    # Convertir imagen de Streamlit
    if photo_input:
        img_bytes = photo_input.getvalue()
    
    if audio_bytes or img_bytes:
        with st.spinner("🧠 Panchote está pensando..."):
            respuesta, response_obj = llamar_a_panchote(audio_bytes, img_bytes)
        
        if respuesta and not respuesta.startswith("Error"):
            st.success("Respuesta de Panchote:")
            st.write(respuesta)
            
            # Generar y reproducir audio
            if el_client:
                audio_output = generar_audio_respuesta(respuesta)
                if audio_output:
                    st.audio(audio_output, format="audio/mp3", autoplay=True)
            else:
                st.info("🔔 ElevenLabs no configurado. Omitiendo síntesis de voz.")
        else:
            st.error(f"Error desde Panchote: {respuesta}")
    else:
        st.warning("Proporciona audio o una imagen para consultar a Panchote")

# --- 7. ESTADO DE SALUD DEL PACIENTE ---
st.divider()
st.subheader("Estado de Salud Actual")
col_gluc, col_pres = st.columns(2)
col_gluc.metric("Glucosa", glucosa)
col_pres.metric("Presión", presion)
