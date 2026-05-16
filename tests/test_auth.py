from fastapi.testclient import TestClient

def test_register_user(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.data if hasattr(response, 'data') else response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"

def test_login_user(client: TestClient):
    # First register
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "password123",
            "full_name": "Login User"
        }
    )
    
    # Then login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "detail" in response.json()

def test_register_duplicate_email(client: TestClient):
    payload = {
        "email": "duplicate@example.com",
        "password": "password123",
        "full_name": "Duplicate User"
    }
    # First time
    client.post("/api/v1/auth/register", json=payload)
    
    # Second time
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]

def test_register_admin_forbidden(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "hacker@example.com",
            "password": "password123",
            "full_name": "Hacker",
            "role": "admin"
        }
    )
    assert response.status_code == 403
    assert "administrator" in response.json()["detail"].lower()
