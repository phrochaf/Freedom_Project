def test_registration_and_login(client, db):
    """Test the full registration and login flow."""
    # 1. Test GET request to registration page
    response = client.get('/register')
    assert response.status_code == 200
    assert "Criar Nova Conta" in response.data.decode('utf-8')

    # 2. Test successful registration
    response = client.post('/register', data={
        'username': 'testuser_2',
        'email': 'testuser_2@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert "Registration successful!" in response.data.decode('utf-8')

    # 3. Test successful login
    response = client.post('/login', data={
        'username': 'testuser_2',
        'password': 'password123'
    }, follow_redirects=True)

    # 4. Assert the state of the page AFTER login
    assert response.status_code == 200
    # The portfolio page should contain the flash message from the login
    assert "Login realizado com sucesso!" in response.data.decode('utf-8')
    # And it should contain the "empty portfolio" message, since no operations were added
    assert "Seu portfólio está vazio" in response.data.decode('utf-8')

