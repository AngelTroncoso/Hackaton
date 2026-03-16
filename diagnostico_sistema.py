import os
import sys
import importlib
import streamlit as st
from dotenv import load_dotenv

def verificar_herramientas_ui():
    """
    Versión visual del diagnóstico para ser ejecutada con Streamlit.
    """
    load_dotenv()
    
    st.title("🔍 Auditoría de Sistema - BioTwin AI")
    st.markdown("---")

    # 1. Verificación de Librerías (SDKs)
    librerias = {
        "google.genai": "Google GenAI (Gemini 2.0)",
        "elevenlabs": "ElevenLabs (Voz)",
        "google.cloud.firestore": "Firestore (Base de Datos)",
        "streamlit": "Streamlit (Interfaz)",
        "PIL": "Pillow (Procesamiento de Imágenes)"
    }

    st.subheader("📦 Estatus de Librerías")
    cols_lib = st.columns(2)
    for i, (lib, nombre) in enumerate(librerias.items()):
        col = cols_lib[i % 2]
        try:
            m = importlib.import_module(lib)
            version = getattr(m, "__version__", "Instalada")
            col.success(f"**{nombre}**: {version}")
        except ImportError:
            col.error(f"**{nombre}**: NO ENCONTRADA")

    # 2. Verificación de Variables de Entorno (.env)
    st.subheader("🔐 Configuración de Credenciales")
    vars_env = ["ELEVEN_LABS_API_KEY", "PROJECT_ID", "GOOGLE_APPLICATION_CREDENTIALS"]
    for var in vars_env:
        valor = os.getenv(var)
        if valor:
            st.write(f"✅ **{var}**: Configurada (`{valor[:5]}...`)")
        else:
            st.error(f"❌ **{var}**: FALTANTE en archivo .env")

    # 3. Verificación de Atributo .live (Crítico para la Hackathon)
    st.subheader("🚀 Verificación Multimodal Live")
    try:
        from google import genai
        # Intentamos inicializar un cliente mínimo para verificar el atributo
        client = genai.Client(vertexai=True, project="test", location="us-central1")
        if hasattr(client.models, "live"):
            st.success("✅ SDK compatible con Multimodal Live API")
        else:
            st.warning("⚠️ SDK instalado pero NO soporta .live (Necesitas upgrade)")
            st.code("pip install --upgrade google-genai")
    except Exception as e:
        st.info("ℹ️ No se pudo verificar el atributo .live (Falta configuración de Vertex o Credenciales)")

    st.markdown("---")
    st.info("💡 **Consejo:** Si ves errores rojos, ejecuta `pip install --upgrade google-genai elevenlabs streamlit python-dotenv` en tu terminal.")

if __name__ == "__main__":
    # Esto permite ejecutarlo directamente con: streamlit run diagnostico_sistema.py
    verificar_herramientas_ui()