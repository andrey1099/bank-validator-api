# Imagen base: Python 3.11 en su version slim
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Primero las dependencias, para aprovechar el cache de capas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Despues el codigo de la aplicacion
COPY app/ ./app/

# Puerto que expone la aplicacion
EXPOSE 8000

# Comando que arranca el contenedor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]