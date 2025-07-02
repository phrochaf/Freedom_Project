# Forcing a file update for Git
# -*- coding: utf-8 -*-
# ... (rest of the file)

def test_homepage(client):
    response = client.get('/')
    assert response.status_code == 200
    assert "página inicial do seu gestor de investimentos pessoal" in response.data.decode('utf-8')

def test_registration_and_login(client, db):
    # Test registration
    #1 Test Get
    response = client.get('/register')
    assert response.status_code == 200
    assert "Criar Nova Conta" in response.data.decode('utf-8')

    #2 Test Post
    response = client.post('/register', data={
        'username': 'testuser_2',
        'email': 'testuser_2@example.com',
        'password': 'testpassword',
        'confirm_password': 'testpassword',
    }, follow_redirects=True) #follow_redirects automatically follows the redirect after success

    assert response.status_code == 200
    assert "Registration successful!" in response.data.decode('utf-8')

    #3 Test Login
    response = client.post('/login', data={
        'username': 'testuser_2',
        'password': 'testpassword',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert "Meu Portfolio de Investimentos" in response.data.decode('utf-8')
    assert "Logged in successfully" in response.data.decode('utf-8')




