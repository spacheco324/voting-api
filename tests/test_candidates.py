def test_create_candidate(client):
    response = client.post(
        "/candidates",
        json={
            "name": "Carlos Perez",
            "party": "Example Party",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Carlos Perez"
    assert data["party"] == "Example Party"
    assert data["votes"] == 0


def test_create_candidate_without_party(client):
    response = client.post(
        "/candidates",
        json={
            "name": "Laura Gomez",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Laura Gomez"
    assert data["party"] is None
    assert data["votes"] == 0


def test_create_duplicate_candidate(client):
    candidate = {
        "name": "Carlos Perez",
        "party": "Example Party",
    }

    first_response = client.post("/candidates", json=candidate)
    second_response = client.post("/candidates", json=candidate)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_create_candidate_with_empty_name(client):
    response = client.post(
        "/candidates",
        json={
            "name": "",
            "party": "Example Party",
        },
    )

    assert response.status_code == 422


def test_create_candidate_with_whitespace_name(client):
    response = client.post(
        "/candidates",
        json={
            "name": "   ",
            "party": "Example Party",
        },
    )

    assert response.status_code == 422


def test_create_candidate_matching_voter_case_insensitively(client):
    voter_response = client.post(
        "/voters",
        json={
            "name": "Felipe Smith",
            "email": "felipe@example.com",
        },
    )

    assert voter_response.status_code == 201

    response = client.post(
        "/candidates",
        json={
            "name": "  felipe smith  ",
            "party": "Example Party",
        },
    )

    assert response.status_code == 409


def test_get_candidates(client):
    client.post(
        "/candidates",
        json={
            "name": "Felipe Smith",
            "party": "Party A",
        },
    )

    client.post(
        "/candidates",
        json={
            "name": "Andres Jones",
            "party": "Party B",
        },
    )

    response = client.get("/candidates")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Felipe Smith"
    assert data[1]["name"] == "Andres Jones"


def test_get_candidate(client):
    create_response = client.post(
        "/candidates",
        json={
            "name": "Felipe Smith",
            "party": "Party A",
        },
    )

    candidate_id = create_response.json()["id"]

    response = client.get(f"/candidates/{candidate_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == candidate_id
    assert data["name"] == "Felipe Smith"


def test_get_nonexistent_candidate(client):
    response = client.get("/candidates/999")

    assert response.status_code == 404


def test_delete_candidate(client):
    create_response = client.post(
        "/candidates",
        json={
            "name": "Felipe Smith",
            "party": "Party A",
        },
    )

    candidate_id = create_response.json()["id"]

    response = client.delete(f"/candidates/{candidate_id}")

    assert response.status_code == 204

    get_response = client.get(f"/candidates/{candidate_id}")

    assert get_response.status_code == 404


def test_delete_nonexistent_candidate(client):
    response = client.delete("/candidates/999")

    assert response.status_code == 404


def test_cannot_delete_candidate_who_has_votes(client):
    voter_response = client.post(
        "/voters",
        json={
            "name": "Felipe Smith",
            "email": "felipe@example.com",
        },
    )

    assert voter_response.status_code == 201

    voter_id = voter_response.json()["id"]

    candidate_response = client.post(
        "/candidates",
        json={
            "name": "Andres Jones",
            "party": "Party A",
        },
    )

    assert candidate_response.status_code == 201

    candidate_id = candidate_response.json()["id"]

    vote_response = client.post(
        "/votes",
        json={
            "voter_id": voter_id,
            "candidate_id": candidate_id,
        },
    )

    assert vote_response.status_code == 201

    response = client.delete(f"/candidates/{candidate_id}")

    assert response.status_code == 409