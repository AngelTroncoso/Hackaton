# Usamos una imagen ligera de Python
FROM python:3.12-slim

# Directorio de trabajo
WORKDIR /app

# Copiar archivos necesarios
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código y la llave (OJO: en prod se usan secretos, pero para la hackatón esto sirve)
COPY . .

# Puerto que usa Streamlit por defecto
EXPOSE 8080

# Comando para ejecutar la app (el flag de server port es vital para Cloud Run)
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]