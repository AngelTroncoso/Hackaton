from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from api.supabase_config import SupabaseManager
from core.analysis import BioTwinEngine
from typing import Annotated

app = FastAPI(title="BioTwin AI API", version="1.0.0")

# Inicializar el gestor de Supabase
try:
    supabase_manager = SupabaseManager()
except Exception as e:
    raise RuntimeError(f"Error al inicializar SupabaseManager: {e}")

class PatientRequest(BaseModel):
    nombre: str
    rut: str
    edad: Annotated[int, Field(ge=0)]
    genero: str  # 'masculino', 'femenino', 'otro', 'no informado'

class BiomarkerRequest(BaseModel):
    paciente_id: str
    glucosa: Annotated[float, Field(ge=0)]
    presion_sistolica: Annotated[float, Field(ge=0)]
    presion_diastolica: Annotated[float, Field(ge=0)]

@app.post("/registrar-paciente")
async def registrar_paciente(request: PatientRequest):
    """Registra un nuevo paciente anonimizado en Supabase."""
    try:
        paciente = supabase_manager.insert_patient(
            nombre=request.nombre,
            rut=request.rut,
            edad=request.edad,
            genero=request.genero
        )
        return {"mensaje": "Paciente registrado exitosamente", "paciente": paciente}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=500, detail=str(re))

@app.post("/procesar-biomarcadores")
async def procesar_biomarcadores(request: BiomarkerRequest):
    """Procesa biomarcadores, calcula Health Score y genera alertas si es necesario."""
    try:
        # 1. Calcular Health Score
        data = {
            "glucosa": request.glucosa,
            "presion_sistolica": request.presion_sistolica,
            "presion_diastolica": request.presion_diastolica
        }
        score = BioTwinEngine.compute_score(data)
        recomendacion = BioTwinEngine.recommendation(score)

        # 2. Guardar biomarcadores en Supabase
        biomarcadores = [
            {"tipo": "glucosa", "valor": request.glucosa, "unidad": "mg/dL"},
            {"tipo": "presion_sistolica", "valor": request.presion_sistolica, "unidad": "mmHg"},
            {"tipo": "presion_diastolica", "valor": request.presion_diastolica, "unidad": "mmHg"}
        ]
        
        for b in biomarcadores:
            supabase_manager.insert_biomarker(
                paciente_id=request.paciente_id,
                tipo=b["tipo"],
                valor=b["valor"],
                unidad=b["unidad"]
            )

        # 3. LÓGICA DE ALERTAS AUTOMÁTICAS
        # Si el score es crítico (< 50), registramos la incidencia
        if score < 50:
            supabase_manager.client.table("alertas").insert({
                "paciente_id": request.paciente_id,
                "score_obtenido": score,
                "mensaje": f"Alerta Crítica: Score de salud en {score}. {recomendacion}",
                "estado": "pendiente"
            }).execute()

        return {
            "mensaje": "Biomarcadores procesados y guardados",
            "health_score": score,
            "recomendacion": recomendacion,
            "alerta_generada": score < 50
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")