import random

from faker import Faker

fake = Faker()
refresh_token = None

signup_data = {
    "username": fake.first_name(),
    "email": fake.email(),
    "password": fake.password(length=random.randint(8, 16))
    }


def test_sign_up(test_client):
    response = test_client.post("/auth/signup", json=signup_data)

    assert response.status_code == 201

    user_data = response.json()
    assert "id" in user_data
    assert "username" in user_data
    assert "email" in user_data

    signup_data.update({"id": user_data["id"]})


def test_sign_up_again(test_client):
    response = test_client.post("/auth/signup", json=signup_data)

    assert response.status_code == 409


def test_sign_in(test_client):
    response = test_client.post("/auth/login", data={
        "username": signup_data["email"],
        "password": signup_data["password"]
    })

    global refresh_token
    refresh_token = response.json()["refresh_token"]

    assert response.status_code == 200


def test_refresh_token(test_client):
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = test_client.get(f"/auth/refresh_token", headers=headers)

    assert response.status_code == 200

    user_data = response.json()
    assert "access_token" in user_data
    assert "refresh_token" in user_data
