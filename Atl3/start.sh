#!/bin/bash

echo "🚀 Démarrage du serveur Flask avec ngrok..."

# Démarrer Flask en arrière-plan
python app.py &
FLASK_PID=$!

# Attendre que Flask soit prêt
sleep 3

# Configurer ngrok avec le token si fourni
if [ ! -z "$NGROK_TOKEN" ]; then
    echo "🔑 Configuration du token ngrok..."
    ngrok config add-authtoken $NGROK_TOKEN
fi

# Démarrer ngrok et capturer l'URL
echo "🌐 Démarrage de ngrok..."
ngrok http 5000 --log=stdout &
NGROK_PID=$!

# Attendre que ngrok soit prêt
sleep 5

# Obtenir l'URL publique de ngrok
NGROK_URL=$(curl -s localhost:4040/api/tunnels | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tunnels = data.get('tunnels', [])
    for tunnel in tunnels:
        if tunnel.get('proto') == 'https':
            print(tunnel['public_url'])
            break
except:
    print('URL non disponible')
")

echo ""
echo "✅ SERVEUR FLASK ACCESSIBLE À L'ADRESSE :"
echo "🔗 $NGROK_URL"
echo ""
echo "📊 Dashboard ngrok : http://localhost:4040"
echo "⏰ Le serveur sera accessible pendant 120 secondes..."
echo ""

# Afficher les logs pendant 120 secondes
timeout 120 tail -f /dev/null

echo ""
echo "⏰ Temps écoulé - Arrêt du serveur..."

# Nettoyer les processus
kill $FLASK_PID 2>/dev/null
kill $NGROK_PID 2>/dev/null

echo "🛑 Serveur arrêté"
