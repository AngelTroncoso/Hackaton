import streamlit as st
import os
import PIL.Image
import io
import warnings
from google import genai
from google.genai import types
from google.cloud import firestore
from dotenv import load_dotenv

try:
    from elevenlabs.client import ElevenLabs
except ImportError:
    ElevenLabs = None

# Suprimir advertencias deprecadas de google-genai
warnings.filterwarnings('ignore', category=FutureWarning)

# --- 1. CONFIGURACIÓN DE ENTORNO ---
load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID") or "multiagentes-479321"
LOCATION = os.getenv("LOCATION", "us-west1")
MODEL_ID = os.getenv("MODEL_ID", "gemini-2.5-flash")
ELEVEN_KEY = os.getenv("ELEVEN_LABS_API_KEY", "")
ELEVEN_VOICE_ID = os.getenv("ELEVEN_VOICE_ID", "ErXwobaYiN4jkqXm7h7W")

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
        if not ElevenLabs or not ELEVEN_KEY:
            return None
        el = ElevenLabs(api_key=ELEVEN_KEY)
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
            detalle = str(e)
            if "404" in detalle and "models/" in detalle:
                return (
                    f"Error al generar contenido: el modelo '{MODEL_ID}' no existe, "
                    f"está retirado o tu proyecto no tiene acceso en {LOCATION}. "
                    "Prueba con MODEL_ID=gemini-2.5-flash o revisa el acceso del proyecto en Vertex AI.",
                    None,
                )
            return f"Error al generar contenido: {detalle}", None
        
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
        st.session_state["ultimo_tts_error"] = "Cliente de ElevenLabs no disponible."
        return None
    
    try:
        st.session_state["ultimo_tts_error"] = None
        audio_result = el_client.text_to_speech.convert(
            text=texto,
            voice_id=ELEVEN_VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )

        if isinstance(audio_result, bytes):
            return audio_result or None

        if isinstance(audio_result, bytearray):
            return bytes(audio_result) or None

        audio_bytes = b""
        for chunk in audio_result:
            if isinstance(chunk, bytes):
                audio_bytes += chunk
            elif isinstance(chunk, bytearray):
                audio_bytes += bytes(chunk)

        return audio_bytes if audio_bytes else None
    except Exception as e:
        st.session_state["ultimo_tts_error"] = str(e)
        st.warning(f"Error en TTS: {e}")
        return None


def inicializar_estado():
    st.session_state.setdefault("ultima_respuesta", None)
    st.session_state.setdefault("ultimo_audio_tts", None)
    st.session_state.setdefault("ultima_imagen", None)
    st.session_state.setdefault("ultimo_tts_error", None)
    st.session_state.setdefault("audio_prueba_tts", None)


def obtener_imagen_entrada(camera_file, upload_file):
    archivo = camera_file or upload_file
    if not archivo:
        return None
    return archivo.getvalue()


def diagnostico_tts():
    diagnostico = {
        "elevenlabs_importado": ElevenLabs is not None,
        "api_key_configurada": bool(ELEVEN_KEY),
        "voice_id_configurado": bool(ELEVEN_VOICE_ID),
        "voice_id_actual": ELEVEN_VOICE_ID or "(vacío)",
        "cliente_inicializado": el_client is not None,
        "ultimo_error_tts": st.session_state.get("ultimo_tts_error"),
    }
    return diagnostico

# --- 6. INTERFAZ STREAMLIT ---
inicializar_estado()

st.title("🦭 Panchote - Asistente Médico Multimodal")
st.markdown("*El lobo marino sabio de Puerto Montt te ayuda con tu nutrición*")

