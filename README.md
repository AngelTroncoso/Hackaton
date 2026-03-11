# 🧬 BioTwin AI: El Gemelo Digital para la Medicina de Precisión

**BioTwin AI** es un ecosistema dinámico de salud que transforma el historial médico estático en un "Gemelo Digital" interactivo. No es solo un chatbot; es un agente inteligente que integra datos genéticos, biológicos y corporales para democratizar el acceso a recomendaciones médicas personalizadas.

---

## 💡 Inspiración
La inspiración nació de visualizar un futuro donde el historial médico no sea un archivo muerto, sino un ecosistema vivo. BioTwin AI busca ser el puente hacia la medicina de precisión, permitiendo que cada paciente tenga un reflejo virtual de su salud que evoluciona en tiempo real, basándose en su individualidad biológica única.

## 🚀 ¿Qué hace?
* **Integración Multimodal:** Consolida exámenes, tratamientos y antecedentes históricos en una única línea de tiempo.
* **Análisis con Modelos de Salud:** Utiliza la potencia de **Gemini** y modelos especializados para identificar patrones biológicos que pasan desapercibidos.
* **Predicción y Recomendación:** Genera proyecciones de salud futuras y sugiere ajustes en tratamientos, siempre bajo un enfoque de validación profesional médica.
* **Interfaz de Acompañamiento:** Implementa a "Panchote", una capa de empatía basada en lenguaje natural que traduce la complejidad técnica en consejos cercanos y comprensibles con un tono cálido y regional.

---

## 🛠️ Stack Tecnológico
* **Core AI:** Google Gemini 2.5/3.1 (via `google-genai`) para razonamiento clínico avanzado.
* **Backend & Memoria:** **Supabase** (PostgreSQL) para la persistencia del estado del Gemelo Digital.
* **Lenguaje:** Python 3.12.
* **Metodología:** Vibe Coding & Agentic Workflow.

---

## 🏗️ Arquitectura del Agente
El sistema opera bajo un flujo de **Recuperación-Generación-Almacenamiento**:

1.  **Context Retrieval:** El motor consulta en Supabase el último resumen histórico del paciente mediante su `patient_id`.
2.  **Prompt Engineering:** Se construye un prompt dinámico que combina el historial ("Memoria") con los nuevos biomarcadores.
3.  **Inference:** Gemini procesa la información manteniendo la personalidad de "Panchote" y la precisión del Gemelo Digital.
4.  **Memory Update:** El nuevo resumen generado se almacena automáticamente para dar continuidad evolutiva a la salud del paciente.

---

### ☁️ Google Cloud Integration (Firebase)
Para cumplir con los estándares de escalabilidad y hosting exigidos, **BioTwin AI** utiliza:
* **Firebase Hosting:** Para el despliegue de la interfaz multimodal.
* **Cloud Functions (GCP):** Para orquestar la lógica de negocio y la conexión con Supabase.
* **Vertex AI Firebase SDK:** Para la implementación de la API Gemini Live, permitiendo interacciones de voz y visión en tiempo real con latencia mínima.
---

## 🕹️ Guía de Ejecución (Demo en Vivo)

Para validar la arquitectura de **BioTwin AI** y su capacidad de memoria persistente, sigue estos pasos:
---

### 1. Preparación del Entorno
Instala las dependencias necesarias:
```bash
python3 -m pip install google-genai supabase python-dotenv
---

### 2. Configuración de Variables (.env)
Para que el motor pueda auditar la base de datos y conectar con la IA, asegúrate de tener tus llaves configuradas en el archivo `.env`:

```env
GOOGLE_API_KEY="tu_api_key_de_google"
SUPABASE_URL="[https://tu-proyecto.supabase.co](https://tu-proyecto.supabase.co)"
SUPABASE_KEY="tu-anon-key-de-supabase"

---

### 3. Ejecución de la Prueba
Lanza el script de prueba para iniciar la interacción con el Gemelo Digital:
python3 test_panchote.py
---

### Qué observar en la Demo
Interacción Inicial: El sistema detectará que no hay historial previo y generará un perfil clínico base desde cero.

Persistencia: Verás en tiempo real la creación del registro en la tabla medical_history de Supabase.

Continuidad (Memoria): Al ejecutar el comando por segunda vez, el agente recuperará el contexto anterior, demostrando que BioTwin AI reconoce la evolución del paciente y ajusta sus consejos dinámicamente.
---

### Desafíos Superados & Logros
Equilibrio Técnico-Humano: Logramos integrar la precisión de un Gemelo Digital con la calidez de un acompañante de salud regional.

Optimización de Tokens: Implementamos el uso de resúmenes contextuales en lugar de historiales densos, garantizando rapidez y bajo costo operativo.

Trazabilidad de Datos: Arquitectura diseñada bajo estándares de auditoría clínica profesional, permitiendo un seguimiento real y seguro de la salud del paciente.
---

👨‍💻 Autor
Angel Troncoso Contador Auditor | Ingeniero Comercial | Desarrollador de Ecosistemas IA

Este proyecto fue desarrollado para el Gemini Live Agent Challenge 2026.