def test_create_voter(client):
    response = client.post(
        "/voters",
        json={
            "name": "Felipe Smith",
            "email": "felipe@example.com",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Felipe Smith"
    assert data["email"] == "felipe@example.com"
    assert data["has_voted"] is False


def test_create_voter_with_invalid_email(client):
    response = client.post(
        "/voters",
        json={
            "name": "Felipe Smith",
            "email": "not-an-email",
        },
    )

    assert response.status_code == 422


def test_create_voter_with_empty_name(client):
    response = client.post(
        "/voters",
        json={
            "name": "",
            "email": "felipe@example.com",
        },
    )

    assert response.status_code == 422


def test_create_voter_with_whitespace_name(client):
    response = client.post(
        "/voters",
        json={
            "name": "   ",
            "email": "felipe@example.com",
        },
    )

    assert response.status_code == 422


def test_create_duplicate_voter_email(client):
    voter = {
        "name": "Felipe Smith",
        "email": "felipe@example.com",
    }

    first_response = client.post("/voters", json=voter)
    second_response = client.post("/voters", json=voter)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_get_voters(client):
    client.post(
        "/voters",
        json={
            "name": "Felipe Smith",
            "email": "felipe@example.com",
        },
    )

    client.post(
        "/voters",
        json={
            "name": "Andres Jones",
            "email": "andres@example.com",
        },
    )

    response = client.get("/voters")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Felipe Smith"
    assert data[1]["name"] == "Andres Jones"


def test_get_voter(client):
    create_response = client.post(
        "/voters",
        json={
            "name": "Felipe Smith",
            "email": "felipe@example.com",
        },
    )

    voter_id = create_response.json()["id"]

    response = client.get(f"/voters/{voter_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == voter_id
    assert data["name"] == "Felipe Smith"


def test_get_nonexistent_voter(client):
    response = client.get("/voters/999")

    assert response.status_code == 404


def test_delete_voter(client):
    create_response = client.post(
        "/voters",
        json={
            "name": "Felipe Smith",
            "email": "felipe@example.com",
        },
    )

    voter_id = create_response.json()["id"]

    response = client.delete(f"/voters/{voter_id}")

    assert response.status_code == 204

    get_response = client.get(f"/voters/{voter_id}")

    assert get_response.status_code == 404


def test_delete_nonexistent_voter(client):
    response = client.delete("/voters/999")

    assert response.status_code == 404

def test_cannot_delete_voter_who_has_voted(client):
    voter_response = client.post(
        "/voters",
        json={
            "name": "Felipe",
            "email": "felipe@example.com",
        },
    )

    voter_id = voter_response.json()["id"]

    candidate_response = client.post(
        "/candidates",
        json={
            "name": "Andres Candidate",
            "party": "Example",
        },
    )

    candidate_id = candidate_response.json()["id"]

    vote_response = client.post(
        "/votes",
        json={
            "voter_id": voter_id,
            "candidate_id": candidate_id,
        },
    )

    assert vote_response.status_code == 201

    response = client.delete(f"/voters/{voter_id}")

    assert response.status_code == 409

def test_cannot_create_voter_who_matches_candidate(client):
    candidate_response = client.post(
        "/candidates",
        json={
            "name": "Andres Candidate",
            "party": "Example",
        },
    )

    assert candidate_response.status_code == 201

    response = client.post(
        "/voters",
        json={
            "name": "  andres candidate  ",
            "email": "bob@example.com",
        },
    )

    assert response.status_code == 409