with st.form("consulta_panchote"):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Captura de Audio")
        audio_input = st.audio_input(
            "Cuéntale a Panchote qué vas a comer",
            key="panchote_audio",
        )

    with col2:
        st.subheader("Captura de Imagen")
        st.caption("Si la cámara falla en tu navegador, usa la carga manual como respaldo.")
        photo_input = st.camera_input(
            "Muéstrale tu plato",
            key="panchote_camera",
        )
        upload_input = st.file_uploader(
            "O sube una imagen del plato",
            type=["jpg", "jpeg", "png"],
            key="panchote_upload",
        )

    consultar = st.form_submit_button("Consultar a Panchote", type="primary")

img_bytes = obtener_imagen_entrada(photo_input, upload_input)
if img_bytes:
    st.session_state["ultima_imagen"] = img_bytes

if st.session_state["ultima_imagen"]:
    st.image(st.session_state["ultima_imagen"], caption="Imagen lista para analizar", width=280)

if consultar:
    audio_bytes = audio_input.getvalue() if audio_input else None
    img_bytes = img_bytes or st.session_state["ultima_imagen"]

    if audio_bytes or img_bytes:
        with st.spinner("🧠 Panchote está pensando..."):
            respuesta, _response_obj = llamar_a_panchote(audio_bytes, img_bytes)

        st.session_state["ultima_respuesta"] = respuesta
        st.session_state["ultimo_audio_tts"] = None

        if respuesta and not respuesta.startswith("Error"):
            if el_client:
                st.session_state["ultimo_audio_tts"] = generar_audio_respuesta(respuesta)
        else:
            st.session_state["ultima_respuesta"] = f"Error desde Panchote: {respuesta}"
    else:
        st.warning("Proporciona audio o una imagen para consultar a Panchote")

if st.session_state["ultima_respuesta"]:
    if st.session_state["ultima_respuesta"].startswith("Error"):
        st.error(st.session_state["ultima_respuesta"])
    else:
        st.success("Respuesta de Panchote:")
        st.write(st.session_state["ultima_respuesta"])

        if st.session_state["ultimo_audio_tts"]:
            st.audio(st.session_state["ultimo_audio_tts"], format="audio/mp3", autoplay=True)
        elif ELEVEN_KEY and not el_client:
            st.warning("ElevenLabs está configurado, pero el cliente no pudo inicializarse.")
        else:
            st.info("🔔 Panchote respondió en texto. Configura ElevenLabs para escuchar su voz.")

with st.expander("Diagnóstico de voz ElevenLabs"):
    diag = diagnostico_tts()
    st.write("Librería ElevenLabs importada:", "Sí" if diag["elevenlabs_importado"] else "No")
    st.write("API key configurada:", "Sí" if diag["api_key_configurada"] else "No")
    st.write("Voice ID configurado:", diag["voice_id_actual"])
    st.write("Cliente inicializado:", "Sí" if diag["cliente_inicializado"] else "No")

    texto_prueba = st.text_input(
        "Texto para probar la voz",
        value="Hola, soy Panchote y ya estoy listo para hablar contigo.",
        key="texto_prueba_tts",
    )

    if st.button("Probar voz", key="boton_probar_tts"):
        st.session_state["audio_prueba_tts"] = generar_audio_respuesta(texto_prueba)

    if st.session_state["audio_prueba_tts"]:
        st.audio(st.session_state["audio_prueba_tts"], format="audio/mp3")

    if diag["ultimo_error_tts"]:
        st.error(f"Último error TTS: {diag['ultimo_error_tts']}")
        if "voice_not_found" in diag["ultimo_error_tts"] or "No se encontró una voz" in diag["ultimo_error_tts"]:
            st.info(
                "Tu API key sí está llegando, pero ese voice_id no existe en tu cuenta o ya no está disponible. "
                "Prueba con otra voz válida de ElevenLabs en ELEVEN_VOICE_ID."
            )
    else:
        st.caption("Todavía no hay errores de TTS registrados en esta sesión.")

# --- 7. ESTADO DE SALUD DEL PACIENTE ---
st.divider()
st.subheader("Estado de Salud Actual")
col_gluc, col_pres = st.columns(2)
col_gluc.metric("Glucosa", glucosa)
col_pres.metric("Presión", presion)
