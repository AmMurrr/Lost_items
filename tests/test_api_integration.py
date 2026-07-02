def _assert_search_result_shape(result: dict) -> None:
    assert set(result).issuperset({"id", "description", "station", "found_date", "similarity"})


def _assert_item_response_shape(item: dict) -> None:
    assert set(item).issuperset({"id", "description", "station", "found_date", "found_place", "image_path"})


def test_search_items(client, sample_item):
    response = client.post(
        "/search/",
        json={
            "description": sample_item["description"],
            "station": sample_item["station"],
            "loss_date": sample_item["found_date"].isoformat(),
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    body = response.json()
    assert isinstance(body, list)
    assert 1 <=len(body) <= 5
    for result in body:
        _assert_search_result_shape(result)


def test_get_existing_item(client, sample_item):
    response = client.get(f"/items/{sample_item['id']}")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    body = response.json()
    _assert_item_response_shape(body)
    assert body["id"] == sample_item["id"]
    assert body["description"]
    assert body["station"]
    assert body["found_date"]


def test_get_missing_item(client):
    response = client.get("/items/9999")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"detail": "Предмет не найден"}