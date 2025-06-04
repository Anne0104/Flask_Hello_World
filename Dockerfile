# Utiliser une image Python officielle comme base
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Installer ngrok
RUN apt-get update && \
    apt-get install -y wget unzip && \
    wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz && \
    tar -xzf ngrok-v3-stable-linux-amd64.tgz && \
    mv ngrok /usr/local/bin/ && \
    rm ngrok-v3-stable-linux-amd64.tgz && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copier le code de l'application
COPY . .

# Exposer le port Flask
EXPOSE 5000

# Script de démarrage
COPY start.sh .
RUN chmod +x start.sh

# Commande par défaut
CMD ["./start.sh"]
