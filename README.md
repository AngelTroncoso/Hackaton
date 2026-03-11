# 🤠 BioTwin AI – El Consejo de Panchote

**Categoría:** Agentes en Vivo (Live Agent Challenge)  
**Ubicación:** Santiago, Chile  
**Tecnología Core:** Gemini 2.0 Flash 001 + Google Cloud Vertex AI + Firestore

---

## 📝 Descripción del Proyecto

BioTwin AI es un agente de salud preventivo que actúa como un "Digital Twin" del usuario. Utilizando capacidades multimodales nativas, el agente "Panchote" (un asistente con identidad rural chilena, sabio y cercano) analiza imágenes de platos de comida en tiempo real y cruza esa información con la ficha médica del paciente almacenada en Google Cloud Firestore.

### El Problema

Pacientes con enfermedades crónicas (diabetes, hipertensión) a menudo no saben si un plato específico es seguro para su condición en un momento dado, lo que genera ansiedad o errores en la dieta.

### La Solución

Panchote identifica ingredientes, estima riesgos nutricionales y entrega un consejo personalizado con modismos chilenos, humanizando la tecnología y mejorando la adherencia al autocuidado mediante una interfaz sencilla y amigable.

---

## 🏗️ Arquitectura del Sistema

El proyecto está construido íntegramente sobre el ecosistema de Google Cloud:

- **IA Multimodal:** Gemini 2.0 Flash 001 (Vertex AI) para razonamiento visual y de lenguaje de baja latencia
- **Base de Datos:** Firestore para almacenamiento de medical_history y persistencia de daily_logs
- **Frontend/Backend:** Streamlit (Python) para una interacción rápida y fluida
- **Infraestructura:** Docker para asegurar la portabilidad y despliegue en Google Cloud Run

---

## 🚀 Instrucciones de Inicio Rápido (Spin-up)

### 1. Requisitos Previos

- Cuenta de Google Cloud con un Proyecto Activo
- APIs habilitadas: Vertex AI API y Cloud Firestore API
- Archivo de credenciales `firebase_key.json` en la raíz del proyecto

### 2. Instalación Local

```bash
# Instalar dependencias necesarias
pip install -r requirements.txt

# Ejecutar la aplicación web
streamlit run app.py
```

### 3. Automatización con Docker (Puntos Extra)

Para el despliegue en la nube, el proyecto incluye un Dockerfile que empaqueta la aplicación de forma reproducible:

```dockerfile
# Usamos una imagen ligera de Python 3.12
FROM python:3.12-slim

# Directorio de trabajo
WORKDIR /app

# Instalación de dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia del código fuente y credenciales
COPY . .

# Puerto para Cloud Run
EXPOSE 8080

# Comando de inicio
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
```

---

## 🛠️ Stack Tecnológico

- **Lenguaje:** Python 3.12
- **SDK:** google-cloud-aiplatform, google-cloud-firestore
- **Modelos:** gemini-2.0-flash-001
- **UI Framework:** Streamlit
- **DevOps:** Docker, Google Cloud Run

---

## 👨‍💻 Hallazgos y Aprendizajes

### Latencia Multimodal
El modelo gemini-2.0-flash-001 procesa imágenes (.jpg, .png) con una velocidad asombrosa, permitiendo una experiencia "en vivo" real para el usuario.

### Identidad del Agente
La técnica de System Instruction permitió que Panchote mantuviera un tono culturalmente relevante (chileno), lo que genera mayor confianza y cercanía.

### Integración de Datos
La conexión directa con Firestore permite que el agente tenga "memoria" del estado de salud del usuario, permitiendo una personalización real sin necesidad de re-introducir datos.

---

## 📹 Estructura del Video de Demostración (4 min)

- **0:00 - 0:45:** Pitch - Presentación de BioTwin AI y el impacto en la salud preventiva
- **0:45 - 2:30:** Demo en Vivo - Interacción con la interfaz subiendo fotos de comida y respuesta de Panchote
- **2:30 - 3:30:** Backstage Cloud - Muestra de los registros en Firestore y configuración en la consola de Google Cloud
- **3:30 - 4:00:** Cierre - Resumen técnico, escalabilidad y visión de futuro del proyecto

---

## 📋 Información del Proyecto

**Desarrollado por:** Angel Troncoso  
**Proyecto:** BioTwin AI - Reto Gemini Live Agent 2026