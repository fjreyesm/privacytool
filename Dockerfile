# Usa una imagen oficial de Python como base.
FROM python:3.11-slim

# Establece variables de entorno recomendadas
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala Node.js para compilar el CSS de Tailwind
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# --- LÓGICA DE INSTALACIÓN SIMPLIFICADA ---
# Copia nuestro requirements.txt verificado
COPY requirements.txt .
# Instala las librerías desde ese archivo
RUN pip install --no-cache-dir -r requirements.txt
# --- FIN DE LA LÓGICA SIMPLIFICADA ---

# Copia los archivos de requerimientos de Node.js y los instala
COPY package*.json ./
RUN npm install

# Finalmente, copia el resto del código de tu aplicación al contenedor
COPY . .

# El puerto que tu aplicación usará
EXPOSE 8000