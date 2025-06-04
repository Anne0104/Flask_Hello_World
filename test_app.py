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
