from core.ai_engine import BioTwinFirestoreEngine

def probar_memoria_panchote():
    print("\n" + "="*50)
    print("--- 🩺 PRUEBA DE INTEGRACIÓN: PANCHOTE + FIRESTORE ---")
    print("="*50)
    
    # ID de prueba que creamos en la consola de Firebase
    id_paciente = "angel_01" 
    
    # Datos simulados de un chequeo rápido
    datos = {"Presión": "118/75", "Glucosa": "90 mg/dL"}
    notas = ["Se siente con mucha energía hoy", "Dice que durmió 8 horas"]
    
    try:
        # Inicializamos el motor
        motor = BioTwinFirestoreEngine()
        
        print(f"🔍 Consultando ficha médica de: {id_paciente}...")
        
        # Llamamos a la función con los 3 argumentos (ID, Datos, Notas)
        resultado = motor.generate_clinical_summary(id_paciente, datos, notas)
        
        print("\n--- 🗣️ RESPUESTA DE PANCHOTE ---")
        print(resultado)
        print("\n" + "-"*50)
        print("✅ ÉXITO: Interacción procesada y guardada en Firestore.")
        print("-"*50 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LA AUDITORÍA TÉCNICA: {e}")

if __name__ == "__main__":
    probar_memoria_panchote()