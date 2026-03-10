import pandas as pd
from typing import Dict, List
from pydantic import BaseModel, confloat, Field

class BiomarkerEntry(BaseModel):
    glucosa: float = Field(ge=0)
    presion_sistolica: float = Field(ge=0)
    presion_diastolica: float = Field(ge=0)

class BioTwinEngine:
    """Motor de evaluación y predicción para el gemelo digital."""

    # Rangos ideales según guías clínicas (simplificados)
    _ideal = {
        "glucosa": (70, 99),
        "presion_sistolica": (90, 120),
        "presion_diastolica": (60, 80),
    }

    @classmethod
    def compute_score(cls, data: Dict[str, float]) -> float:
        """Calcula el health score actual (0-100)."""
        entry = BiomarkerEntry(**data)
        score = 100.0

        # Evaluación de Glucosa
        g = entry.glucosa
        if g > 126:
            score -= 40
        elif g > cls._ideal["glucosa"][1]:
            score -= 20

        # Evaluación de Presión Arterial
        sys = entry.presion_sistolica
        dia = entry.presion_diastolica
        if sys >= 140 or dia >= 90:
            score -= 30
        elif sys > cls._ideal["presion_sistolica"][1] or dia > cls._ideal["presion_diastolica"][1]:
            score -= 15

        return max(0.0, min(100.0, score))

    @classmethod
    def recommendation(cls, score: float) -> str:
        """Proporciona la recomendación clínica basada en el score."""
        if score >= 80:
            return "Mantener estilo de vida saludable."
        if score >= 50:
            return "Revisar con profesional y considerar ajustes en dieta/ejercicio."
        return "Consultar atención médica de inmediato."

    @staticmethod
    def analyze_trend(biomarkers: List[Dict]) -> str:
        """
        Analiza la tendencia histórica para predecir riesgos.
        Calcula la diferencia entre el último registro y el anterior.
        """
        if not biomarkers or len(biomarkers) < 2:
            return "📈 Datos insuficientes para proyectar tendencia."
        
        # Convertir a DataFrame para facilitar el manejo de series temporales
        df = pd.DataFrame(biomarkers)
        df['fecha_registro'] = pd.to_datetime(df['fecha_registro'])
        df = df.sort_values('fecha_registro')
        
        # Analizar tendencia de Glucosa
        glucosa_hist = df[df['tipo'] == 'glucosa']
        if len(glucosa_hist) >= 2:
            ultimo = glucosa_hist.iloc[-1]['valor']
            penultimo = glucosa_hist.iloc[-2]['valor']
            diferencia = ultimo - penultimo
            
            if diferencia > 20:
                return "⚠️ Riesgo Alza: Glucosa subiendo rápidamente."
            elif diferencia < -20:
                return "⚠️ Riesgo Hipoglucemia: Descenso brusco detectado."
        
        return "📉 Tendencia Estable: Sin cambios bruscos en las últimas mediciones."