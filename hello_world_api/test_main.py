import json

import pytest
from fastapi.testclient import TestClient

from hello_world_api import main
from hello_world_api.main import Customer


SAMPLE_CUSTOMERS = [
    {
        "id": "dcb833f3-5ac9-4404-aaf5-1412f9da065b",
        "name": "Leo Decaprio",
        "address": "123 Smith St",
        "city": "Los Angeles",
        "state": "CA",
        "zip": "90210",
        "phone": "805-123-4567",
        "email": "kingoftheworld@yahoo.com",
        "hobbies": ["hunting", "biking", "bee keeping"],
    },
    {
        "id": "07eb08b9-421d-4af1-a026-5da336f585d5",
        "name": "Maya Chen",
        "address": "482 Oak Avenue",
        "city": "Seattle",
        "state": "WA",
        "zip": "98101",
        "phone": "206-555-0142",
        "email": "maya.chen@outlook.com",
        "hobbies": ["photography", "hiking", "cooking"],
    },
    {
        "id": "206f93cc-6a74-4ac7-b97b-b9a9f34e0668",
        "name": "Andre Williams",
        "address": "19 Pine Court",
        "city": "Atlanta",
        "state": "GA",
        "zip": "30303",
        "phone": "404-555-0198",
        "email": "andre.williams@gmail.com",
        "hobbies": ["basketball", "grilling", "jazz"],
    },
]

NEW_CUSTOMER = {
    "name": "Riley Thompson",
    "address": "6 Cedar Ridge",
    "city": "Boulder",
    "state": "CO",
    "zip": "80302",
    "phone": "720-555-0144",
    "email": "riley.thompson@icloud.com",
    "hobbies": ["climbing", "trail running"],
}


@pytest.fixture
def client(tmp_path, monkeypatch):
    data_file = tmp_path / "customers.json"
    data_file.write_text(json.dumps({"customers": SAMPLE_CUSTOMERS}), encoding="utf-8")
    monkeypatch.setattr(main, "DATA_FILEPATH", str(data_file))
    main.app_data.customers = [Customer(**row) for row in SAMPLE_CUSTOMERS]
    return TestClient(main.app)


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World!"}


def test_read_customers(client):
    response = client.get("/customers/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert [c["name"] for c in data] == [
        "Leo Decaprio",
        "Maya Chen",
        "Andre Williams",
    ]


def test_find_customers_by_name_partial(client):
    response = client.get("/customers/", params={"name": "Maya"})
    assert response.status_code == 200
    assert [c["name"] for c in response.json()] == ["Maya Chen"]


def test_find_customers_by_name_case_insensitive(client):
    response = client.get("/customers/", params={"name": "leo"})
    assert response.status_code == 200
    assert [c["name"] for c in response.json()] == ["Leo Decaprio"]


def test_find_customers_by_name_url_encoded(client):
    response = client.get("/customers/", params={"name": "Maya Chen"})
    assert response.status_code == 200
    assert [c["name"] for c in response.json()] == ["Maya Chen"]


def test_find_customers_by_name_not_found(client):
    response = client.get("/customers/", params={"name": "nobody"})
    assert response.status_code == 200
    assert response.json() == []


def test_find_customer_by_email(client):
    response = client.get(
        "/customers/", params={"email": "maya.chen@outlook.com"}
    )
    assert response.status_code == 200
    assert [c["name"] for c in response.json()] == ["Maya Chen"]


def test_find_customer_by_email_blank_name_still_filters(client):
    response = client.get(
        "/customers/",
        params={"name": "", "email": "maya.chen@outlook.com"},
    )
    assert response.status_code == 200
    assert [c["name"] for c in response.json()] == ["Maya Chen"]


def test_find_customer_by_email_not_found(client):
    response = client.get(
        "/customers/", params={"email": "missing@example.com"}
    )
    assert response.status_code == 200
    assert response.json() == []


def test_find_customers_by_name_and_email(client):
    response = client.get(
        "/customers/",
        params={"name": "Maya", "email": "maya.chen@outlook.com"},
    )
    assert response.status_code == 200
    assert [c["name"] for c in response.json()] == ["Maya Chen"]


def test_find_customers_by_name_and_email_no_overlap(client):
    response = client.get(
        "/customers/",
        params={"name": "Maya", "email": "andre.williams@gmail.com"},
    )
    assert response.status_code == 200
    assert response.json() == []


def test_read_customer_by_id(client):
    customer_id = SAMPLE_CUSTOMERS[0]["id"]
    response = client.get(f"/customers/{customer_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Leo Decaprio"
    assert response.json()["id"] == customer_id


def test_read_customer_by_id_not_found(client):
    response = client.get("/customers/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"


def test_update_customer_partial(client, tmp_path):
    customer_id = SAMPLE_CUSTOMERS[0]["id"]
    response = client.put(f"/customers/{customer_id}", json={"city": "Santa Monica"})
    assert response.status_code == 200
    body = response.json()
    assert body["city"] == "Santa Monica"
    assert body["name"] == "Leo Decaprio"
    saved = json.loads((tmp_path / "customers.json").read_text(encoding="utf-8"))
    assert saved["customers"][0]["city"] == "Santa Monica"


def test_update_customer_not_found(client):
    response = client.put(
        "/customers/00000000-0000-0000-0000-000000000000",
        json={"city": "Nowhere"},
    )
    assert response.status_code == 404
    assert "was not found" in response.json()["detail"]


def test_update_customer_invalid_body(client):
    customer_id = SAMPLE_CUSTOMERS[0]["id"]
    response = client.put(
        f"/customers/{customer_id}",
        json={"hobbies": "not-a-list"},
    )
    assert response.status_code == 422


def test_create_customer(client, tmp_path):
    response = client.post("/customers/", json=NEW_CUSTOMER)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Riley Thompson"
    assert body["id"]
    names = [c.name for c in main.app_data.customers]
    assert "Riley Thompson" in names
    saved = json.loads((tmp_path / "customers.json").read_text(encoding="utf-8"))
    assert any(c["email"] == "riley.thompson@icloud.com" for c in saved["customers"])


def test_create_customer_missing_fields(client):
    response = client.post("/customers/", json={"name": "Only Name"})
    assert response.status_code == 422


def test_delete_customer(client, tmp_path):
    customer_id = SAMPLE_CUSTOMERS[1]["id"]
    response = client.delete(f"/customers/{customer_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Customer deleted"
    assert body["customer"]["name"] == "Maya Chen"
    assert all(c.id != customer_id for c in main.app_data.customers)
    saved = json.loads((tmp_path / "customers.json").read_text(encoding="utf-8"))
    assert all(c["id"] != customer_id for c in saved["customers"])


def test_delete_customer_not_found(client):
    response = client.delete("/customers/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert "was not found" in response.json()["detail"]
