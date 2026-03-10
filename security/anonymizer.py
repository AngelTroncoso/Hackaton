import hashlib
import re
from datetime import datetime


class Anonymizer:
    """Clase para anonimizar datos sensibles de pacientes.

    - Hash SHA-256 con sal para nombres y RUTs.
    - Fechas de nacimiento limitadas al año.
    - Verificación si un valor ya está anonimizado.
    """

    SALT = "BioTwinSalt2026"  # valor de sal constante, en producción debería mantenerse aparte
    HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")

    @classmethod
    def _hash_value(cls, value: str) -> str:
        hasher = hashlib.sha256()
        hasher.update(cls.SALT.encode("utf-8"))
        hasher.update(value.encode("utf-8"))
        return hasher.hexdigest()

    @classmethod
    def anonymize_name(cls, name: str) -> str:
        if cls.is_anonymized(name):
            return name
        return cls._hash_value(name.lower().strip())

    @classmethod
    def anonymize_rut(cls, rut: str) -> str:
        # Limpia formatos comunes como puntos y guion
        cleaned = re.sub(r"[^0-9kK]", "", rut)
        if cls.is_anonymized(cleaned):
            return cleaned
        return cls._hash_value(cleaned)

    @classmethod
    def anonymize_birthdate(cls, birthdate: str) -> str:
        # espera formato YYYY-MM-DD o variantes ISO
        try:
            dt = datetime.fromisoformat(birthdate)
        except ValueError:
            raise ValueError("Fecha de nacimiento no tiene formato ISO válido")
        return str(dt.year)

    @classmethod
    def is_anonymized(cls, value: str) -> bool:
        """Detecta si un valor ya parece un hash SHA-256.
        Esto ayuda a evitar doble anonimización.
        """
        return bool(cls.HASH_PATTERN.fullmatch(value))
