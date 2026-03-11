import os
import google.generativeai as genai
from typing import List, Dict

class BioTwinAI:
    def __init__(self):
        # Asegúrate de tener tu API KEY en las variables de entorno de Codespaces
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_clinical_summary(self, patient_data: Dict, notes: List[str]):
        """Genera un análisis profesional combinando datos y notas."""
        
        prompt = f"""
        Actúa como un asistente médico experto de BioTwin AI.
        Analiza los siguientes datos del paciente:
        - Biomarcadores actuales: {patient_data}
        - Últimas observaciones clínicas: {notes}
        
        Proporciona un resumen ejecutivo de 3 puntos:
        1. Estado actual simplificado.
        2. Riesgos detectados basados en la tendencia.
        3. Sugerencia de acción inmediata para el equipo médico.
        
        Mantén un tono profesional, empático y preciso.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error al generar análisis de IA: {str(e)}"