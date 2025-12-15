def test_activate_account_ok(client, users_service_mock):
    response = client.post(
        "/activation",
        json={"code": "1234"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Account successfully activated."

    users_service_mock.activate.assert_awaited_once_with(
        42,
        "1234",
    )
