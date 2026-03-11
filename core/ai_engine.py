import os
import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import firestore
from dotenv import load_dotenv

# Cargamos las variables del .env
load_dotenv()

class BioTwinFirestoreEngine:
    def __init__(self):
        # 1. Configuración de Vertex AI
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "multiagentes-479321")
        self.location = "us-central1" 
        
        vertexai.init(project=self.project_id, location=self.location)
        
        # 2. Cliente de Firestore (Integración confirmada con éxito)
        self.db = firestore.Client() 
        
        # 3. ID de modelo actualizado según tu Model Garden
        # Usamos el identificador corto que el SDK de Vertex resuelve automáticamente
        self.model_id = "gemini-2.0-flash-001"
        self.model = GenerativeModel(self.model_id)

    def _get_history(self, patient_id: str):
        """Recupera el último resumen médico desde Firestore."""
        try:
            doc_ref = self.db.collection("medical_history").document(patient_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict().get("last_summary", "Primera vez que conversamos.")
            return "Sin historial previo en la ficha."
        except Exception as e:
            return f"Error Firestore: {e}"

    def _save_interaction(self, patient_id: str, new_summary: str):
        """Actualiza la ficha médica en Firestore."""
        try:
            doc_ref = self.db.collection("medical_history").document(patient_id)
            doc_ref.set({"last_summary": new_summary}, merge=True)
        except Exception as e:
            print(f"⚠️ Error al guardar en Firestore: {e}")

    def generate_clinical_summary(self, patient_id: str, medical_data: dict, notes: list):
        """Genera respuesta con la personalidad sureña de Panchote."""
        history = self._get_history(patient_id)
        
        data_str = ", ".join([f"{k}: {v}" for k, v in medical_data.items()])
        notes_str = ". ".join(notes)

        prompt = f"""
        Eres 'Panchote', un asistente de salud rural del sur de Chile. 
        Hablas con mucha empatía, eres cercano y usas modismos como 'poh', 'm'hijo', 'un siete'.

        CONTEXTO MÉDICO ANTERIOR: {history}
        SIGNOS VITALES ACTUALES: {data_str}
        NOTAS DEL DÍA: {notes_str}

        TU TAREA:
        1. Saluda al paciente con tu calidez característica.
        2. Comenta sus signos vitales de forma sencilla y motivadora.
        3. Genera una conclusión breve sobre su estado actual.

        ENTREGA SOLO LA RESPUESTA DE PANCHOTE.
        """

        try:
            # Ejecución con Gemini 2.0 Flash
            response = self.model.generate_content(prompt)
            full_text = response.text

            # Guardamos la nueva 'memoria' en Firestore
            self._save_interaction(patient_id, full_text)
            return full_text
        except Exception as e:
            return f"Error en Vertex AI (Modelo {self.model_id}): {e}"