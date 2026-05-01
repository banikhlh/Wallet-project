from fastapi import status


def test_register_and_login(client):
    resp = client.post("/register", data={
        "username": "eva",
        "password": "secret123",
        "confirm_password": "secret123"
    })
    assert "alert-danger" not in resp.text

    resp = client.post("/login", data={"username": "eva", "password": "wrongpass"})
    assert "alert-danger" in resp.text

    resp = client.post("/login", data={"username": "eva", "password": "secret123"})
    assert "alert-danger" not in resp.text
    assert "access_token" in client.cookies


def test_dashboard_requires_auth(client):
    resp = client.get("/dashboard")
    assert resp.status_code == 401


def test_api_create_transaction(client):
    client.post("/register", data={
        "username": "frank",
        "password": "testpass",
        "confirm_password": "testpass"
    })
    client.post("/login", data={"username": "frank", "password": "testpass"})

    resp = client.get("/api/categories?type=expense")
    assert resp.status_code == 200
    categories = resp.json()
    assert len(categories) > 0
    cat_id = categories[0]["id"]

    resp = client.post("/api/transactions", data={
        "category_id": cat_id,
        "amount": 1500.50,
        "type": "expense",
        "description": "тест",
        "date": "2026-04-15"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] is not None
    assert "Транзакция добавлена" in data["message"]

    stats = client.get("/api/stats/summary?period=month")
    assert stats.status_code == 200
    summary = stats.json()
    assert summary["expense"] == 1500.50


def test_settings_change_username(client):
    client.post("/register", data={
        "username": "helen",
        "password": "123456",
        "confirm_password": "123456"
    })
    client.post("/login", data={"username": "helen", "password": "123456"})

    resp = client.post("/settings", data={
        "action": "change_username",
        "new_username": "helen2"
    })
    if resp.status_code == 303:
        assert resp.headers["location"] == "/logout"
    else:
        assert resp.status_code == 200
        assert "Имя занято" not in resp.text