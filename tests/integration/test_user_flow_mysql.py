import os


def test_register_and_activate_user_mysql(client):
    response = client.post(
        "/users/register",
        json={
            "email": "mysql@test.com",
            "password": "StrongPassword123",
        },
    )

    assert response.status_code == 201
    assert response.json()["message"] == "User created. Activation code sent."

    import pymysql
    from hashlib import sha256
    from datetime import datetime, timedelta, timezone

    conn = pymysql.connect(
        host="localhost",
        port=int(os.environ["MYSQL_PORT"]),
        user="test",
        password="test",
        database="test_db",
    )

    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT id FROM users WHERE email=%s",
            ("mysql@test.com",),
        )
        user_id = cursor.fetchone()[0]

        code = "1234"
        cursor.execute(
            """
            UPDATE activation_codes
            SET hashed_code=%s, expires_at=%s
            WHERE user_id=%s
            """,
            (
                sha256(code.encode()).hexdigest(),
                datetime.now(tz=timezone.utc) + timedelta(minutes=1),
                user_id,
            ),
        )

    conn.commit()
    conn.close()

    response = client.post(
        "/activation",
        json={"code": code},
        auth=("mysql@test.com", "StrongPassword123"),
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Account successfully activated."
