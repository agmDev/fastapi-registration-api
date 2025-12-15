def test_register_and_activate_user_mysql(client):
    email = "mysql@test.com"
    password = "StrongPassword123"

    response = client.post(
        "/users/register",
        json={"email": email, "password": password},
    )
    assert response.status_code == 201

    response = client.post(
        "/activation",
        json={"code": "1234"},
        auth=(email, password),
    )

    assert response.status_code == 200
