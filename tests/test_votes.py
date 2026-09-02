def create_voter(client, name="Felipe Smith", email="felipe@example.com"):
    response = client.post(
        "/voters",
        json={
            "name": name,
            "email": email,
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def create_candidate(client, name="Andres Jones", party="Party A"):
    response = client.post(
        "/candidates",
        json={
            "name": name,
            "party": party,
        },
    )

    assert response.status_code == 201
    return response.json()["id"]


def test_create_vote(client):
    voter_id = create_voter(client)
    candidate_id = create_candidate(client)

    response = client.post(
        "/votes",
        json={
            "voter_id": voter_id,
            "candidate_id": candidate_id,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["voter_id"] == voter_id
    assert data["candidate_id"] == candidate_id


def test_vote_marks_voter_as_voted(client):
    voter_id = create_voter(client)
    candidate_id = create_candidate(client)

    response = client.post(
        "/votes",
        json={
            "voter_id": voter_id,
            "candidate_id": candidate_id,
        },
    )

    assert response.status_code == 201

    voter_response = client.get(f"/voters/{voter_id}")

    assert voter_response.status_code == 200
    assert voter_response.json()["has_voted"] is True


def test_vote_increments_candidate_votes(client):
    voter_id = create_voter(client)
    candidate_id = create_candidate(client)

    response = client.post(
        "/votes",
        json={
            "voter_id": voter_id,
            "candidate_id": candidate_id,
        },
    )

    assert response.status_code == 201

    candidate_response = client.get(f"/candidates/{candidate_id}")

    assert candidate_response.status_code == 200
    assert candidate_response.json()["votes"] == 1


def test_cannot_vote_twice(client):
    voter_id = create_voter(client)
    candidate_id = create_candidate(client)

    first_response = client.post(
        "/votes",
        json={
            "voter_id": voter_id,
            "candidate_id": candidate_id,
        },
    )

    second_response = client.post(
        "/votes",
        json={
            "voter_id": voter_id,
            "candidate_id": candidate_id,
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_nonexistent_voter(client):
    candidate_id = create_candidate(client)

    response = client.post(
        "/votes",
        json={
            "voter_id": 999,
            "candidate_id": candidate_id,
        },
    )

    assert response.status_code == 404


def test_nonexistent_candidate(client):
    voter_id = create_voter(client)

    response = client.post(
        "/votes",
        json={
            "voter_id": voter_id,
            "candidate_id": 999,
        },
    )

    assert response.status_code == 404


def test_failed_vote_does_not_mark_voter_as_voted(client):
    voter_id = create_voter(client)

    response = client.post(
        "/votes",
        json={
            "voter_id": voter_id,
            "candidate_id": 999,
        },
    )

    assert response.status_code == 404

    voter_response = client.get(f"/voters/{voter_id}")

    assert voter_response.status_code == 200
    assert voter_response.json()["has_voted"] is False


def test_failed_vote_does_not_increment_candidate_votes(client):
    voter_id = create_voter(client)
    candidate_id = create_candidate(client)

    response = client.post(
        "/votes",
        json={
            "voter_id": voter_id,
            "candidate_id": 999,
        },
    )

    assert response.status_code == 404

    candidate_response = client.get(f"/candidates/{candidate_id}")

    assert candidate_response.status_code == 200
    assert candidate_response.json()["votes"] == 0


def test_get_votes(client):
    voter_id = create_voter(client)
    candidate_id = create_candidate(client)

    vote_response = client.post(
        "/votes",
        json={
            "voter_id": voter_id,
            "candidate_id": candidate_id,
        },
    )

    assert vote_response.status_code == 201

    response = client.get("/votes")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["voter_id"] == voter_id
    assert data[0]["candidate_id"] == candidate_id


def test_statistics_with_no_votes(client):
    create_candidate(
        client,
        name="Felipe Smith",
        party="Party A",
    )

    create_candidate(
        client,
        name="Andres Jones",
        party="Party B",
    )

    response = client.get("/votes/statistics")

    assert response.status_code == 200

    data = response.json()

    assert data["total_votes"] == 0
    assert data["total_voters_voted"] == 0

    assert len(data["results"]) == 2

    for result in data["results"]:
        assert result["votes"] == 0
        assert result["percentage"] == 0


def test_statistics_with_multiple_votes(client):
    voter_1 = create_voter(
        client,
        name="Felipe Smith",
        email="felipe@example.com",
    )

    voter_2 = create_voter(
        client,
        name="Andres Jones",
        email="andres@example.com",
    )

    voter_3 = create_voter(
        client,
        name="Carlos Perez",
        email="carlos@example.com",
    )

    candidate_1 = create_candidate(
        client,
        name="Laura Gomez",
        party="Party A",
    )

    candidate_2 = create_candidate(
        client,
        name="Juan Rodriguez",
        party="Party B",
    )

    # Two votes for candidate 1
    for voter_id in [voter_1, voter_2]:
        response = client.post(
            "/votes",
            json={
                "voter_id": voter_id,
                "candidate_id": candidate_1,
            },
        )
        assert response.status_code == 201

    # One vote for candidate 2
    response = client.post(
        "/votes",
        json={
            "voter_id": voter_3,
            "candidate_id": candidate_2,
        },
    )

    assert response.status_code == 201

    response = client.get("/votes/statistics")

    assert response.status_code == 200

    data = response.json()

    assert data["total_votes"] == 3
    assert data["total_voters_voted"] == 3

    results = {
        result["candidate_id"]: result
        for result in data["results"]
    }

    assert results[candidate_1]["votes"] == 2
    assert results[candidate_1]["percentage"] == 66.67

    assert results[candidate_2]["votes"] == 1
    assert results[candidate_2]["percentage"] == 33.33