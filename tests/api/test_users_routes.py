def test_register_user_ok(client, users_service_mock):
    users_service_mock.register.return_value = 1

    response = client.post(
        "/users/register",
        json={
            "email": "test@example.com",
            "password": "StrongPassword123",
        },
    )

    assert response.status_code == 201
    assert response.json()["message"] == "User created. Activation code sent."

    users_service_mock.register.assert_awaited_once_with(
        email="test@example.com",
        password="StrongPassword123",
    )

    def test_register_user_already_exists(client, users_service_mock):
        users_service_mock.register.side_effect = ValueError("USER_ALREADY_EXISTS")

        response = client.post(
            "/users/register",
            json={
                "email": "test@example.com",
                "password": "StrongPassword123",
            },
        )

        assert response.status_code == 409
        assert response.json()["detail"] == "User already exists"
