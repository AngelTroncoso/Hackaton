import os
from typing import Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
from security.anonymizer import Anonymizer


class SupabaseManager:
    """Gestor de conexión y operaciones con Supabase para BioTwin AI."""

    def __init__(self):
        """Inicializa el cliente de Supabase cargando variables desde .env."""
        load_dotenv()  # Carga variables de entorno desde .env
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")

        if not self.url or not self.key:
            raise ValueError(
                "Variables SUPABASE_URL y SUPABASE_KEY no están configuradas en .env"
            )

        try:
            self.client: Client = create_client(self.url, self.key)
        except Exception as e:
            raise RuntimeError(f"Error al conectar con Supabase: {e}")

    def insert_patient(self, nombre: str, rut: str, edad: int, genero: str) -> Dict:
        """Inserta un nuevo paciente anonimizado.

        Args:
            nombre: Nombre del paciente (se anonimiza).
            rut: RUT del paciente (se anonimiza y usa como id_anonimo).
            edad: Edad del paciente (int).
            genero: Género ('masculino', 'femenino', 'otro', 'no informado').

        Returns:
            Dict con los datos del paciente insertado.

        Raises:
            ValueError: Si los datos son inválidos.
            RuntimeError: Si falla la inserción en BD.
        """
        try:
            # Anonimizar datos sensibles
            id_anonimo = Anonymizer.anonymize_rut(rut)
            # Nota: nombre se anonimiza pero no se guarda en la tabla actual

            genero_validos = {"masculino", "femenino", "otro", "no informado"}
            if genero not in genero_validos:
                raise ValueError(f"Género '{genero}' no es válido")
            if not isinstance(edad, int) or edad < 0:
                raise ValueError("Edad debe ser un entero no negativo")

            # Insertar con id_anonimo como hash del RUT (ajuste al esquema)
            response = self.client.table("pacientes").insert(
                {"id_anonimo": id_anonimo, "edad": edad, "genero": genero}
            ).execute()
            return response.data[0] if response.data else {}
        except ValueError as ve:
            raise ve
        except Exception as e:
            raise RuntimeError(f"Error al insertar paciente: {e}")

    def insert_biomarker(
        self, paciente_id: str, tipo: str, valor: float, unidad: str
    ) -> Dict:
        """Sube un biomarcador procesado para un paciente.

        Args:
            paciente_id: ID anonimizado del paciente.
            tipo: Tipo de biomarcador ('glucosa', 'presion_sistolica', etc).
            valor: Valor numérico del biomarcador.
            unidad: Unidad de medida ('mg/dL', 'mmHg', etc).

        Returns:
            Dict con el biomarcador insertado.

        Raises:
            ValueError: Si los datos son inválidos.
            RuntimeError: Si falla la inserción en BD.
        """
        try:
            if not isinstance(valor, (int, float)) or valor < 0:
                raise ValueError("Valor debe ser un número no negativo")
            if not tipo or not unidad:
                raise ValueError("Tipo y unidad son requeridos")

            response = self.client.table("biomarcadores").insert(
                {
                    "paciente_id": paciente_id,
                    "tipo": tipo,
                    "valor": valor,
                    "unidad": unidad,
                    "fecha_registro": datetime.utcnow().isoformat(),
                }
            ).execute()
            return response.data[0] if response.data else {}
        except ValueError as ve:
            raise ve
        except Exception as e:
            raise RuntimeError(f"Error al insertar biomarcador: {e}")

    def query_patient_biomarkers(self, paciente_id: str) -> list:
        """Obtiene todos los biomarcadores de un paciente.

        Args:
            paciente_id: ID anonimizado del paciente.

        Returns:
            Lista de biomarcadores del paciente.

        Raises:
            RuntimeError: Si falla la consulta.
        """
        try:
            response = (
                self.client.table("biomarcadores")
                .select("*")
                .eq("paciente_id", paciente_id)
                .execute()
            )
            return response.data if response.data else []
        except Exception as e:
            raise RuntimeError(f"Error al obtener biomarcadores: {e}")
