# <h1 align="center">Panchote Multimodal</h1>
![Panchote](https://image.lexica.art/full_webp/00007a82-c490-4a9f-9b09-038ea8163158)

**Categoria:** Agentes en Vivo  
**Ubicacion:** Santiago, Chile  
**Tecnologia Core:** Gemini en Vertex AI + Firestore + ElevenLabs + Streamlit

---

## Descripcion del Proyecto

**Panchote Multimodal** es una experiencia de salud conversacional creada para hackathon. Combina voz, imagen y contexto clinico basico para entregar recomendaciones breves, cercanas y comprensibles sobre alimentos cotidianos.

La aplicacion usa a **Panchote**, un lobo marino sabio de Puerto Montt, como interfaz empatica para traducir senales de salud en consejos simples con tono local. El foco no es reemplazar criterio medico, sino demostrar una forma mas humana, accesible y memorable de interactuar con IA multimodal.

## El Problema

Pacientes con condiciones cronicas como diabetes o hipertension muchas veces no tienen una forma simple e inmediata de validar si una comida cotidiana es compatible con su estado de salud. Eso genera dudas, ansiedad y errores evitables en la alimentacion.

## La Solucion

Panchote recibe una consulta por voz o una imagen del plato, cruza esa informacion con biomarcadores del paciente almacenados en Firestore y genera una recomendacion corta usando Gemini. Si ElevenLabs esta configurado, la respuesta tambien se reproduce con voz personalizada.

## Que Hace

- Recibe una consulta por voz desde Streamlit.
- Recibe una foto del plato por camara o carga manual.
- Recupera datos de salud base desde Firestore.
- Consulta un modelo multimodal de Gemini en Vertex AI.
- Responde en texto breve y, si ElevenLabs esta configurado, tambien en voz.
- Incluye un panel de diagnostico para validar la integracion de TTS en vivo.

## Demo Flow

1. El usuario graba audio o sube una imagen de su comida.
2. Panchote incorpora glucosa y presion del paciente desde Firestore.
3. Gemini analiza el contexto y entrega una recomendacion corta.
4. ElevenLabs convierte la respuesta a audio con una voz personalizada.
5. La interfaz muestra texto, imagen capturada y estado tecnico del sistema.

## Arquitectura del Sistema

- **Frontend/App:** Streamlit
- **Modelo multimodal:** Google Gemini via `google-genai`
- **Plataforma de inferencia:** Vertex AI
- **Memoria de salud:** Google Cloud Firestore
- **Sintesis de voz:** ElevenLabs
- **Lenguaje:** Python 3.12
- **Contenerizacion:** Docker

## Arquitectura de Flujo

1. **Input multimodal**  
   Streamlit recibe audio e imagen del usuario.

2. **Contexto clinico**  
   La app consulta Firestore para recuperar biomarcadores basicos del paciente.

3. **Razonamiento**  
   Gemini genera una respuesta breve, contextual y con personalidad.

4. **Voz**  
   ElevenLabs sintetiza la salida con una voz configurada por `voice_id`.

5. **Observabilidad**  
   La app muestra errores de TTS y un bloque de diagnostico para la demo.

## Estructura Relevante

- `core/app.py`: app principal de Streamlit
- `Dockerfile`: contenedor listo para ejecutar `core/app.py`
- `requirements.txt`: dependencias del proyecto
- `.env`: variables de entorno locales

## Variables de Entorno

Configura un archivo `.env` con valores como estos:

```env
PROJECT_ID=multiagentes-479321
LOCATION=us-west1
MODEL_ID=gemini-2.5-flash
ELEVEN_LABS_API_KEY=tu_api_key
ELEVEN_VOICE_ID=tu_voice_id
```

Notas:

- `MODEL_ID` debe corresponder a un modelo habilitado en Vertex AI para tu proyecto y region.
- `ELEVEN_VOICE_ID` debe ser una voz valida y permitida por tu cuenta de ElevenLabs.
- Firestore y Vertex AI requieren credenciales correctamente disponibles en el entorno.

## Ejecucion Local

Instala dependencias:

```bash
python3 -m pip install -r requirements.txt
```

Levanta la app:

```bash
streamlit run core/app.py
```

## Despliegue

El proyecto esta preparado para contenedorizarse con Docker. El `Dockerfile` arranca correctamente la app desde `core/app.py`, alineado con la estructura actual del repositorio.

## Logros Tecnicos de la Demo

- Integracion real entre Streamlit, Vertex AI, Firestore y ElevenLabs.
- Correccion de un modelo retirado de Gemini hacia una version vigente y configurable.
- Estabilizacion del flujo de captura de imagen con respaldo por carga manual.
- Diagnostico visible de TTS para aislar errores de voz, credenciales o plan.
- Voz personalizada de Panchote validada con ElevenLabs.

## Hallazgos y Aprendizajes

- La multimodalidad mejora mucho la experiencia cuando se combina con contexto clinico simple y lenguaje cercano.
- La observabilidad en demo importa tanto como la funcionalidad: el diagnostico de TTS permitio aislar rapido errores de `voice_id` y restricciones de plan.
- Una personalidad local bien definida aumenta cercania sin sacrificar claridad tecnica.

## Consideraciones

- Esta demo esta orientada a evaluacion de hackathon y validacion tecnica de producto.
- Las respuestas son de apoyo y no sustituyen evaluacion medica profesional.
- El tono cercano de Panchote es intencional: busca hacer la IA mas accesible y humana.

## Autor

**Angel Troncoso**  
Contador Auditor | Ingeniero Comercial | Desarrollador de Ecosistemas IA

Proyecto desarrollado para presentacion de hackathon con enfoque en IA multimodal aplicada a salud y experiencia de usuario.
