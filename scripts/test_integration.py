#!/usr/bin/env python3
"""
Script de integración para probar BioTwin AI.
Genera datos ficticios, inserta paciente, procesa biomarcadores y verifica.
"""

from api.supabase_config import SupabaseManager
from core.analysis import BioTwinEngine


def main():
    # Inicializar SupabaseManager
    try:
        manager = SupabaseManager()
    except Exception as e:
        print(f"Error al inicializar SupabaseManager: {e}")
        return

    # 1. Generar datos ficticios de paciente
    nombre = "Juan Pérez"
    rut = "12345678-9"
    edad = 45
    genero = "masculino"

    print("Insertando paciente ficticio...")
    try:
        paciente = manager.insert_patient(nombre, rut, edad, genero)
        paciente_id = paciente["id_anonimo"]
        print(f"Paciente insertado con ID: {paciente_id}")
    except Exception as e:
        print(f"Error al insertar paciente: {e}")
        return

    # 2. Simular entrada de biomarcadores
    glucosa = 130.0  # mg/dL
    presion_sistolica = 120.0  # mmHg
    presion_diastolica = 80.0   # mmHg

    print("Calculando Health Score...")
    data = {
        "glucosa": glucosa,
        "presion_sistolica": presion_sistolica,
        "presion_diastolica": presion_diastolica
    }
    score = BioTwinEngine.compute_score(data)
    recomendacion = BioTwinEngine.recommendation(score)
    print(f"Health Score: {score}, Recomendación: {recomendacion}")

    # 3. Guardar biomarcadores
    print("Guardando biomarcadores...")
    try:
        manager.insert_biomarker(paciente_id, "glucosa", glucosa, "mg/dL")
        manager.insert_biomarker(paciente_id, "presion_sistolica", presion_sistolica, "mmHg")
        manager.insert_biomarker(paciente_id, "presion_diastolica", presion_diastolica, "mmHg")
        print("Biomarcadores guardados.")
    except Exception as e:
        print(f"Error al guardar biomarcadores: {e}")
        return

    # 4. Verificar que los datos llegaron a la base de datos
    print("Verificando datos en la base de datos...")
    try:
        biomarkers = manager.query_patient_biomarkers(paciente_id)
        if len(biomarkers) >= 3:  # Al menos glucosa, sistolica, diastolica
            print("ÉXITO: Los datos se guardaron correctamente en la base de datos.")
        else:
            print(f"Error: Solo se encontraron {len(biomarkers)} biomarcadores.")
    except Exception as e:
        print(f"Error al verificar datos: {e}")


if __name__ == "__main__":
    main()