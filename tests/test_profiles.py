from fastapi.testclient import TestClient
from app.main import app



client = TestClient(app)

def test_create_profile():
    response = client.post("/profiles/", json={
        "child_age": 10,
        "city": "Wonderland",
        "strengths": "Curiosity",
        "needs": "Explore",
        "notes": "Adventurous and kind"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["child_age"] == 10
    assert data["city"] == "Wonderland"


def test_get_profiles():
    response = client.get("/profiles/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_profile_by_id():
    post = client.post("/profiles/", json={
        "child_age": 12,
        "city": "Fantasy",
        "strengths": "Logic",
        "needs": "Learn",
        "notes": "Very curious"
    })
    assert post.status_code == 201
    new_id = post.json()["id"]

    get = client.get(f"/profiles/{new_id}")
    assert get.status_code == 200
    assert get.json()["child_age"] == 12
    

def test_delete_profile():
    post = client.post("/profiles/", json={
        "child_age": 9,
        "city": "Dreamland",
        "strengths": "Kindness",
        "needs": "Make friends",
        "notes": "Loves sharing"
    })
    assert post.status_code == 201
    new_id = post.json()["id"]

    delete = client.delete(f"/profiles/{new_id}")
    assert delete.status_code == 204

    get = client.get(f"/profiles/{new_id}")
    assert get.status_code == 404