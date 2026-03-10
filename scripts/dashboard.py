import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px

# --- PARCHE DE RUTAS ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.supabase_config import SupabaseManager
from core.analysis import BioTwinEngine

# 1. Configuración Mobile-Friendly
st.set_page_config(
    page_title="BioTwin AI Mobile", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

st.title("🩺 BioTwin AI")
st.caption("Sistema de Monitoreo de Gemelos Digitales")

# Inicializar Supabase
manager = SupabaseManager()

# 2. Selector simplificado (Sidebar)
with st.sidebar:
    st.header("Configuración")
    pacientes_res = manager.client.table("pacientes").select("id_anonimo").execute()
    pacientes = [p["id_anonimo"] for p in pacientes_res.data]
    paciente_seleccionado = st.sidebar.selectbox("Paciente:", pacientes)

# 3. Estado Actual y Score
st.subheader("🎯 Estado Actual")
biomarkers = manager.query_patient_biomarkers(paciente_seleccionado)

if biomarkers:
    tipos = ["glucosa", "presion_sistolica", "presion_diastolica"]
    ultimos = {}
    for t in tipos:
        data_tipo = [b for b in biomarkers if b["tipo"] == t]
        ultimos[t] = data_tipo[-1]["valor"] if data_tipo else 100.0

    score = BioTwinEngine.compute_score(ultimos)
    
    m1, m2 = st.columns(2)
    m1.metric("Health Score", f"{score}/100")
    status = "🔴 CRÍTICO" if score < 50 else "🟡 ALERTA" if score < 80 else "🟢 ESTABLE"
    m2.metric("Estado", status)

    st.info(f"**Sugerencia IA:** {BioTwinEngine.recommendation(score)}")
else:
    st.warning("Sin datos registrados.")

# 4. ANÁLISIS PREDICTIVO (Nueva Sección)
st.markdown("---")
st.subheader("🔮 Análisis Predictivo")
prediccion = BioTwinEngine.analyze_trend(biomarkers)
if "⚠️" in prediccion:
    st.warning(prediccion)
else:
    st.success(prediccion)

# 5. Gráfico Histórico
st.subheader("📈 Historial")
if biomarkers:
    df = pd.DataFrame(biomarkers)
    df["fecha_registro"] = pd.to_datetime(df["fecha_registro"])
    
    fig = px.line(df, x="fecha_registro", y="valor", color="tipo", markers=True)
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# 6. GESTIÓN DE ALERTAS (Última Sección)
st.markdown("---")
st.subheader("⚠️ Alertas Críticas Pendientes")

alertas_res = manager.client.table("alertas")\
    .select("*")\
    .eq("estado", "pendiente")\
    .execute()

if alertas_res.data:
    for alerta in alertas_res.data:
        with st.expander(f"🚨 Alerta ID #{alerta['id']} - Score: {alerta['score_obtenido']}"):
            st.write(f"**Mensaje:** {alerta['mensaje']}")
            st.write(f"**Fecha:** {alerta['fecha_alerta']}")
            if st.button(f"Marcar como Atendida #{alerta['id']}"):
                manager.client.table("alertas")\
                    .update({"estado": "atendida"})\
                    .eq("id", alerta['id'])\
                    .execute()
                st.rerun()
else:
    st.success("No hay alertas críticas pendientes.")

# --- MÓDULO DE COMENTARIOS MÉDICOS ---
st.markdown("---")
st.subheader("📝 Evolución Clínica")

# Formulario para nueva nota
with st.form("nueva_nota", clear_on_submit=True):
    nueva_nota = st.text_area("Agregar observación médica:", placeholder="Ej: Paciente estable tras ajuste de dieta.")
    submit_nota = st.form_submit_button("Guardar Nota")
    
    if submit_nota and nueva_nota:
        try:
            manager.client.table("notas_clinicas").insert({
                "paciente_id": paciente_seleccionado,
                "comentario": nueva_nota
            }).execute()
            st.success("Nota guardada exitosamente.")
            st.rerun()
        except Exception as e:
            st.error(f"Error al guardar: {e}")

# Mostrar historial de notas
st.write("**Historial de Observaciones:**")
notas_res = manager.client.table("notas_clinicas")\
    .select("*")\
    .eq("paciente_id", paciente_seleccionado)\
    .order("fecha_registro", desc=True)\
    .execute()

if notas_res.data:
    for nota in notas_res.data:
        fecha = pd.to_datetime(nota['fecha_registro']).strftime('%d/%m/%Y %H:%M')
        st.info(f"📅 **{fecha}**\n\n{nota['comentario']}")
else:
    st.caption("No hay notas registradas para este paciente.")