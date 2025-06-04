name: Docker + ngrok + Tests pytest
on: 
  push:
    branches: [ main, master ]

jobs:
  deploy-and-test:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install pytest dependencies ONLY
      run: |
        pip install pytest==7.4.0 requests==2.31.0
        
    - name: Build Docker image
      run: |
        docker build -t flask-app .
        
    - name: Deploy et récupérer URL
      run: |
        # Installer ngrok - CORRECTION ICI
        curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
        echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
        sudo apt update && sudo apt install ngrok
        
        # Configurer le token
        ngrok config add-authtoken ${{ secrets.NGROK_AUTHTOKEN }}
        
        # Lancer l'app Flask
        docker run -d -p 5000:5000 --name flask-container flask-app
        sleep 10
        
        # Vérifier que l'app Flask répond localement
        echo "🔍 Test local de l'app Flask..."
        curl -f http://localhost:5000/ || (echo "❌ App Flask ne répond pas localement" && docker logs flask-container && exit 1)
        echo "✅ App Flask répond localement"
        
        # Lancer ngrok
        ngrok http 5000 --log=stdout > /tmp/ngrok.log 2>&1 &
        sleep 25
        
        # Récupérer l'URL avec plusieurs tentatives
        for i in {1..5}; do
          NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*https[^"]*' | cut -d'"' -f4 | head -1)
          if [ -n "$NGROK_URL" ]; then
            break
          fi
          echo "Tentative $i/5 pour récupérer l'URL..."
          sleep 5
        done
        
        if [ -n "$NGROK_URL" ]; then
          echo "🌐 Application accessible sur : $NGROK_URL"
          
          # Test de connectivité ngrok
          echo "🔍 Test de connectivité ngrok..."
          for i in {1..3}; do
            if curl -f -s "$NGROK_URL/" > /dev/null; then
              echo "✅ ngrok tunnel OK"
              echo "NGROK_URL=$NGROK_URL" >> $GITHUB_ENV
              break
            else
              echo "Tentative $i/3 de connexion ngrok..."
              sleep 10
            fi
          done
          
          if [ -z "$(curl -s "$NGROK_URL/" || echo '')" ]; then
            echo "❌ ngrok tunnel ne répond pas"
            exit 1
          fi
          
        else
          echo "❌ Pas d'URL trouvée"
          cat /tmp/ngrok.log
          exit 1
        fi
        
    - name: Run pytest tests
      env:
        NGROK_URL: ${{ env.NGROK_URL }}
      run: |
        echo "🧪 === TESTS PYTEST ==="
        echo "URL testée : $NGROK_URL"
        
        # Lancer pytest depuis un dossier séparé pour éviter l'import de __init__.py
        mkdir /tmp/tests
        cp test_app.py /tmp/tests/
        cp conftest.py /tmp/tests/
        cd /tmp/tests
        
        pytest test_app.py -v --tb=short -s
... (12lignes restantes)
Réduire
docker-ngrok.yml
4 Ko
FROM python:3.9-slim

WORKDIR /Flask_Hello_World

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "__init__.py"]
Réduire
Dockerfile.txt
1 Ko
Flask==2.3.3
pytest==7.4.0
requests==2.31.0
requirements.txt
1 Ko
import pytest
import requests
import os

def test_routes_status_code():
    """Test que toutes les routes retournent un code 200"""
    
    ngrok_url = os.environ.get('NGROK_URL', '').rstrip('/')
    if not ngrok_url:
        pytest.fail("NGROK_URL non définie")
    
    routes_to_test = [
        "/",
        "/exercices/", 
        "/contact/",
        "/calcul_carre/5",
        "/somme/10/15"
    ]
    
    print(f"🧪 Testing URL: {ngrok_url}")
    
    for route in routes_to_test:
        url = f"{ngrok_url}{route}"
        print(f"Testing: {url}")
        
        try:
            response = requests.get(url, timeout=15)
            print(f"Response: {response.status_code}")
            assert response.status_code == 200, f"Route {route} returned {response.status_code}"
            print(f"✅ {route} → 200 OK")
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error on {route}: {e}")
            pytest.fail(f"Connection failed for {route}: {e}")

def test_content_verification():
    """Test que le contenu attendu est présent"""
    
    ngrok_url = os.environ.get('NGROK_URL', '').rstrip('/')
    if not ngrok_url:
        pytest.fail("NGROK_URL non définie")
    
    try:
        # Test page d'accueil
        response = requests.get(f"{ngrok_url}/", timeout=15)
        assert response.status_code == 200
        assert "Bonjour tout le monde" in response.text
        print("✅ Page d'accueil OK")
        
        # Test calcul carré
        response = requests.get(f"{ngrok_url}/calcul_carre/5", timeout=15)
        assert response.status_code == 200
        assert "25" in response.text
        print("✅ Calcul carré OK")
        
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Content test failed: {e}")
Réduire
test_app.py
2 Ko
+ Créer un Token Ngork
﻿
import pytest
import requests
import os

def test_routes_status_code():
    """Test que toutes les routes retournent un code 200"""
    
    ngrok_url = os.environ.get('NGROK_URL', '').rstrip('/')
    if not ngrok_url:
        pytest.fail("NGROK_URL non définie")
    
    routes_to_test = [
        "/",
        "/exercices/", 
        "/contact/",
        "/calcul_carre/5",
        "/somme/10/15"
    ]
    
    print(f"🧪 Testing URL: {ngrok_url}")
    
    for route in routes_to_test:
        url = f"{ngrok_url}{route}"
        print(f"Testing: {url}")
        
        try:
            response = requests.get(url, timeout=15)
            print(f"Response: {response.status_code}")
            assert response.status_code == 200, f"Route {route} returned {response.status_code}"
            print(f"✅ {route} → 200 OK")
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error on {route}: {e}")
            pytest.fail(f"Connection failed for {route}: {e}")

def test_content_verification():
    """Test que le contenu attendu est présent"""
    
    ngrok_url = os.environ.get('NGROK_URL', '').rstrip('/')
    if not ngrok_url:
        pytest.fail("NGROK_URL non définie")
    
    try:
        # Test page d'accueil
        response = requests.get(f"{ngrok_url}/", timeout=15)
        assert response.status_code == 200
        assert "Bonjour tout le monde" in response.text
        print("✅ Page d'accueil OK")
        
        # Test calcul carré
        response = requests.get(f"{ngrok_url}/calcul_carre/5", timeout=15)
        assert response.status_code == 200
        assert "25" in response.text
        print("✅ Calcul carré OK")
        
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Content test failed: {e}")
